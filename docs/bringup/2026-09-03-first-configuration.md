# First configuration: the fleet leaves its factory state

2026-09-03 · All four GIM6010-8 actuators · **The first writes we have ever made to this
hardware.** Nothing moved under power.

Every session before this one was read-only — connect, read the parameter tree, disconnect,
change nothing. This one wrote. Each actuator now has a unique address on the bus it will
eventually join, a current limit set well below what the bench supply can deliver, and
telemetry configured for the rate the design needs rather than the rate it shipped with.
Every value was written, saved to flash, power-cycled and read back to confirm it survived.

Two things came out of the day. One is a clean result. The other is a correction to our own
reasoning, and it is the more useful of the two.

## The encoder finding, which is bad news

[Last time](2026-08-18-hot-swap-position-verified.md) we established that a joint recovers its
absolute output-shaft position after a power cycle, including movement that happened while it
was unpowered — the property that makes a leg swappable without recalibration. That note also
recorded a limit: the recovery only holds within **one output revolution**.

This session tested what happens past that limit. One actuator, clamped, tape mark on the
output flange, powered down, shaft turned by hand through **one complete revolution**, powered
back up.

**It came back reporting the position it had before the rotation.**

Not approximately. The recovered position was wrong by exactly one output revolution, and it
was reported with the same confidence and precision as a correct reading. Every error register
read zero — no fault, no warning, nothing to catch in software. The joint simply believed it
was somewhere it was not.

That is the failure mode you least want, because there is no signal to act on. A joint that
knows it is confused can ask for help. This one cannot tell.

**The remedy is mechanical, not software.** Hard stops that keep a joint's travel inside one
output revolution make the condition physically unreachable. That is now an input to the leg
and bay design rather than something to discover during assembly.

### Why one turn, instead of measuring an angle

The earlier plan was to rotate past a specific angle and find the boundary. That test was
replaced by a simpler one, because **one complete turn of a shaft — mark leaving the reference
and returning to it — is far more repeatable by hand than any measured angle.** It also tests
the thing that actually matters: a leg unplugged, carried across a bench, and reattached.

## The correction to our own reasoning

Our earlier reading treated the *placement* of that one-revolution window as already settled by
arithmetic left over from the previous session. Re-reading it while writing this one showed
that it is not.

The arithmetic in question relates two numbers that are **two different names for the same
physical shaft position**, 360° apart in how the driver represents it. That identity fixes the
**width** of the recovery window — exactly one output revolution — and says nothing whatever
about **where that window sits**. A whole family of placements fits the same data equally well.
The symmetric answer is the natural guess. It remains a guess.

This matters more than it sounds, and not for the reason you would expect. Within one
revolution the reported position is never ambiguous, so the boundary is not a source of
confusion about where the joint is. It is a **numerical discontinuity**: a joint whose travel
straddles it reports +150°, +170°, then −175°, −155° across one smooth physical sweep. Any
limit check, any interpolation, any arithmetic that assumes position increases smoothly will
break — and it will break in the *middle* of the travel range rather than at an edge, where
nobody thinks to look.

The fix is again assembly rather than code: orient the actuator relative to the link so the
boundary falls outside the joint's reachable travel. Doing that requires knowing where the
boundary actually is, and on which units. We do not yet, and that test is scheduled.

**Owning this is the point.** We stated something as established that our own arithmetic never
established. Nobody else would have caught it, which is exactly why it is written down here.

## Two numbers worth publishing

**Position recovery survived being reconfigured.** Between the encoder test and the end of the
session, one unit went through a parameter write, a flash save, a forced reboot, a software
restart and a good deal of physical handling. Its output-shaft position moved **0.110°** — less
than half the gearbox's own backlash figure. Whatever we do to the firmware configuration, the
position knowledge underneath it holds.

**The vendor's factory calibration survived the flash write.** Each of these actuators ships
with per-unit motor and encoder calibration constants measured at the factory, and the driver
computes its current-loop gains directly from them. After the first flash write these units
have ever received, all of those constants matched their pre-write values exactly, on all four
units, with the gain relationship still holding to the last decimal. That was not guaranteed,
and it is worth knowing before anyone writes an automated configuration routine.

## What has not happened

**Nothing has moved under power.** Nothing was commanded, nothing was armed, no motion of any
kind. **No CAN bus exists yet** — no transceiver has been connected, and the addresses written
today are untested on a real bus. **No gait has run on hardware.** No calibration was re-run,
because these units ship calibrated and re-running it spins the shaft.

The walking in this repository's videos is still simulation. What changed today is that the
hardware is no longer in the state the factory shipped it in, and we have written down exactly
what it is in instead.

---

*Part of [Project FENRIR](../../README.md) — an open, modular, hot-swappable quadruped.
Findings here come from the private development repository's bench logs and are published as
the build progresses.*
