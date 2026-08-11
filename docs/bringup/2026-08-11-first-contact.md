# First contact: what the actuator actually said

2026-08-11 · One GIM6010-8 on the bench, read-only. The motor never moved and nothing
was written to the device.

This is a note for anyone else integrating these actuators, and a small illustration of
why FENRIR verifies against hardware rather than against paper. Nothing here is a
complaint about the vendor — the documentation is genuinely good, and documentation drift
on a fast-moving part is normal. It is just that a datasheet is a claim and a device is
evidence.

## Setup

One actuator, clamped, output shaft free and unloaded. A 24 V bench supply with an inline
fuse, measuring 23.81 V at the terminals. USB-C to a host running `odrivetool`. No CAN
bus, no motion, no configuration writes — the entire session was reading the device's
parameter tree and comparing it against what the manuals say.

## The headline: a version number you cannot look up

The device reports firmware **v0.6.5**. It is **not** upstream ODrive 0.6.5. It is a
vendor fork carrying its own version numbering, built on ODrive **0.5.x** architecture.

This matters more than it sounds, because acting on the version string sends you to
documentation that describes a different device. The evidence is structural rather than
cosmetic:

- **`axis0.encoder` still exists**, carrying `config.cpr`, `shadow_count`,
  `count_in_cpr` and `pos_estimate`. Upstream ODrive 0.6.x removed that object entirely
  and replaced it with a mapper/estimator split. If this really were upstream 0.6.5, the
  paths we read successfully would not exist at all.
- **The hardware reports v3.12.** Upstream ODrive's v3 board line ended at v3.6.
- **The identity string carries the vendor's own brand**, not ODrive's.

And the tree contains a whole surface that appears in no upstream release and in neither
manual revision:

| Present on the device | What it is |
|---|---|
| `controller.adrc_z1`, `adrc_z2` | Active Disturbance Rejection Control observer states |
| `controller.autotuning`, `auto_set_gains()`, `auto_set_bandwidth()` | automated gain tuning |
| `controller.input_mit_kp`, `input_mit_kd` | impedance-control gains as first-class parameters |
| `encoder.poll_sec_enc()` | secondary encoder polling |
| `encoder.pos_abs`, `set_current_pos_zero()` | absolute-position handling |
| `mechanical_brake.engage()` / `release()` | holding brake |
| `config.can.thermistor_rate_ms` | a periodic telemetry message absent from both manuals |
| `motor.last_drv_fault`, `task_times.*` | gate-driver fault capture, per-task timing |

Upstream 0.5.x documentation remains useful for the shared core — axis states, control
modes, the CAN framing. Upstream 0.6.x documentation is actively misleading for this
device. Everything in the table above is documented nowhere public that we could find.

**The transferable lesson:** a version string from a forked firmware is not a version you
can look up. Identify the device by the *shape of its parameter tree*, not by what it
calls itself. We are keying our firmware-compatibility checks off observed structure for
exactly this reason.

## Encoder resolution: settled at 14-bit

Three sources disagreed. The product listing and the older English manual revision both
said 16-bit; the newer manual revision said 14-bit and named the encoder part.

The device settles it:

```
axis0.encoder.config.cpr    ->  16384
```

16384 is 2¹⁴ exactly. The newer manual and the encoder part number were right; the listing
and the older revision were wrong. Worth knowing before you size anything that depends on
counts-per-revolution, because a factor-of-four error in position quantisation is the kind
that looks plausible right up until it doesn't.

## Two shipped defaults that contradict the manuals

Both manual revisions state the factory node ID is **0**. The unit arrived as
**`node_id = 1`**.

Both revisions describe bus termination as something you enable on the nodes at the
physical ends of the bus. In fact **`enable_r120` ships `True` on every unit** — each
board terminates out of the box. On a multi-node bus that is backwards: only the two end
nodes should terminate, so the setup step is *disabling* termination on the interior
nodes, not enabling it on the ends. Six terminators on one bus is not a working bus.

Neither of these is dangerous if you check. Both are the kind of thing you discover at
the worst possible moment if you don't — which is the argument for reading the device
before assembling anything around it.

## The USB driver question: both documents were right

The manual's host-software section specifies **WinUSB**. The vendor's Motor Wizard tool
ships a readme specifying **libusb** and stating that WinUSB is not supported. Read side
by side, that looks like a contradiction.

It isn't. Each is correct for its own tool:

- **`odrivetool` → WinUSB**
- **Motor Wizard → libusb**

Confirmed on hardware: WinUSB bound to the right interface connects `odrivetool`
successfully. Swapping between the two tools means re-binding the driver. Annoying, not
broken — and worth ten minutes of knowing rather than an afternoon of guessing.

## What is still open

The most valuable question is not answered by reading a parameter tree, so it remains
open: **does the joint recover its absolute output-shaft position after a power cycle?**
That is the property recalibration-free hot-swap depends on. The device exposes a
secondary-encoder poll function and an error path for it, so the mechanism is there — but
whether position survives a power cycle needs the physical test: move the shaft, power
the unit down, bring it back, read the position. That test is next.

Also deliberately not done in this session: no node IDs assigned, no calibration run, no
current limits changed, no writes of any kind. The unit reports itself pre-calibrated by
the vendor, and re-running calibration spins the motor. First contact was for looking.

---

*Part of [Project FENRIR](../../README.md) — an open, modular, hot-swappable quadruped.
Findings here come from the private development repository's bring-up log and are
published as the build progresses.*
