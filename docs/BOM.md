# FENRIR bill of materials

Complete component list for the v1 build. Compiled 2026-07-17 from the
private Build Bible v2.1 BOM, the robot configuration, and the build-log
order history. Statuses: **owned** · **ordered** (date, ETA) · **planned**
(phase-gated) · **canceled** (kept for the record).

Prices are estimates at order time, USD.

## Actuation

| Item | Qty | Unit est. | Status | Notes |
|---|---|---|---|---|
| SteadyWin GIM6010-8, **Standard body, 24 V winding, GDS68 driver, WITH secondary output-shaft encoder, no brake** | 4 | $100–150 | **Ordered 2026-07-12**, ETA ~Jul 25 | One leg + spare; all units identical. Secondary encoder gives absolute joint position on power-up: no recalibration after hot-swap. No brake: the robot lies down unpowered |
| SteadyWin GIM6010-8 (same variant) | 8 | $100–150 | Planned | Fleet completion after one-leg validation |
| MiToot 2804 gimbal motor, 100 KV | 1 | owned | **Owned** | Bench/learning rig only (~0.1 N·m class) |
| SimpleFOC Mini (DRV8313) | 1 | owned | **Owned** | Bench rig driver (~2.5 A limit) |
| 360 KV / 1000 KV hobby BLDC motors | 2 | owned | **Owned** | Shelf; not for legs |
| ~~ST B-G431B-ESC1 discovery boards~~ | ~~2~~ | ~~$60~~ | **Canceled 2026-07-16** | Price doubled from ~$20 ea. Bench rig runs on the owned SimpleFOC Mini stack; if the DIY high-torque path revives, dual-channel ODrive-lineage boards ($40–60) are the better value |

## Compute & AI

| Item | Qty | Unit est. | Status | Notes |
|---|---|---|---|---|
| Raspberry Pi 5, 8 GB | 1 | owned | **Owned** | Layer 3 cognition, Ubuntu 24.04 + ROS 2 Jazzy |
| Raspberry Pi AI HAT+ 2 (Hailo-10H, 40 TOPS) + active cooler | 1 + 1 | ~$140 | **Ordered 2026-07-12** | Vision AND local LLM acceleration; cooler non-negotiable |
| Teensy 4.1 (600 MHz Cortex-M7) | 1 | owned | **Owned** | Layer 2 real-time: CAN master, safety supervisor, health registry |
| Raspberry Pi Camera Module 3 | 1 | owned | **Owned** | Head has two camera bays: stereo = matched pair later; NoIR night module = separate attachment |
| Touchscreen(s) | 1–2 | owned | **Owned** | Debug/UI panels |

## Sensing

| Item | Qty | Unit est. | Status | Notes |
|---|---|---|---|---|
| TDK QCIoT-ICM42688P Pmod IMU (SPI) | 1 | ~$32 | **Ordered 2026-07-12** | Fallbacks qualified: ISM330DHCX or BMI088. Driver-node isolation makes the choice invisible to the rest of the stack |
| MT6816 magnetic encoders, 14-bit SPI/ABZ | 3 | owned | **Owned** | Bench actuator encoders |
| AS5600 encoder | 1 | owned | **Owned** | Bench rig first pass (I²C); driven joints use SPI |
| INA228 power monitor, 20-bit | 1 | ~$8 | **Ordered 2026-07-12** | Main battery line: coulomb counting → state of charge |
| INA226 power monitor | 4 | ~$3 | **Ordered 2026-07-12** | One per leg rail: per-leg current telemetry |

## Power

| Item | Qty | Unit est. | Status | Notes |
|---|---|---|---|---|
| Mean Well LRS-350-24 bench PSU (24 V, 350 W) | 1 | ~$35 | **Ordered 2026-07-12** | Develop on PSU, not LiPo |
| 6S LiPo battery | 1 | ~$100 | Planned (Phase 2) | Bench PSU until untethered work starts |
| 5 V / 5 A BEC | 1 | ~$20 | Planned (Phase 2) | Pi rail; sized to ride through motor transients |
| Blade fuses, **25 A** (leg rails) | 4 + spares | assort. | **Ordered 2026-07-12** | One fused rail per leg module |
| Blade fuse, **40 A** (main line) | 1 + spares | assort. | **Ordered 2026-07-12** | Battery main |
| Inline fuse holders, 12 AWG | 4 | ~$2 | **Ordered 2026-07-12** | Leg rails |
| Inline fuse holder, 10 AWG | 1 | ~$3 | **Ordered 2026-07-12** | Main line |

## Connectivity & wiring

| Item | Qty | Unit est. | Status | Notes |
|---|---|---|---|---|
| SN65HVD230 CAN transceiver breakouts | 5 | ~$2.50 | **Ordered 2026-07-12** | Dual CAN buses + spares; 120 Ω termination both ends of each bus |
| XT30 connector pairs | kit | ~$15 | **Ordered 2026-07-12** | Per-leg power half of the two-connector hot-swap interface |
| JST-GH 4-pin cable kit, **"Same Direction"** (straight-through) | kit | ~$15 | **Ordered 2026-07-12** | CAN daisy-chain. Never the "Reverse" variant: it swaps CAN H/L |
| JST-GH 4-pin **"Single Head"** pigtails | kit | incl. | **Ordered 2026-07-12** | Board-end termination |
| 16 AWG silicone wire | spool | incl. | **Ordered 2026-07-12** | Power runs |
| SK6812 addressable LED segments + 74AHCT125 level shifter + wiring (series resistor, bulk capacitor) | 1 set | ~$20 | Planned (Phase 1 batch) | Bay status LEDs: the health state machine, visible across the room |

## Structure & filament

| Item | Qty | Unit est. | Status | Notes |
|---|---|---|---|---|
| Bambu Lab A1 printer | 1 | owned | **Owned** | 256 mm bed: leg segments print one-piece |
| Hardened steel 0.4 mm nozzle | 1 | ~$15 | Planned | Enables carbon-fiber filament for hip brackets |
| PETG-HF filament (structural) | 2–3 kg | ~$25/kg | Planned | Motors run hot: no PLA near actuators |
| PETG-CF filament (hip brackets) | 1 kg | ~$30/kg | Planned | Needs the hardened nozzle |
| TPU 95A filament (feet) | 0.5 kg | ~$30/kg | Planned | Compliant printed feet |
| PLA+ filament (prototypes/jigs only) | 1–2 kg | ~$20/kg | Planned | Never load-bearing near heat |
| Bearings, GT2 belt stock, shafts | TBD | ~$50 | Planned (CAD-gated) | Sizes finalize with leg CAD around the actuator STEP files |

## Fasteners & hardware

| Item | Qty | Unit est. | Status | Notes |
|---|---|---|---|---|
| Leg-module mounting bolts (4-bolt pattern per bay) | 16 + spares | TBD | Planned (CAD-gated) | Sizes finalize with the hot-swap interface CAD; a leg detaches with 2 plugs + 4 bolts |
| Heat-set inserts, printed-part hardware | assort. | TBD | Planned (CAD-gated) | With first structural prints |

## Safety & test equipment

| Item | Qty | Unit est. | Status | Notes |
|---|---|---|---|---|
| Big red e-stop switch | 1 | ~$10 | **Ordered 2026-07-12** | Wired into the main line from day one; supreme over all software |
| Soldering station | 1 | owned | **Owned** | |
| Pixhawk flight controller | 1 | owned | **Owned** | Shelved for a future aerial variant; its JST-GH cables serve as compatible spares |

## Budget summary

Day-1 batch spent (ordered 2026-07-12): **~$700–840**.
Full integrated-actuator path: **~$1,700–2,100** (dominated by 12× GIM6010-8).
Hybrid fallback documented at ~$1,200–1,400 if budget forces it.
