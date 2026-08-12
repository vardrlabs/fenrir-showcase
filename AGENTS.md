# AGENTS.md — for AI agents working in this repository

**This repository is downstream.** `vardrlabs/fenrir` (private) is upstream and
authoritative. Everything here is curated from it by hand, is deliberately partial, and
lags on purpose. Nothing here is a source of truth about the robot.

If you are working here, the most useful thing you can know is what *not* to do.

## Never "correct" this repo from your own knowledge

Content that looks wrong, incomplete, or out of date is usually one of three things:
curated (detail withheld on purpose), lagging (upstream has moved and this repo has not
been refreshed yet), or genuinely wrong.

You cannot tell which from inside this repository. So:

1. Check the private repo. If it disagrees with what is written here, this repo is
   **lagging** — say so, and let a human do the refresh from upstream.
2. If the private repo agrees with what is written here and you still think it is wrong,
   that is a **finding for RK**, not a fix. Report it with evidence.
3. Never edit a curated document to match your own understanding of the subject.

A confident agent "helpfully" fixing a deliberately curated public document is the exact
failure mode this file exists to prevent.

## Never publish what is not settled upstream

These do not belong in this repository, in any file, at any time:

- Open verification debt, open decisions, or anything mid-argument. Internal identifiers
  (`V-n` verification items, `D-n` decisions) never appear here.
- Wire-protocol internals, the command grammar and its training data, control internals,
  firmware source, or the full machine configuration.
- Vendor correspondence, unsent questions, or commercial detail.
- Torque budgets, bus-load arithmetic, node-ID schemes, or anything a competitor could
  use to skip work rather than to evaluate the platform.

If you are unsure whether something is publishable, it is not. Ask.

## Never claim a capability that has not been demonstrated

Simulation results and CI results are fair game, and should be labelled as such.
**Hardware behaviour is not claimable until it has actually happened.** Prefer the
conservative phrasing: "four actuators received, one read over USB, nothing has moved
under power" is accurate; "hardware bring-up complete" is not.

This matters more here than anywhere else in the project, because this is the surface
third parties would evaluate the platform on, and eventually build modules against. A
published specification that turns out to be wrong costs somebody else their time.

## What this repo is for

The public face of an open modular-robotics platform: what FENRIR is, how it is
architected, what has been verified, and what the plan is. At launch it becomes the
place the attachment specification and SDK live. Accuracy of anything spec-shaped
therefore matters more than completeness.

## Cold start

1. `README.md` — what the project is and what provably works today.
2. `docs/BUILD_BIBLE.md` — the plan, public edition, with its own provenance note.
3. `docs/ARCHITECTURE.md`, `docs/BOM.md`, `docs/MILESTONES.md` — system view,
   components, dated results.
4. `docs/bringup/` — dated records of hardware sessions.

The private repository's `AGENTS.md` carries the full operational brief: authority
ordering, the `[TN]`/`[REC]` conventions, the vendor-protocol quarantine, and the rule
that approved specs land verbatim. Those rules apply here too.
