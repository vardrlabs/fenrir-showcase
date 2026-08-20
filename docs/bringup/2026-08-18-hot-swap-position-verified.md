# Hot-swap position recovery, verified

2026-08-18 · One GIM6010-8 on the bench, read-only. No writes, no motion under power.

[Last time](2026-08-11-first-contact.md) we read the device's parameter tree and left the one
question a parameter tree cannot answer: **does a joint recover its absolute output-shaft
position after a power cycle?** That is the property that makes a module swappable without
recalibration. This is that test.

## The claim, and an admission

FENRIR's material has said, in more than one place, that the actuator's secondary
output-shaft encoder reports absolute joint position on power-up, so a swapped module needs
no recalibration.

**That was published before it was verified.** It came from the vendor's description of the
part, it was plausible, and it was load-bearing for the whole modular design — exactly the
combination that should have made it a measurement first and a claim second. It was tracked
internally as unverified, which is better than not tracking it, but it was still out in
public with nothing behind it but a datasheet. It turns out to be true. That is luck as much
as judgement, and the order was still wrong.

## Why the obvious test would have proved nothing

Two completely different mechanisms produce identical results in a naive test:

1. **The secondary encoder senses the output shaft at boot** — the driver looks at where the
   joint physically is, which works no matter what happened while it was disconnected.
2. **The driver writes position to flash on shutdown and reads it back on boot** — the
   position is remembered, not sensed.

Power a unit down and back up without touching it and both return the same number. You would
conclude the encoder works. But mechanism 2 is **useless for hot-swap**: a leg that is
detached, carried across a bench and reattached has moved, and a remembered position is then
a confidently wrong one.

**The discriminator is to move the shaft while the unit is dead.** Flash persistence reports
the stale value, real sensing reports the true one, and there is no way for the two to agree.
The rotation was also chosen at roughly a quarter turn of the output — two full rotor
revolutions through the 8:1 gearbox, which the rotor's single-turn encoder cannot tell from
zero. The answer had to come from somewhere other than the motor encoder.

## Four readings

| | Position estimate (rotor turns) | What it should show |
|---|---|---|
| **A** baseline | 3.0337727 | starting point |
| **B** power cycle, untouched | 3.0338063 | unchanged, if a power cycle alone loses nothing |
| **C** power cycle, shaft moved while dead | −3.2758303 | **changed**, if the shaft is genuinely sensed |
| **D** moved back to the mark | 3.0234385 | back near A, if the result is repeatable |

**The control matters as much as the result.** Between A and B the unit was power-cycled and
nothing was touched: the reading moved by 0.0000336 turns, about half a count out of 16384 —
noise. Meanwhile the driver's incremental counters reset to near zero, which tells us they
are *not* what holds the position. Something else survives.

**Reading C settles it.** If position were restored from flash, C would have read 3.0338, the
value in memory at shutdown. It read −3.2758. The shaft moved while the driver had no power
at all, and the driver knew.

## The part that makes it convincing

A single changed number could be a lot of things. What makes this conclusive is that **two
independently measured quantities agree.** The position estimate decomposes cleanly into a
whole-turn count plus the rotor's own fractional position within its current turn — separate
measurements from separate sensors — so the fine position can be predicted from the coarse
displacement, and checked.

Working the displacement from A to C gives 1.6903970 rotor turns, predicting a rotor fraction
of **0.7240677**. Measured: **0.7242317** — agreement to within 0.00016 turns, under three
counts out of 16384. The same check on the way back: displacement C to D gives −1.7007312
turns, predicting **0.0235005**, measured **0.0234041**. Agreement to 0.0001 turns, a second
time, in the opposite direction.

Through the gearbox the shaft went out 76.07° and came back 76.54°, returning to within
**0.46° at the output** — by hand, against a tape mark. The instrument's own self-consistency
is around 0.002° at the rotor, so **the half-degree is the human hand, not the sensor.**

## The constraint, which is the part worth reading

The whole-turn count does not run forever. **It wraps after exactly 8 rotor turns — one full
output revolution** — and the observed values place that window at roughly **±180° at the
output**.

The width of one revolution is proven by both transitions; the exact placement of the bounds
is inferred from where the readings fell, and confirming it is a separate test not yet run.

**Inside that window, recovery is exact. Outside it, a joint comes back believing it is one
full output revolution from where it actually is — and nothing raises an error.** It is not a
fault condition; it is a wrong answer delivered with the same confidence as a right one.

For a robot whose entire premise is detaching a limb and putting it back, that is a real
constraint, not a footnote. It also has a mechanical answer: hard stops that keep a joint
inside the window make exceeding it structurally impossible. That is now an input to the bay
design rather than something to discover later.

## What this does and does not establish

**Does:** the joint recovers absolute output-shaft position across a power cycle — including
movement while unpowered, repeatably, in both directions, within one output revolution.
Recalibration-free module swapping works the way the architecture assumed, and bay design can
proceed on the encoder question.

**Does not:** anything about motion. **Nothing has moved under power.** No gait has run on
hardware, no CAN bus has been exercised, no current limits changed. This verified a sensing
property, not a working hot-swap demonstration — that needs a robot, and there isn't one yet.
Rotating past 180° to pin down the bounds was skipped deliberately: it is its own test.

## The transferable part

If you are relying on an absolute encoder to survive a power cycle, **test it with the shaft
moved while the device is off.** A test that leaves the shaft still passes whether position
is sensed or merely remembered, and only one of those is worth anything to you. It costs one
extra reading.

---

*Part of [Project FENRIR](../../README.md) — an open, modular, hot-swappable quadruped.
Findings here come from the private development repository's bench logs and are published as
the build progresses.*
