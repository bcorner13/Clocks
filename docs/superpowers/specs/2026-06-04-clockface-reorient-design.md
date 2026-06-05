# ClockFace Reorient Design Spec (blank & lines → XY-flat)

**Date:** 2026-06-04
**Project:** Clocks
**Status:** Approved by Bradley — pending implementation plan
**Type:** Geometry reorient (re-attach in place; no redraw unless fallback triggers)
**Priority:** Runs after bootstrap scaffolding + Params migration (see `2026-06-04-clocks-bootstrap-design.md`)

---

## Why this exists

This spec defines the XZ→XY reorient of `ClockFace-blank` and `ClockFace-lines` to match
`ClockFace-number`. Per Bradley's final call, it honors the bootstrap spec's documented
order — **Params migration → reorient → XLink wiring** — so the reorient operates on
sketches whose dimensional constraints are already bound to `<<Params>>` expressions. The
bootstrap spec (`2026-06-04-clocks-bootstrap-design.md`) governs the scaffolding + the
Params migration that precede this reorient.

## Correction to the bootstrap spec's plane facts

Inspection of the live FCStds proved the bootstrap spec mislabeled the planes. The
corrected, verified reality:

| File | Disc lies in | Thickness along | Base `Sketch` attaches to | Markings/pocket attach to |
|---|---|---|---|---|
| `ClockFace-number` (**target**) | **XY** (flat on bed) | **Z** (0→3) | `XZ_Plane` (datum) | `XY_Plane` **datum** ✅ |
| `ClockFace-blank` (current) | XZ (standing up) | **Y** (−3→0) | `YZ_Plane` (datum) | `Revolution.Face5` **feature face** ⚠️ |
| `ClockFace-lines` (current) | XZ (standing up) | **Y** (−3→0) | `YZ_Plane` (datum) | `Pocket.Face5` **feature face** ⚠️ |

So the inconsistency is **two** problems, not one:
1. **Orientation** — blank/lines stand vertical (thickness in Y); number lies flat (thickness in Z).
2. **Coupling/DAG debt** — blank/lines anchor downstream sketches to *feature faces*; number anchors to the `XY_Plane` *datum*. The global rules flag feature-face attachment as a DAG-cycle red flag.

`ClockFace-number` already embodies the clean target on both counts. The goal of this work
is to make blank and lines match it.

## Verified current recipes

**number (target):** base `Sketch` on `XZ_Plane`; `Revolution` axis ≈ (0,0,−1) → spins
profile around **Z**, disc flat in XY (Z 0→3); `Sketch001` (movement pocket) on `XY_Plane`
datum.

**blank (current):** base `Sketch` on `YZ_Plane`; `Revolution` axis = (0,1,0) → spins
around **Y**, disc in XZ (Y −3→0); `Sketch001` on `Revolution.Face5`; `Pocket` UpToFirst.

**lines (current):** identical base to blank, plus `Sketch002` "Hours" (4 line segments,
11 constraints) → `Pad` 1.0mm → `PolarPattern` ×12 around sketch N_Axis; and `Sketch004`
"HalfHour" (5 line segments, 14 constraints) → `Pad001` 0.5mm → `PolarPattern001` ×12.
Both marking sketches anchor to `Pocket.Face5` (feature face ⚠️).

## Approach — re-attach in place (decided)

Chosen over (a) Body.Placement rotation and (b) re-attach base sketch only. Rationale:
matches number's clean datum structure, fixes orientation AND DAG debt in one pass, and
preserves all constrained geometry. The reorient is **independent of the constraint
values** — re-attaching a sketch to a different datum does not touch its dimensional
constraints. Since Params migration runs first, those constraints are already
`<<Params>>#VarSet.Var` expressions when the reorient happens, and re-attachment preserves
them unchanged.

### ClockFace-blank (macro `macros/reorient_blank_to_xy.FCMacro`)
1. Snapshot to `ClockFace-blank.Session-20260604.FCStd` first (session-hygiene rule).
2. Re-attach base `Sketch`: `YZ_Plane` → `XZ_Plane`, matching number's MapMode/placement,
   so the revolve axis becomes Z and the disc lands flat in XY.
3. Retarget `Sketch001` (movement pocket): `Revolution.Face5` → `XY_Plane` datum, as number does.
4. Recompute. Verify disc flat in XY (bbox dz ≈ 3, disc in XY), pocket on the correct face.
   Flip `Revolution.Reversed` / `Pocket.Reversed` if the solid builds on the wrong side.
5. Screenshot for Bradley's review. **No save until approved.**

### ClockFace-lines (macro `macros/reorient_lines_to_xy.FCMacro`)
Steps 1–3 as blank, then:
6. Retarget `Sketch002` (Hours) and `Sketch004` (HalfHour): `Pocket.Face5` → `XY_Plane`
   datum (or a thin offset datum at the face surface), preserving line geometry + polar patterns.
7. Recompute full tree (Pocket → Pad → PolarPattern → Pad001 → PolarPattern001).
8. Verify markings sit on the visible face, centered and radial; screenshot for review.

### Fallback for markings (decided: recreate)
Marking sketches were authored in the `Pocket.Face5` local frame; their 2D coordinates may
not land correctly on the `XY_Plane` datum. If a re-attached marking sketch mis-places, the
fallback is to **recreate that sketch** on the datum to match the original geometry (same
segment lengths, radial positions, constraints), verified visually. Bradley chose recreate
over pause-and-show. Because Params migration runs first, a recreated sketch binds its
dimensional constraints **directly to `<<Params>>` expressions** — no literal-coordinate
debt is introduced (this supersedes the earlier R4 concern).

## Constraints / rules honored

- All edits via reviewable macros under `macros/`; no direct FCStd XML surgery.
- Sketches end up on **datum/principal planes only** — never feature faces (global rule #3).
- **No raw coordinate edits** to fix geometry; reorientation is via attachment + revolve axis,
  not by editing StartX/EndY etc. (global rules #1/#2). Recreate-fallback redraws against the
  same dimensional intent, to be Params-migrated later.
- Dimensional constraints are **left as-is** (still literals) — Params migration is a separate,
  later pass and is explicitly out of scope here.

## Out of scope (handled elsewhere, not in this spec)

- Params migration (literals → `<<Params>>#VarSet.Var`) — runs **before** this reorient, per
  the bootstrap spec. Not redefined here.
- XLink wiring (lines/number → blank) — runs after this reorient.
- Any change to `ClockBracket.FCStd`.
- Re-export of STL/3MF — **decided: leave for later** (reorient FCStd source only this session;
  regenerate exports after Bradley reviews the reoriented models).

## Sequence (honors bootstrap spec ordering)

1. Retroactive bootstrap scaffolding per `2026-06-04-clocks-bootstrap-design.md` (creates the
   empty `Params.FCStd`, CLAUDE.md, audit, git, etc.).
2. Params migration: populate `Params.FCStd` and rewrite literal dimensional constraints in
   blank/lines/number/bracket as `<<Params>>#VarSet.Var` expressions.
3. Reorient blank → verify/screenshot → Bradley approves → save.
4. Reorient lines → verify/screenshot → Bradley approves → save.
5. (Later) XLink wiring.

The stub `macros/reorient_blank_lines_to_xy.FCMacro` named in the bootstrap spec is superseded
by the two real macros above (`reorient_blank_to_xy.FCMacro`, `reorient_lines_to_xy.FCMacro`);
note this in the bootstrap scaffolding.

## Acceptance criteria

- [ ] `ClockFace-blank`: base `Sketch` on `XZ_Plane`; `Sketch001` on `XY_Plane` datum;
      bbox thickness along Z (dz ≈ 3), disc in XY; recompute clean (no DAG errors).
- [ ] `ClockFace-lines`: same as blank, plus `Sketch002`/`Sketch004` on a datum (not
      `Pocket.Face5`); polar patterns intact (×12 each); markings centered/radial on the face.
- [ ] No sketch in either file attaches to a feature face after the reorient.
- [ ] Dimensional constraints remain bound to `<<Params>>` expressions through the reorient
      (re-attached sketches keep their expressions; any recreated sketch binds to Params).
- [ ] A pre-edit `*.Session-20260604.FCStd` snapshot exists for each file.
- [ ] Both files saved only after Bradley approves the screenshots.
- [ ] STL/3MF not regenerated (deferred).

## Risks

- **R1 — Marking sketches mis-place on re-attach.** Mitigated by the recreate fallback.
- **R2 — Revolve builds on the wrong side after axis change.** Mitigated by checking bbox
  Z-range and flipping `Reversed`.
- **R3 — `FaceN` topological-naming breakage cascades during re-attach.** Expected; the whole
  point is to move *off* those faces onto datums. Recompute after each step and verify before
  proceeding to the next sketch.
- **R4 — Recreate-fallback geometry drift.** Because Params migration runs first, a recreated
  sketch binds directly to `<<Params>>` expressions (no literal debt). Residual risk is only
  visual placement drift, mitigated by screenshot verification before save.
