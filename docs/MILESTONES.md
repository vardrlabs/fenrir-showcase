# FENRIR development milestones

Curated highlights from the private build log, results-and-dates level.
Source: private repo `docs/build_log.md` · compiled 2026-07-17.

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

**Next gate — hardware arrival (~2026-07-25):** actuator datasheet
verification, one-joint bring-up using the same wiggle procedure that runs
in CI, bench characterization.
