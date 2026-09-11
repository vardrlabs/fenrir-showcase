# FENRIR development milestones

Curated highlights from the private build log, results-and-dates level.
Source: private repo `docs/build_log.md` · compiled 2026-07-17, extended 2026-09-06.

**2026-07-12 — Architecture v2 frozen; leg kinematics derived and verified.**
Closed-form IK/FK/analytic Jacobian for the 3-DOF leg, with a verification
suite that is now the project's template: 10,000 FK→IK→FK round trips at
~3×10⁻¹⁶ m (machine precision), analytic Jacobian vs central finite
differences at 7×10⁻¹¹, closed-form determinant verified to 1×10⁻¹⁷, standing
statics against hand calculation. First actuator batch ordered the same day.

**2026-07-12 — Simulation agrees with the math.** MuJoCo leg model generated
from the robot's single source-of-truth config at load time; simulated foot
position matches the analytic kinematics to 2.2×10⁻¹⁶ m (acceptance bound
1×10⁻⁶ m) across 2,008 sampled configurations per leg, all four legs.

**2026-07-12 — Voice command grammar v1 approved.** 25-verb command schema
frozen (append-only from day one), with a validated 485-example training seed
and a CI validator that fails the build if schema and data ever drift.

**2026-07-12 — CAN protocol v1 frozen before any wire is touched.** Dual-bus
topology with schema-versioned, append-only message contracts; worst-case bus
utilization budgeted and enforced by CI (a rate or node-count change that
blows the budget fails the build).

**2026-07-13 — Full repository audit: 63 PASS / 1 FAIL / 5 deviations, zero
blockers.** Independent re-verification from a cold clone: all suites green,
the Jacobian and its determinant re-derived symbolically in CI-quality
tooling, statics reproduced from first principles. The one FAIL was a stale
organization name in a checklist. All findings dispositioned and closed.

**2026-07-13 — Busmaster firmware skeleton.** Teensy 4.1 CAN-master firmware
structured as testable modules: 16 hardware-free native test cases green
(framing round-trips with corruption recovery, health state machine legality,
discovery lifecycle including hot-swap replug, safety supervisor timing), and
the embedded target compiles in CI. Vendor-specific frame handling is
quarantined behind one adapter, marked verify-on-arrival.

**2026-07-14 — Full quadruped walks in simulation.** Assembled-robot world
kinematics verified at 4.7×10⁻¹⁶ m against the composed analytic solution;
open-loop crawl and trot on flat ground with color-coded legs, dual-camera
renders, and a CI job that fails unless the robot demonstrably walks on video.

**2026-07-15 — Per-leg liveness in CI.** A wiggle test (command one leg,
assert exactly that foot moves) that doubles as the hardware bring-up
procedure, plus per-leg swing assertions: a foot that drags instead of
stepping now fails the build. Used the same day to find and fix a gait bug
that aggregate metrics could not see.

**2026-07-16 — Motor-envelope validation catches two overload conditions
before the remaining actuators were purchased.** Adopted from the KAIST HOUND
lineage (ICRA 2022): every simulated rollout now checks torque-velocity
containment in the actuator operating region, sustained-torque thermal
budget, and cost of transport. First run flagged a knee thermal-budget
exceedance in trot and touchdown torque spikes in crawl; smooth quintic swing
trajectories with near-zero touchdown velocity fixed both. Trot covers
150 cm in 10 s in simulation; crawl velocity smoothness improved 42% the
same week.

**2026-08-11 — first hardware contact.** Four actuators received; one powered
and read over USB in a read-only session. The motor never moved and nothing
was written to the device. Settled the encoder resolution question at 14-bit
and found two shipped defaults that contradict the vendor manuals; the shipped
firmware turns out to be a vendor fork whose version number does not mean what
it appears to. See [first contact](bringup/2026-08-11-first-contact.md).

**2026-08-18 — hot-swap position recovery verified.** The output-shaft
encoder recovers absolute joint position across a power cycle *including
movement that happened while the unit was unpowered* — the property
recalibration-free module swapping depends on. Tested with a design that could
distinguish real sensing from a value merely remembered in flash: four readings
plus a reversal, with two independently measured quantities agreeing to four
decimal places. Also established the limit: recovery holds within one output
revolution. See [position recovery](bringup/2026-08-18-hot-swap-position-verified.md).

**2026-09-03 — the fleet leaves its factory state.** First writes ever made to
this hardware: all four actuators configured, every value saved to flash,
power-cycled and read back to confirm it survived. Vendor factory calibration
came through the write intact on all four. Position recovery survived a
configuration write, save and reboot to 0.110° at the output, under half the
gearbox backlash. The same session confirmed the bad half: a joint turned
through a full output revolution while disconnected returns wrong by exactly
one revolution and **raises no error**, so the remedy is mechanical hard stops.
It also corrected our own earlier reasoning — arithmetic we had treated as
settling where the recovery window sits turned out to fix only its width. See
[first configuration](bringup/2026-09-03-first-configuration.md).

**2026-09-04 — the first CAN bus.** Two actuators on one bus, **348,000 frames,
zero errors**, receive-and-acknowledge only with nothing commanded. The 5 ms
telemetry rate configured the day before was confirmed *on the wire* at
4.999 ms mean — register value and emitted rate agree. The factory default of
100 ms was twice our own 50 ms fault threshold, so a missed beat and a dead node
would have been indistinguishable on an unmodified unit. The same session found
the first silent fault: a telemetry message that arrives on time, correctly
formed, with no error flag, carrying values that are not true. See
[the first bus, and a message that lies](bringup/2026-09-07-first-bus-and-a-lie.md).

**2026-09-07 — the fault localised, and the recovery window bracketed.** The
lying message was narrowed to one specific telemetry frame; every other message
from the same node at the same instant is correct. Park-and-restore cycles
established that position recovery is exact — residuals inside the encoder's own
resolution — and bracketed the edge of the recovery window to a 23.5° span. The
best position hold recorded in the project comes from this work: **0.0070° at the
output across three days and a power-down.**

**2026-09-10 — a workaround, a second fault, and a register with nothing behind
it.** A way around the lying message, accurate to better than one encoder count,
using a different endpoint on the same device. A second fault of the same silent
kind. And a health register the design had assumed existed turns out not to —
there is no bus-health signal on this actuator at all. Also the uncomfortable
part: the check that caught all of this had already caught it weeks earlier, on
screen, and nobody was watching. The instrument now says so loudly. See
[two lies and a workaround](bringup/2026-09-10-two-lies-and-a-workaround.md).

**2026-09-11 — the checks became a program.** The validation idea behind hot
swap — decide whether to trust a module by cross-examining its own reports —
now runs offline against every capture taken so far: **1,830 checks across four
sessions of recorded data, catching two of the three known faults, with no false
alarms in 1,337 checks against healthy data.** The third fault is not detectable
at this stage and the results say so rather than rounding up. Every recorded
capture in the repository is now a regression test.

**Next gate — first motion under power:** measure the noise floor the validation
thresholds should be derived from, settle where the recovery window actually
sits (it gates leg geometry), wire the emergency stop into the DC main, then
one-joint bring-up using the same wiggle procedure that runs in CI, and bench
characterization.
