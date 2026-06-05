# WARNINGS — Clocks parametric debt & known issues

Captured during the retroactive bootstrap (2026-06-04).

## STATUS after Params migration + reorient (2026-06-04)

**Params migration complete.** Every literal dimensional constraint across the four FCStds is
bound to `<<Params>>#VarSet.<Var>` in the central `Params.FCStd` (21 params). Geometry verified
unchanged (bbox + volume identical pre/post); central Params proven to drive geometry
(FaceDiameter round-trip). The bracket's pre-existing **local** VarSet (`InsideDistance`) was
migrated into central Params and the dead local VarSet deleted.

**Reorient complete.** `ClockFace-blank` and `ClockFace-lines` are now **XY-flat, ridge up
(disc Z 0→3), matching `ClockFace-number`**. Base `Sketch`→`XZ_Plane`, `Sketch001`→`XY_Plane`;
lines' Hours/HalfHour markings moved off `Pocket.Face5` onto a new `DialFaceDatum` plane whose
Z-height is bound to `FacePlateThickness`. Re-attach was clean (pattern bbox + body volume
unchanged — no recreate fallback needed). The base flip used `Sketch.MapReversed=True` +
`Pocket.Reversed=True` to put the bezel ridge on +Z.

**✓ Corrected audit now passes on all five files.** No unbound dimensions, no feature-face DAG
risk. STL/3MF for blank & lines were re-exported in the new flat orientation
(watertight/manifold, 0.01 mm deflection). **Geometry XLink wiring was evaluated and declined
(2026-06-05)** — see the decision note below; nothing remains outstanding from the original
bootstrap/reorient plan.

> ⚠️ **Canonical `audit_parametric.py` bug (affects ALL projects).** The copied-from-Spade
> audit shipped a WRONG Sketcher constraint-type table — it labeled Tangent(5) as
> "ParallelDistance", Perpendicular(10) as "Angle", Block(17) as "Diameter", and missed real
> Radius(11)/Diameter(18). Result: it reported geometric constraints as unbound dimensions
> (the original "84 baseline" was heavily inflated with false positives). The **Clocks copy is
> fixed** (correct enum, verified 1:1 against the live Sketcher API, plus Type-aware feature
> dims and a 90°-angle exemption). The canonical copy and other projects' copies are still
> buggy — propagate the fix.

The historical baseline below is retained for reference; the per-file literal counts in it
were partly false positives from the audit bug. The DAG-risk findings in it are real.

---

## Historical baseline (pre-migration, pre-audit-fix — partly inflated)

Baseline audit (buggy script): **84 issues across 5 files** (the duplicate `ClockFace.FCStd`,
deleted during bootstrap, accounted for 8).

## Remediation order (per specs)

**Params migration → reorient (blank & lines) → ~~XLink wiring~~.** Params migration and the
reorient are done. **Geometry XLink wiring was evaluated and declined on 2026-06-05** (YAGNI —
see the decision note below). Reorient ran *after* Params so re-attached sketches carry
`<<Params>>` expressions, not literals.

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

## Decision (2026-06-05): central Params, no geometry XLinks

Originally the "live parametric parent (XLink)" topology was the intended end state. It was
evaluated after the Params migration and **declined (YAGNI)**:

- **Dimension sync is already solved** by the central `Params.FCStd` VarSet — all four FCStds
  reference `<<Params>>#VarSet.*`, so common dimensions stay synchronized with no XLinks.
- **What geometry-XLinking would add** is base-disc *topology* inheritance (a structural change
  to blank's profile propagating to lines/number). For a clock line where the disc is stable and
  only the markings vary, that benefit is marginal.
- **What it would cost** is rebuilding the two clean, audit-passing SKU files to consume blank's
  body via cross-document SubShapeBinders, plus topological-naming fragility (XLinks break on
  FCStd rename) and recompute-order coupling.

**Accepted consequence:** the base disc geometry is duplicated across the face SKUs, so a
*structural* (not dimensional) change to the base profile must be replicated by hand in each.
Revisit XLinking only if such structural changes become frequent.

## Audit exemption: B-spline `Weight` constraints

`Sketcher` `Weight` constraints (Type 18) on B-spline poles are control-point weights, not
user-facing dimensions. Per project decision they are **exempt** from the parametric-binding
requirement. The audit currently flags them; treat those specific lines as known-exempt.
