# The first bus, and a message that lies

2026-09-04 and 2026-09-07 · Two actuators, a microcontroller, and the first CAN bus this
project has ever run. Nothing moved under power.

Two sessions. The first brought a bus up and left it running for fourteen minutes. The second
worked out what was wrong with what came down it, and finished a piece of arithmetic we had
got wrong three weeks earlier.

## The bus works

**348,000 frames. Zero errors.**

The actuators talk on a shared two-wire bus, and until this week nothing had ever listened to
one. The listener is deliberately dumb: it receives, it acknowledges — which the protocol
requires and cannot be avoided — and it transmits nothing. Nothing was commanded. The motor
was never armed.

It ran for 870 seconds. Every frame arrived. The message counter that increments once per
message did so **174,090 times without a single break**, which is the cleanest statement
available that nothing was dropped. And the telemetry arrived at exactly the rate the
configuration claimed it would — measured on the wire, not read back from a register. Those
are different claims, and until this week we had only made the second one.

For a first bus, on wiring built the same afternoon, that is a better result than we expected.

## And then the interesting part

**One of the telemetry messages is not telling the truth.**

It arrives exactly on time. It is the right size. It carries no error flag, and every error
register on the device reads clean. And the position it reports is **zero**, on every one of
174,091 frames, while the same actuator over a second, independent connection reports its true
position at the same moment.

Not a dropout. Not a corrupted frame. Not a device that has fallen over. A message that shows
up punctually, correctly formed, claiming everything is fine, carrying a number that is simply
invented.

### Why we can be certain

The obvious suspicion is that the device just isn't producing that data while idle — that the
motor is disarmed and the number is meaningless rather than wrong.

The second session ruled that out by turning on **two more telemetry messages from the same
device**. One reports raw encoder counts; the other reports supply voltage. Both were captured
in the same recording, in the same second, from the same actuator.

**Both match the second connection exactly.** Encoder counts agree. Voltage agrees to three
decimal places. The third message, sitting between them in the same capture, reads zero.

So it is not the device, not the wiring, not the bus, and not our decoder. **It is one
message.** We then checked a second actuator and got the identical signature, which rules out
a single bad unit.

### Why this matters beyond one actuator

A device that fails loudly is an easy problem. It stops answering, or it answers with an
error, and anything watching it notices immediately.

**A device that answers confidently and wrongly is the hard case**, and it defeats the obvious
defence. Every check of the form *"did the endpoint respond?"* returns yes. Ours would have.
The module would have been admitted as fully working, and a safety check that compares where a
leg thinks it is against where it should be would have been fed an invented zero.

The fix is not to ask harder whether something responded. It is to **ask two independent
sources the same question and check that they agree**. In this case two of the messages
describe the same physical angle by different routes; one says 0.1218 of a turn and the other
says nothing at all. That check needs no external reference, and it points at the specific
message that is wrong rather than just raising a general alarm.

We only caught this because a diagnostic cable happened to be plugged in at the time. A robot
walking across a floor does not have that. So the check has to work without it — which is why
cross-checking two of the robot's own messages against each other, rather than against some
external truth, is the version that survives contact with reality.

## The correction to our own reasoning

[An earlier note](2026-08-18-hot-swap-position-verified.md) recorded that a joint recovers its
absolute position after a power cycle, and that this only holds within one full revolution of
the output. Beyond that boundary the joint comes back wrong by exactly one revolution and says
nothing about it.

At the time we treated **where that boundary sits** as already settled — a piece of arithmetic
from the original test appeared to fix it. Re-reading it while writing that note showed it does
not. The two numbers in question turn out to be **two different names for the same physical
shaft position**, 360° apart in how the driver represents it. That identity fixes the *width*
of the window. It says nothing whatever about its *placement*.

This session went and measured it. Three power cycles, each parking the shaft at a chosen
angle with the unit dead and reading back where it thought it was on wake:

- The wrap is a **clean, exact subtraction of one output revolution** — agreeing to within a
  fraction of one encoder count, twice.
- The upper edge lies somewhere in a **23.5° window**, and **that window contains 180°**.

So the original assumption survives. It is now bracketed rather than guessed, and one more
cycle would pin it exactly. **Owning the correction is the point** — the arithmetic was ours,
the overreach was ours, and nobody outside would ever have found it.

## Two numbers worth publishing

**Position recovery reproduces to better than 0.0025° at the output** — under a single encoder
count. That figure comes from a cycle where the shaft was parked, the unit powered down, and
the position read back on wake with no hand touching it in between. Earlier figures for this
were four to seven times looser because they were limited by how precisely a person can return
a shaft to a mark, not by the sensor.

**One actuator held to 0.0147° across four days**, a power-down, being carried around a bench
and being remounted. That is roughly a sixtieth of the mechanical backlash in the gearbox it
drives through.

## What has not happened

**Nothing has moved under power.** No motor has been armed, no motion commanded, no joint
driven. **No gait has run on hardware.** **There is no leg** — these are individual actuators
clamped to a bench.

What exists is a working bus, two actuators that talk on it, and a much better map of which of
the things they say can be believed.

---

*Part of [Project FENRIR](../../README.md) — an open, modular, hot-swappable quadruped.
Findings here come from the private development repository's bench logs and are published as
the build progresses.*
