# Project FENRIR — Build Bible (public edition)

**Vardr Labs** · Public edition of internal Build Bible v2.2 · 2026-07-17

> ### What this document is, and where it comes from
>
> FENRIR is developed in a **private repository** (`vardrlabs/fenrir`). This repository,
> `vardrlabs/fenrir-showcase`, is its curated public face — and this file is the public
> edition of the Build Bible that the project is actually run from day to day, not a
> marketing summary written afterward.
>
> **Curated, not redacted.** The architecture, the engineering reasoning, the decisions
> and their trade-offs, the build order, the risks, and the verification evidence are
> all here. What is held back is the implementation that constitutes the platform's
> differentiators: wire protocol internals, the command grammar, control and firmware
> source, and the full machine configuration.
>
> **It does not stay that way.** The private repository opens at launch: the platform,
> the published attachment specification, and the SDK release under permissive licenses
> (Apache-2.0 planned for software, CERN-OHL-P planned for hardware). The privacy here
> is a runway, not a business model — the entire strategic bet is on being the open
> platform in this category.
>
> Updated by hand at milestones, in step with the internal document.

This is the plan: what FENRIR is, how it is architected, why each decision went the
way it did, and what order it gets built in.

Companion documents in this repository, which this one deliberately does not
duplicate: [ARCHITECTURE.md](ARCHITECTURE.md) for the block-level system view,
[BOM.md](BOM.md) for the complete bill of materials, [MILESTONES.md](MILESTONES.md)
for dated results, and the production kinematics module with its full test suite in
[`kinematics/`](../kinematics/), which runs in CI on every push to this repository.

---

## 0. The pitch

A small-to-mid quadruped whose legs are driven by quasi-direct-drive FOC actuators,
with an onboard autonomy brain: vision, natural-language command, gesture learning,
and eventually a sim-to-real reinforcement-learned locomotion policy. Built as a
**ladder** — every rung is a complete, demo-able robot, so the project is never a
half-finished thing waiting on the next milestone to be worth showing.

The robot is architected like a product, not a project. Every leg is a two-connector
module. Every actuator is a **self-announcing node**: plug a module in and it registers
itself, with no configuration, no manual registration, and no rebuild. Every capability
is a registered, hot-loadable Skill. Every state is observable live over one clean API,
which is what the future control app plugs into.

**The one-sentence version:** a quadruped you can take apart while it is running.

## 1. Capability tiers

Each tier is a shippable robot. The ladder exists so that funding, time, or interest
running out at any point still leaves something that works.

- **Tier 1 — "It walks":** model-based trot, teleoperation. Guaranteed finishable.
- **Tier 2 — "It sees and obeys":** plus vision, voice, follow-me. The realistic target.
- **Tier 3 — "It learned to walk":** plus an RL sim-to-real policy with shove recovery.
- **Tier 4 — "It thinks and learns":** plus task planning and the gesture-learning demo
  ("it watched me wave, and learned to wave").

## 2. System architecture — three layers, two buses

Three layers, each running an order of magnitude slower than the one below it, which
is the property that makes the system debuggable:

- **Layer 3 — Cognition.** Raspberry Pi 5 with a 40-TOPS AI accelerator. All AI runs
  on the robot: detection and tracking, pose and hand tracking, speech in, intent
  parsing, speech out, and on-demand scene description. Skill Registry, telemetry and
  command API, ROS 2.
- **Layer 2 — Real-time.** A Teensy 4.1 as bus master and safety supervisor: node
  discovery, the joint health registry, IMU fusion, joint command distribution, and
  the bay status LEDs driven straight from the registry.
- **Layer 1 — Actuation.** Twelve identical integrated smart actuators as nodes on
  two CAN buses split by body side. Each carries its own FOC driver and dual encoders
  and reports position, velocity, torque, temperature, bus voltage, and fault flags in
  every telemetry frame.

The FOC loops are distributed to the actuators rather than centralized, because a
single microcontroller running twelve of them at quality is a fiction. The Teensy's
job is coordination and safety, which it can actually do in hard real time.

Two buses rather than one, split left and right: it halves per-bus load and means a
bus fault costs one side of the robot, not the robot. Sustained bus utilization is
budgeted with headroom and enforced in CI, so no rate or node-count change can quietly
saturate it. Full block diagram: [ARCHITECTURE.md](ARCHITECTURE.md).

## 3. The hot-swap architecture — built first, on purpose

This is the differentiator, so it is the first thing built rather than the last thing
bolted on.

**Electrical.** Each leg module meets the body at exactly **two connectors**: XT30 for
power, a keyed 4-pin connector for the bus. A leg detaches with two plugs and four
bolts. Every leg rail is individually fused and current-monitored. The power
distribution board carries three requirements from its first revision, all cheap now
and painful to retrofit: headroom for the status LEDs, brownout ride-through sized
against motor-stall transients so that cognition cannot die mid-gait, and an always-on
trickle rail with a soft-latch that makes a future voice cold-boot possible at all.

**Protocol.** Frozen as v1 before any wire was cut, and append-only from that day:
message contracts are versioned, and fields are never renamed, renumbered, or
repurposed. No frame is transmitted that the specification does not define.

**Self-announcing, at three layers.** "Plug it in and it appears" is one property
delivered by three different mechanisms, and the system is designed so that no single
layer has to carry it alone. On the bus, a module is registered by two paths that back
each other up: unsolicited announcements are accepted where the actuator firmware emits
them, and active polling by the bus master is the guaranteed fallback that works
regardless of vendor behavior. On the link up to the cognition layer, health changes
are pushed the instant they happen rather than polled for. On the ROS graph, discovery
is announcement-based by construction. The shared health enum was written for all three
readings from the start: its `DISCOVERED` state means *announced on bus, or process
started, not yet configured*.

**The health registry.** The Teensy maintains the authoritative record of every
joint's health. A joint that stops reporting is degraded within one control tick and
the gait reconfigures or soft-stops around it. Longer silence returns the joint to
offline, and discovery resumes automatically — which is what makes replugging free. A
returning module walks the same lifecycle as a booting one: rediscovery, firmware
check, absolute-position sanity check, then back into the gait. Recovery time is a
tracked metric.

**One health vocabulary.** Every component in the stack, from actuator firmware to UI
status pill, speaks exactly one seven-state machine:

```
OFFLINE → DISCOVERED → CALIBRATING → READY → ACTIVE → DEGRADED → FAULT
```

Ad-hoc status strings and `is_ok` booleans are forbidden anywhere in the codebase.
The enum header is published here: [`common/component_state.h`](../common/component_state.h).

**Bay status LEDs.** Each bay carries an addressable segment driven directly by the
Teensy from the registry, with no dependency on the Pi or any network. The hot-swap
demo therefore narrates itself in light: pull a leg and the bay goes red, plug it back
and it pulses amber through calibration, then settles green. LED output on the
real-time layer is DMA-driven as a hard rule, because an interrupt-blocking LED
library would stall the control loop — which is the kind of thing that is obvious in
hindsight and expensive in practice.

## 4. Actuators — the decision that changed

The original plan was twelve hand-built actuators: bare motor, discrete driver,
encoder, printed cycloidal reduction. It is the cheapest path and the least modular
one. Four hand-assembled components and a harness per joint kills hot-swap in
practice, which is the entire point of the robot.

The fleet is therefore **integrated smart actuators**: 5 N·m rated and 11 N·m peak,
388 g, 80 mm diameter, 8:1 planetary reduction, a 14-bit driver encoder plus an
output-shaft encoder, CAN, and a USB-C configuration port. All twelve units identical.
The encoder figure is read off the hardware — `cpr = 16384`, which is 2¹⁴ exactly. The
vendor's product listing and an older manual revision both claimed 16-bit; the newer
manual revision and the encoder's part number were right.
The output-shaft encoder is what earns its place: it reports absolute joint position
on power-up, so a swapped module needs no recalibration.

**Ordering rule:** buy one leg's worth plus a spare, validate the complete leg on
hardware — bring-up, thermals, hot-swap recovery, torque tracking — and only then
order the remaining eight. A bought, specified actuator carries integration risk
rather than design risk, and one complete leg exposes integration risk far better than
one perfect hand-built motor does. A DIY bench actuator is still built and
characterized in parallel, as a learning and firmware rig.

Per-item detail, quantities, prices, and status: [BOM.md](BOM.md).

## 5. The local-model stack

Ground rule, and it is absolute: **no LLM in any control loop, ever.** Language models
parse intent and bind names to skills. Deterministic code and small vision networks
act. A model's output never becomes a joint target, a torque, or a velocity.

Everything runs locally on the robot — a privacy and latency story that a
cloud-dependent product cannot tell. Detection and tracking, pose and hand tracking,
speech recognition, a small function-calling model for intent parsing, speech
synthesis, and a compact vision-language model for on-demand scene description. The
detector is deliberately swappable behind its driver node, which matters because the
best-performing option and the best-licensed option are not currently the same model.

The command grammar is designed, approved, and frozen: 25 canonical verbs, one
envelope, three reply shapes, append-only. Safety-critical stop commands additionally
have a deterministic non-model recognition path, so stopping the robot never depends
on inference succeeding — and the physical emergency stop outranks all of it. One
vocabulary serves three consumers: voice, UI, and scripts.

## 6. The Skill Registry

Every motion the robot can perform — hand-authored gait, retargeted gesture, learned
policy — is a **Skill**: a uniform object with a name, a version, a source, explicit
preconditions, a trajectory or policy handle, and blend rules.

**Every skill passes the same four-gate validation in simulation before it is allowed
near hardware.** No exceptions and no demo-day bypass:

1. Stability margin and joint/torque limits across the entire trajectory.
2. Jacobian determinant above a floor along the whole path — the singularity check.
3. Motor-operating-region containment: every joint's torque-velocity trajectory stays
   inside the actuator envelope with margin.
4. Sustained-torque budget: per-joint RMS torque under a thermal cap even when peaks
   are legal. Peaks are allowed. Sustained overload is not.

Gates 3 and 4 were adopted from the KAIST HOUND lineage and paid for themselves the
day they were implemented, catching a knee thermal exceedance and touchdown torque
spikes that no existing test could see — before the remaining actuators were bought.

## 7. Gesture learning

Not "the language model figures out motor commands." The pipeline is deterministic
and debuggable end to end: observe the human with pose tracking, retarget the keypoint
trajectory onto robot kinematics through inverse kinematics that respects joint and
torque limits, validate the candidate through the four-gate gauntlet above, register
it as a versioned skill, and let the language model bind a name to it. On-device
policy *training* is out of scope permanently; learning happens in simulation.

## 8. Telemetry and command API

Decide the seam now, build the app later. The robot exposes one streaming endpoint:
joint states at display rate with delta encoding and client-side interpolation,
component health in the seven-state vocabulary, logs, and parameter get/set against a
whitelisted registry. Development uses an off-the-shelf robotics dashboard, which
teaches what a custom UI needs before a line of it is written. The eventual product UI
is a pure client of an API that already exists.

## 9. Build plan

- **Phase 0 — Foundations.** *Substantially complete.* Long-lead hardware ordered;
  leg kinematics derived, implemented, and verified at machine precision; wire
  protocol and command grammar frozen; simulation matching the analytic solution and
  walking two gaits. Outstanding: leg CAD around the actuator STEP files, and the
  bench actuator characterization.
- **Phase 1 — The bus and one leg.** Firmware skeleton complete with a hardware-free
  test suite. Hardware-gated remainder: verify the vendor protocol against real units,
  bring up one joint, then one leg tracking trajectories. **Milestone demo: unplug a
  joint mid-motion, watch it degrade and soft-stop, plug it back, watch it recover.**
- **Phase 2 — Full body, static walk.** Four modules, body, power distribution, IMU.
  Model-based trot and teleoperation. Telemetry API live. Includes a 30-minute
  continuous endurance walk with full telemetry logged, because long duration is where
  thermal models, connectors, and firmware leaks are found.
- **Phase 3 — Perception and voice.** Follow-me, voice command end to end, spoken
  replies, on-demand scene questions.
- **Phase 4 — RL sim-to-real.** Training in simulation on rented GPU time, domain
  randomization, deployment for on-robot inference. Shove test.
- **Phase 4.5 — Gesture learning.** One gesture end to end is the milestone; further
  gestures are free after that.
- **Phase 5 — Industrial design and launch.** Finished panels, cable spine,
  connectorized harnesses, paint. Filmed and published.

**Minimum viable awesome:** Phase 2 plus the hot-swap demo plus voice stop. A walking
robot whose leg you can pull out live, and which recovers, is already a serious demo.

## 10. Positioning

The lane is the **open, modular, hot-swappable quadruped where the SDK is the product
and FENRIR is the reference hardware** — the Framework laptop of quadrupeds. The
incumbents build excellent closed machines; competing with them on manufacturing scale
would be foolish, and competing on openness is a lane they have chosen not to enter.

Four stacked differentiators: hot-swap modules with a *published* attachment
specification so third parties can build payloads; an SDK that exposes everything,
including per-joint gains, gait parameters, skill scripting, and full telemetry;
local-first AI; and interface polish in a field where robot software is famously ugly.

The discipline that follows from this, starting now rather than at launch: version the
API from the beginning, write documentation as though an external developer already
exists, and keep the verification culture strong enough that an outsider can trust the
platform without taking anyone's word for it.

## 11. Risk register

| Risk | Mitigation |
|---|---|
| RL consumes all available time | Model-based gait guarantees Tier 1; RL is upside, never the critical path |
| Actuator lead times | Ordered early, staged; bench prototyping continues meanwhile |
| Protocol churn after wiring starts | Schema frozen on paper first, every message versioned, contracts append-only, drift caught by CI |
| Vendor frame layout differs from expectation | The entire vendor surface is quarantined behind one adapter; a surprise changes that file and one spec section, nothing else |
| Sustained thermal overload at the knees | Operating-region and RMS-torque budgets enforced in CI on every gait; thermals watched from the first hardware run |
| Power brownout kills cognition mid-gait | Capacitance and regulation sized for stall transients in the first board revision; the host-watchdog fallback is already implemented and tested |
| Compute thermal throttling under inference | Active cooling, temperatures in telemetry from day one |
| Temptation to put a language model in the loop | Hard architectural rule, enforced in review: models orchestrate, never actuate |
| Scope creep, especially the UI | The UI is an API seam until the final phase; an off-the-shelf dashboard until then |
| "Works but ugly" | The industrial design phase is non-negotiable; panels designed with the structure, not around it |

**Definition of done, every phase:** works, wired cleanly, looks intentional,
documented.

## 12. Metrics

Captured as they occur rather than reconstructed later: actuator torque, bandwidth and
thermals; leg-tip RMSE; walking speed and cost of transport; recovery success rate;
vision throughput and accuracy; command-to-action latency; hot-swap recovery time;
heartbeat-loss to soft-stop latency; intent-parse accuracy; and gesture retargeting
error.

Four of these are now measured automatically on every simulated gait rollout, which
makes them comparable against hardware telemetry later: cost of transport, per-joint
peak and RMS torque, motor-operating-region containment, and foot touchdown velocity.
Current simulated baseline: trot cost of transport 0.40 with worst-joint RMS torque
3.92 N·m against a 4.0 N·m sustained cap and zero envelope violations; crawl 1.76 with
worst-joint RMS 3.54 N·m, also clean. See the per-joint operating-region plots in
[media/](media/).

## 13. Where the project stands

Verified and done: leg kinematics at machine precision, simulation agreeing with the
mathematics to sub-micron, wire protocol and command grammar frozen, firmware skeleton
with a hardware-free test suite, a full repository audit passed, two gaits walking in
simulation under per-leg liveness assertions, and motor-envelope validation running in
CI on every change.

Outstanding before the robot stands up: leg CAD around the actuator geometry, bench
actuator characterization, and — gated on hardware arrival — vendor protocol
verification and one-joint bring-up.

Dated detail: [MILESTONES.md](MILESTONES.md).

---

*Build the one you'd be proud to sign. Then sign it, and make the status lights green.*

*Curated from the internal Build Bible v2.2 at milestones. The platform, its
attachment specification, and the SDK release openly at launch.*
