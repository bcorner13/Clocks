# Project rules — Clocks

Every FCStd in this project is currently **independent** — no XLinks, no shared Params. Two
consequences flow from that: (a) common dimensions (FaceDiameter, FaceThickness, …) are
duplicated across blank/lines/number/bracket, and changing one will silently desync the
others; (b) the immediate parametric debt is literal numbers in sketches plus marking/pocket
sketches anchored to **feature faces**. Migrate to Params *before* wiring up XLinks — wiring
first only propagates the debt. Read the full rules below before any geometry change.

---

## Hard rules (this project)

These restate the global rules in `~/.claude/CLAUDE.md` with project-specific context. Cite the actual incident or constraint that motivates each one — generic restatements are useless because the global file already has them.

1. **Everything parametric.** Files predate the parametric-rigor bootstrap. Baseline audit
   (2026-06-04) found **84 unbound literals + DAG flags** across the project (see
   `WARNINGS.md`). Worst offenders: `ClockBracket.Sketch`/`Sketch001` (31 unbound dims) and
   `ClockFace-lines` markings. Migrate these to `<<Params>>#VarSet.Var` via macros — never by
   editing the values in place.

2. **No fixing geometry by editing raw sketch coordinates.** No prior coordinate-edit
   incident in this project; rule applies preventively. (The cautionary incident is the Spade
   Connector project, 2026-04-15/16 — documented globally.)

3. **Attach sketches to datum planes, not feature faces.** This project **actively has the
   problem**: `ClockFace-blank.Sketch001` and `ClockFace-lines.Sketch001/Sketch002/Sketch004`
   are attached to `Revolution.Face5` / `Pocket.Face5`. `ClockFace-number` is the
   counter-example done right — its marking sketch is on the `XY_Plane` datum. The reorient
   macros retarget blank & lines onto datums. Before XLinks are wired, **no sketch may remain
   on a feature face** or the first SKU recompute will produce a DAG cycle.

4. **Clearance concepts stay decoupled.** This project's clearance Params, one per interface:
   - `MovementShaftClearance` — clock face bore ↔ quartz movement shaft (slip fit)
   - `MountingScrewClearance` — bracket screw hole ↔ wall fastener
   Never overload `WallThickness` (or each other) to express either.

---

## Assembly architecture

The product line is a wall clock built from three independently-printed pieces:

- **ClockFace** (one of the SKUs: `-blank` template, `-lines`, or `-number`) is the visible
  disc. It carries a central bore + boss for a standard quartz movement shaft (~6mm) and
  raised/recessed face markings. Target orientation: disc flat in the XY plane, thickness
  along Z, printed face-down/up without supports.
- **ClockBracket** is a separate wall-mounting bracket that the movement/face assembly hangs
  from. It is independent of the face geometry (no shared features today).
- The **quartz movement** (not printed) seats through the face bore from behind; its shaft
  passes through `MovementShaftHoleDiameter`. The face markings (lines or numbers) are
  patterned ×`MarkCount` (12) around the face center via polar patterns.

The "ClockFace-blank as parametric parent, lines/number XLinked from it" topology is the
**intended** end state — it does not exist yet (see Files table + WARNINGS.md).

---

## Files in this project

| File | Role | Depends on | Status |
|---|---|---|---|
| `Params.FCStd` | VarSet — all parametric variables (21) | — | ✅ populated; drives all four FCStds |
| `ClockFace-blank.FCStd` | Parametric face template (disc + movement pocket) | `Params.FCStd` | ✅ Params-bound · ⚠️ `Sketch001` on feature face + XZ-vertical (reorient = Phase 3) |
| `ClockFace-lines.FCStd` | SKU: line/tick markings (Hours ×12, HalfHour ×12) | `Params.FCStd`, blank | ✅ Params-bound · ⚠️ `Sketch001/002/004` on feature faces + XZ-vertical (reorient = Phase 3) |
| `ClockFace-number.FCStd` | SKU: numeric markings (separate `Part::Extrusion` numerals) | `Params.FCStd`, blank | ✅ Params-bound · clean datum attachment · already XY-flat — structural model for the others |
| `ClockBracket.FCStd` | Shared wall mounting bracket | `Params.FCStd` | ✅ Params-bound (incl. migrated local `InsideDistance`→`BracketInnerInset`); audit clean |

Notes: no file is ❌ BROKEN. As of the 2026-06-04 Params migration, all dimensional literals
are bound to central Params; the only remaining ⚠️ is the feature-face attachment in
blank/lines (Phase 3 reorient). `ClockFace-number` builds its numerals as separate
`Part::Extrusion`/`ShapeString` objects (an `FcClock001` group), not PartDesign pads — and its
`Sketch001` "CenterHole" is currently *unconsumed* (drives no solid). `ClockFace.FCStd` (a
duplicate of `-blank`) was deleted during bootstrap; its `*.Session-20260604.FCStd` snapshot is
the archive.

---

## Params variables (summary)

`Params.FCStd` (`VarSet`) is the single source of truth, referenced as `<<Params>>#VarSet.Var`.
Groups: **Face geometry** (FaceDiameter, FaceThickness, BezelWidth, MovementBossDiameter),
**Clearances** (MovementShaftClearance, MountingScrewClearance) + derived holes
(MovementShaftHoleDiameter, MountingScrewHoleDiameter), **Bracket** (BracketWidth/Height/
Thickness), **Walls** (WallThickness), **Markings** (HourMark*, HalfHourMark*, MarkCount).
Full table in `plan.md`. At bootstrap the VarSet is empty; populated during Params migration.

---

## How to verify your change didn't break parametric

After any FreeCAD edit, before considering the task done:

```bash
python3 scripts/audit_parametric.py
```

This script flags:
- Sketches with 0 constraints
- Sketches with dimensional constraints lacking expression bindings
- Sketches attached to feature faces (DAG risk)
- Params variables used nowhere (dead Params)

The script is authoritative. If it reports violations, fix them via a `macros/*.FCMacro` change before saving or committing — never by direct coordinate edits or FCStd XML surgery.

**Documented exemptions** (the corrected Clocks audit already honors these — they will not
appear in its output):
- B-spline `Weight` constraints (Sketcher Type **19**) — control-point weights, not dimensions.
- `Angle` constraints at exactly 90° — perpendicularity expressed as an angle (e.g.
  `ClockFace-lines.Sketch004`), geometric not parametric.
- Inert feature dims — a Pad/Pocket `Length` under `UpToFirst`/`ThroughAll`, or `Length2`
  when not `TwoLengths` — don't affect geometry, so they're not flagged.

> ⚠️ The **canonical** `audit_parametric.py` (copied from the Spade project) has a WRONG
> constraint-type table that mislabels Tangent/Perpendicular/Block as dimensions and misses
> real Radius/Diameter. The **Clocks copy is corrected** (verified against the live Sketcher
> API on 2026-06-04). Do not "sync" the Clocks copy back to the buggy canonical; instead
> propagate the Clocks fix outward.

---

## Memory files (deeper context)

`~/.claude/projects/[encoded-path]/memory/MEMORY.md` indexes the persistent memories for this project. If you're unsure *why* a rule exists, read those files first — they trace each rule to a concrete past incident.

No project-scoped memories yet — this is a fresh project. (Cross-project incident context:
the Spade Connector coordinate-edit saga in the global memory motivates rules #1/#2.)

---

## Workflow notes

**Invariant (apply to every FreeCAD project — do not edit):**

- **MCP server auto-starts with FreeCAD.** If an `mcp__freecad__*` call fails, the right interpretation is "FreeCAD isn't running" — ask whether to launch it. Do **not** silently fall back to `unzip` + XML parsing, and do **not** retry the same MCP call.
- **Write changes as `macros/*.FCMacro` files**, not direct XML edits. Reasons: reviewable, re-runnable, idempotent-friendly, uses FreeCAD's own serialization.
- **Cross-document expressions**: use the canonical form `<<Params>>#VarSet.VarName`. The shorter `<<Params>>.VarName` form sometimes fails with "Params not found."
- **Run `python3 scripts/audit_parametric.py` before committing.** If it reports violations, fix via macro, not by editing FCStd XML.

**Project-specific:**

- FCStd sources live at the project root; there is no `cad/` subdir.
- `ClockFace-number` is the structural reference (XY-flat, datum-attached). When in doubt
  about how blank/lines *should* be built, copy number's pattern.
- Two reorient macros — `macros/reorient_blank_to_xy.FCMacro` and
  `macros/reorient_lines_to_xy.FCMacro` — supersede the bootstrap spec's single stub
  `reorient_blank_lines_to_xy.FCMacro`. Do not derive new SKUs from blank until the reorient runs.
- STL/3MF re-export is deferred until after the reorient is reviewed — existing exports in
  `stl/`/`3mf/` reflect the pre-reorient geometry.

---

## Print profile

**No successful test print yet — profile TBD.**
