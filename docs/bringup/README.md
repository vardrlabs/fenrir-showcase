# Bring-up log

Dated notes from hardware sessions, newest first. This is where FENRIR's claims get
checked against a physical device.

## Where the build actually is

Four GIM6010-8 actuators are on the bench. All four have been read, the output-shaft
encoder has been tested across a power cycle, and as of 2026-09-03 **all four have been
configured** — the fleet has left the state the factory shipped it in.

**Nothing has moved under power.** No gait has run on hardware, and no CAN bus has been
exercised yet — the addresses written on 2026-09-03 are untested on a real bus. Everything in
the [README](../../README.md) marked as simulation or CI is exactly that — the walking you can
see in the repo's videos is MuJoCo, not a robot.

## The notes

- **[2026-09-03 — First configuration: the fleet leaves its factory state](2026-09-03-first-configuration.md)**
  The first writes ever made to this hardware. A joint turned through a full output revolution
  while disconnected comes back wrong by exactly one revolution and raises no error — the
  remedy is mechanical. Also corrects our own earlier reasoning about where the recovery
  window sits.
- **[2026-08-18 — Hot-swap position recovery, verified](2026-08-18-hot-swap-position-verified.md)**
  The joint recovers absolute output-shaft position after a power cycle, including movement
  that happened while it was unpowered. Also documents the limit: recovery holds within one
  output revolution, and outside that window it is silently wrong.
- **[2026-08-11 — First contact: what the actuator actually said](2026-08-11-first-contact.md)**
  Read-only inspection of the parameter tree. Settled the encoder resolution at 14-bit,
  found two shipped defaults that contradict the manuals, and established that the firmware
  version number belongs to a vendor fork and cannot be looked up.

## How we label things

Claims are marked unverified until hardware proves them, and stay that way in our own
documents however plausible they look. These notes record what the measurements showed —
including the corrections, the constraints they turned up, and the occasions we published
something before we had tested it.
