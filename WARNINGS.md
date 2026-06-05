# WARNINGS — Clocks parametric debt & known issues

Captured during the retroactive bootstrap (2026-06-04). These are recorded, not yet fixed.
Baseline audit: `scripts/audit_parametric.py` → **84 issues across 5 files** (the duplicate
`ClockFace.FCStd`, deleted during bootstrap, accounted for 8). Re-run the audit after each
remediation phase.

## Remediation order (per specs)

**Params migration → reorient (blank & lines) → XLink wiring.** Reorient runs *after* Params
so re-attached/recreated sketches carry `<<Params>>` expressions, not literals.

## Per-file audit findings (baseline)

### ClockBracket.FCStd — 38 issues
- `Sketch`: 22 unbound dimensional constraints (DistanceX/Y, ParallelDistance, Distance).
- `Sketch001`: 9 unbound dimensional constraints.
- `Sketch002.Constraints[0]`: `Weight` — **B-spline weight, exempt** (see exemption note).
- Feature dims unbound: `Pad.Length/Length2`, `Pad001.Length/Length2`, `Pocket.Length/Length2`.
- No feature-face attachment (bracket is structurally clean on attachment).

### ClockFace-blank.FCStd — 8 issues
- `Sketch`: 4 unbound dimensional constraints (Constraints[13,14,15,16]).
- `Sketch001.Constraints[0]`: `Weight` — exempt.
- ⚠️ **DAG RISK**: `Sketch001` attached to feature face `Revolution.Face5` → retarget to datum (Phase 3).
- Feature dims unbound: `Pocket.Length/Length2`.

### ClockFace-lines.FCStd — 23 issues
- `Sketch`: 4 unbound dimensional constraints (same as blank base).
- `Sketch001.Constraints[0]`: `Weight` — exempt.
- ⚠️ **DAG RISK**: `Sketch001` → `Revolution.Face5`; `Sketch002` (Hours) → `Pocket.Face5`;
  `Sketch004` (HalfHour) → `Pocket.Face5`. All three retarget to datums (Phase 3).
- `Sketch002`: 3 unbound dims. `Sketch004`: 6 unbound dims (incl. 3 Radius).
- Feature dims unbound: `Pad.Length/Length2`, `Pad001.Length/Length2`, `Pocket.Length/Length2`.

### ClockFace-number.FCStd — 7 issues
- `Sketch`: 4 unbound dimensional constraints.
- `Sketch001.Constraints[0]`: `Weight` — exempt.
- Feature dims unbound: `Pocket.Length/Length2`.
- **No feature-face attachment** — already the clean structural target (markings on XY_Plane datum).

## Sketch-orientation inconsistency (vertical vs XY-flat)

`ClockFace-number` lies flat in XY (thickness along Z) with its movement/marking sketches on
the `XY_Plane` datum — the desired state. `ClockFace-blank` and `ClockFace-lines` stand
vertical (disc in XZ, thickness along Y) with downstream sketches anchored to **feature
faces**. The reorient (`macros/reorient_blank_to_xy.FCMacro`,
`macros/reorient_lines_to_xy.FCMacro`) lays them flat and re-attaches their sketches to datum
planes, matching number. These two real macros supersede the bootstrap spec's stub
`macros/reorient_blank_lines_to_xy.FCMacro`. Do not derive new face SKUs from `ClockFace-blank`
until the reorient runs.

## No XLinks today — intended topology is aspirational

Every FCStd is currently **independent**. No XLinks exist between any of them. Common
dimensions (FaceDiameter, FaceThickness, etc.) are duplicated across blank/lines/number/bracket;
changing one will silently desync the others until the central `Params.FCStd` VarSet drives them.
XLink wiring (lines/number → blank) is follow-on work that must happen **after** Params
migration, so XLinks propagate Params expressions rather than literal-number debt.

## Audit exemption: B-spline `Weight` constraints

`Sketcher` `Weight` constraints (Type 18) on B-spline poles are control-point weights, not
user-facing dimensions. Per project decision they are **exempt** from the parametric-binding
requirement. The audit currently flags them; treat those specific lines as known-exempt.
