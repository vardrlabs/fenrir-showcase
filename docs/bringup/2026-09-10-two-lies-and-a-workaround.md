# Two lies and a workaround

2026-09-10 · Two actuators on the bench. Nothing moved under power.

[Last time](2026-09-07-first-bus-and-a-lie.md) we brought up a bus, ran it for fourteen minutes
without an error, and found that one of the telemetry messages was reporting a position of zero
while the actuator's true position was something else entirely.

This session went looking for a way around that. It found one. It also found a second fault of
the same kind, and a third thing that is arguably worse than either.

## The workaround: ask directly instead of listening

The failing message is one the device broadcasts on a timer. Nobody asked for it; it simply
arrives, two hundred times a second, carrying zeros.

But the same quantity can also be **requested directly** — a question sent to the device and an
answer sent back, rather than an unprompted broadcast. So we asked.

**The answer was correct to better than one encoder count.** The device returned a position
matching a second, independent measurement path to within less than the resolution of the sensor
itself.

> **The parameter is fine. The request path is fine. The fault is confined to the one message
> handler that broadcasts it.**

That is a genuinely good outcome. A device with a lying telemetry stream still has a truthful
value underneath, reachable on demand — and the safety check that matters for swapping a limb
runs **once per swap**, not two hundred times a second, so asking directly is entirely
affordable. **The thing we thought might be unbuildable is buildable.**

## The second lie

The other job for the session was to pin down the exact position of the recovery-window boundary
described in the last two notes — the point past which a joint moved while powered down comes
back wrong by a full revolution.

The method is simple: park the shaft very near where we think the boundary is, power down, power
up, see which side it lands on.

**It came back with the device disagreeing with itself.**

The actuator reports its position in more than one way, and those reports have to describe the
same physical shaft. On a healthy reading they agree to less than one encoder count. **This time
they disagreed by 275.**

The restored value was not the parked position, and it was not the parked position minus a
revolution either. It was the parked position *negated* — which is neither of the two things a
wrap can produce. **That is not a boundary effect. That is a corrupted restore.**

So the measurement is void. It tells us nothing about where the boundary is, because the restore
itself misbehaved. The bracket stays where the previous session left it: a window roughly 23°
wide, which does contain the value we originally assumed.

**And the re-test has to park well clear of the boundary**, because the boundary is exactly
where the restore stops being trustworthy. Parking right on top of it was the wrong call.

## The third thing, which is the one that stings

Here is the part worth reading.

**The check that caught this had already caught it — weeks ago, on the screen, in front of us.**

Our bench tool prints a small consistency figure every time it reads a device: a number that
should be essentially zero if the device's two ways of reporting position agree. Across the whole
project that number has never exceeded about one ten-thousandth.

On the corrupted restore, **it printed a number roughly 170 times larger than it has ever been**.

It was printed. It was correct. **Nobody looked.**

The tool flags other conditions loudly, with obvious warning markers. This figure had no threshold and no marker. It was just a number in a column,
being right, alone.

> **A validator that nobody watches is not a validator.** That is a process failure rather than a
> hardware one, and it is the clearest possible argument for the thing we are now building:
> something that watches these checks continuously and reacts, instead of printing them and
> hoping.

The same cross-check, running properly, has now caught **two separate faults in this actuator's
firmware** — the fabricated message and the corrupted restore — **using nothing but the device's
own contradictory statements.** No external reference, no second sensor, no diagnostic cable.
That last part is what matters, because a robot walking across a floor has none of those.

## A health signal that does not exist

One more. The device has a register that is supposed to report communication faults. It has read
clean in every session since we started.

We stopped believing that and tested it: **disconnected the transceiver entirely** and
transmitted into a bus with nothing on the other end for thirty seconds — the condition that
should set every error flag a communication controller has.

**It stayed clean.** And we checked the device had not quietly restarted underneath us, using an
internal counter as a clock, so the reading is real.

Then we enumerated the whole communications configuration and found there are **no error counters
on this device at all.** Not a broken one. None.

> **So a "healthy" reading from that register was never evidence of anything.** Communication
> health has to be worked out by the machine on the other end of the wire — from what arrives,
> when, and whether the sequence is unbroken — and never asked of the device itself.

## Two numbers worth publishing

**Position recovery reproduces to better than 0.0025° at the output** — under a single encoder
count, from a cycle where nothing touched the shaft between the two readings.

**One actuator held to 0.0070° across three days** and a power-down. That is the best figure the
project has produced, and it is roughly a thirtieth of the mechanical backlash in the gearbox the
joint drives through.

The sensing is excellent. **It is the reporting that keeps being wrong**, which is a much more
interesting problem and a much more transferable one.

## What has not happened

**Nothing has moved under power.** Nothing has been armed, nothing commanded to move. **No gait
has run on hardware. There is no leg.** These are individual actuators clamped to a bench.

What exists is a bus that works, a reliable way to ask a lying device for the truth, two firmware
faults found with a technique that needs no special equipment, and a much clearer idea of what
the machine will have to watch for once it stands up.

---

*Part of [Project FENRIR](../../README.md) — an open, modular, hot-swappable quadruped.
Findings here come from the private development repository's bench logs and are published as
the build progresses.*
