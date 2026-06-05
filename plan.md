# Clocks — Plan

Generated for the retroactive bootstrap (2026-06-04). Geometry pre-exists; this plan
documents the parametric target, not a from-scratch modeling order. Authoritative specs:
`docs/superpowers/specs/2026-06-04-clocks-bootstrap-design.md` and
`docs/superpowers/specs/2026-06-04-clockface-reorient-design.md`. Execution plan:
`docs/superpowers/plans/2026-06-04-clocks-bootstrap-params-reorient.md`.

## PARAMETERS

Central VarSet lives in `Params.FCStd` (`VarSet`). Cross-document references use
`<<Params>>#VarSet.VarName`. Initial set (App::PropertyLength unless noted); refined during
the Params-migration pass to cover every literal found by `scripts/audit_parametric.py`.

| Name | Type | Meaning |
|---|---|---|
| FaceDiameter | Length | Clock face overall OD |
| FaceThickness | Length | Face disc thickness |
| BezelWidth | Length | Outer bezel ring width |
| MovementBossDiameter | Length | Boss around the movement bore |
| MovementShaftClearance | Length | Slip fit, face-to-shaft (decoupled clearance) |
| MovementShaftHoleDiameter | Length | Derived: shaft Ø + MovementShaftClearance |
| MountingScrewClearance | Length | Bracket-to-wall fastener fit (decoupled clearance) |
| MountingScrewHoleDiameter | Length | Derived: screw Ø + MountingScrewClearance |
| WallThickness | Length | General wall thickness |
| BracketWidth / BracketHeight / BracketThickness | Length | Mounting bracket envelope |
| HourMarkLength / HourMarkWidth / HourMarkPadHeight | Length | Hour tick geometry (pad 1.0mm) |
| HalfHourMarkLength / HalfHourMarkWidth / HalfHourMarkPadHeight | Length | Half-hour tick geometry (pad 0.5mm) |
| MarkCount | Integer | Tick repetitions (12) |

Decoupled-clearance rule: `MovementShaftClearance` and `MountingScrewClearance` are distinct
concepts — never overload `WallThickness` to express either.

## FEATURE TREE (per file)

- **ClockBracket** — wall mounting bracket (independent of faces).
- **ClockFace-blank** — `Sketch` (revolve profile) → `Revolution` (disc) → `Sketch001`
  (movement pocket) → `Pocket`. Parametric template for the face SKUs.
- **ClockFace-lines** — blank base, plus `Sketch002`/`Pad`/`PolarPattern` (Hours ×12) and
  `Sketch004`/`Pad001`/`PolarPattern001` (HalfHour ×12).
- **ClockFace-number** — blank base, plus numeric face markings. **Already in the target
  XY-flat orientation with markings on the `XY_Plane` datum** — the structural model the
  others copy.

## ORIENTATION STATUS (corrected 2026-06-04)

| File | Disc plane | Thickness | Marking/pocket attach | State |
|---|---|---|---|---|
| ClockFace-number | XY (flat) | Z | XY_Plane datum ✅ | target |
| ClockFace-blank | XZ (vertical) | Y | Revolution.Face5 ⚠️ | reorient pending |
| ClockFace-lines | XZ (vertical) | Y | Pocket.Face5 ⚠️ | reorient pending |

Reorient (Phase 3 of the execution plan) re-attaches blank & lines to datum planes and lays
them flat to match number.

## CONSTRAINT STRATEGY

- Every dimensional sketch constraint binds via `setExpression` to `<<Params>>#VarSet.<Var>`.
- Sketches attach to `PartDesign::Plane` datums / principal planes only — never feature
  faces (DAG-cycle risk).
- SKU XLinks (future) reference datum geometry of the parent (`ClockFace-blank`), never faces.

## VALIDATION

- `python3 scripts/audit_parametric.py` reports clean (B-spline `Weight` constraints exempt,
  per project decision) before any commit that claims a parametric milestone.
- Each face SKU prints in PLA before being declared production-ready.
