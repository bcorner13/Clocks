# Clocks Project — Bootstrap Design Spec

**Date:** 2026-06-04
**Project:** Clocks
**Status:** Approved — pending implementation plan
**Type:** Retroactive project bootstrap (scaffolding-only; no geometry edits)

---

## Overview

The `Clocks/` folder under `~/Documents/3dPrinting/Commercial License/` already contains five in-progress FCStd files and exported `.stl`/`.3mf` outputs but has none of the structure required by `PROJECT_BOOTSTRAP.md`. This spec defines a retroactive in-place bootstrap that adds the missing scaffolding around the existing CAD files without touching their geometry. Known parametric debt and a known sketch-plane inconsistency are documented for follow-on work, not fixed here.

## Goals

1. Bring `Clocks/` into compliance with `PROJECT_BOOTSTRAP.md` structure.
2. Preserve all existing FCStd files and their `.FCBak` backups; preserve `3mf/` and `stl/` outputs.
3. Run the parametric audit and capture every violation in `WARNINGS.md` as a future-work checklist.
4. Document the known XZ→XY sketch-plane inconsistency between SKUs and stage (but do not run) a reorient macro.
5. Remove only one confirmed duplicate: `ClockFace.FCStd` (duplicate of `ClockFace-blank.FCStd`).
6. Document that no XLinks exist yet between any FCStds — the "live parametric parent" topology is **intended future state**, not current reality.

## Non-goals

- Migrating literal numeric values from existing sketches into `Params.FCStd`.
- Reorienting `ClockFace-blank` or `ClockFace-lines` from XZ_Plane to XY_Plane.
- Wiring up XLinks from `ClockFace-lines` / `ClockFace-number` back to `ClockFace-blank`. (Confirmed by Bradley: no XLinks exist between any FCStds today. The topology in §"Product topology" is the *intended* end state, deferred to follow-on work.)
- Any change to `ClockBracket.FCStd`'s mounting geometry.
- Re-slicing or re-exporting any existing `.stl` / `.3mf`.

## Product topology (intended)

| File | Role | Depends on | Plane at bootstrap |
|---|---|---|---|
| `Params.FCStd` | VarSet — all parametric variables | — | n/a |
| `ClockFace-blank.FCStd` | Parametric **template** for face SKUs; defines disc, bezel, movement boss, mounting interface | `Params.FCStd` | **XZ_Plane** (inconsistent — reorient pending) |
| `ClockFace-lines.FCStd` | SKU: line-style face markings, XLinks to `ClockFace-blank` for base geometry | `Params.FCStd`, `ClockFace-blank.FCStd` | **XZ_Plane** (inconsistent — reorient pending) |
| `ClockFace-number.FCStd` | SKU: numeric face markings, XLinks to `ClockFace-blank` for base geometry | `Params.FCStd`, `ClockFace-blank.FCStd` | **XY_Plane** (target orientation) |
| `ClockBracket.FCStd` | Shared mounting bracket for all face SKUs | `Params.FCStd` | n/a (independent) |

The XLink relationships above describe the **intended** architecture. **No XLinks exist in any current FCStd** (confirmed by Bradley). Every FCStd is currently independent: edits to `ClockFace-blank` do not propagate, and `ClockFace-lines` / `ClockFace-number` carry their own copies of the face base geometry. Wiring up the XLinks is follow-on work.

## intent.md (content to be written verbatim)

```
Goal:
Parametric wall clock product line — one shared mounting bracket and a
parametric face template (ClockFace-blank), with interchangeable face
SKUs (ClockFace-lines, ClockFace-number) XLinked from the template so
common dimensions stay synchronized across the product line.

Constraints:
* Must follow CAD_STANDARDS.md
* Target price $36–$45 per CAD_STANDARDS.md
* K2 Plus build plate (350×350mm); designs must fit
* Standard quartz movement (~6mm shaft) — bracket and face must accommodate
* PLA for test prints; ASA or other engineering plastic for production
* Printable without supports where possible
```

## plan.md (content outline)

**PARAMETERS** — initial set; Bradley refines in follow-on migration.

```
FaceDiameter              App::PropertyLength  — clock face overall OD
FaceThickness             App::PropertyLength
BezelWidth                App::PropertyLength
MovementBossDiameter      App::PropertyLength
MovementShaftHoleDiameter App::PropertyLength  — derived: shaft Ø + MovementShaftClearance
MovementShaftClearance    App::PropertyLength  — slip fit, face-to-shaft
MountingScrewHoleDiameter App::PropertyLength  — derived: screw Ø + MountingScrewClearance
MountingScrewClearance    App::PropertyLength  — bracket-to-wall fastener fit
BracketWidth              App::PropertyLength
BracketHeight             App::PropertyLength
BracketThickness          App::PropertyLength
WallThickness             App::PropertyLength
```

**FEATURE TREE** — documents XLink topology, not feature-by-feature modeling steps (which require post-Params-migration design).

**CONSTRAINT STRATEGY**:
- Every dimensional sketch constraint binds via `setExpression` to `<<Params>>#VarSet.<Var>`.
- Sketches attach to `PartDesign::Plane` datums only — never to feature faces (DAG-cycle risk).
- SKU XLinks reference datum geometry of the parent (`ClockFace-blank`), never feature faces.

**VALIDATION**:
- `python3 scripts/audit_parametric.py` reports clean before any commit.
- Each face SKU prints in PLA before being declared production-ready.

**Planned reorient (XZ → XY)**: described in §"Pending follow-on work" below.

## CLAUDE.md fills (key sections)

- **Headline (project-specific parametric risk):** "Every FCStd in this project is currently independent — no XLinks, no shared Params. Two consequences: (a) common dimensions are duplicated across blank/lines/number/bracket, and changing one will silently desync the others; (b) the immediate parametric debt is literal numbers in sketches. Migrate to Params *before* wiring up XLinks — wiring up first will only propagate the debt."
- **Hard rule #1:** Cite "No prior incident in this project; files predate parametric-rigor bootstrap. Audit-flagged literals (see WARNINGS.md) will be migrated to Params via macros, not coordinate edits."
- **Hard rule #2:** Cite "No prior coordinate-edit incident in this project; rule applies preventively."
- **Hard rule #3:** Cite "ClockFace-lines/number do not yet XLink to ClockFace-blank, but they will. Before XLinks are wired, any sketch in blank that attaches to a feature face (not a datum) must be retargeted to a datum — otherwise the first SKU recompute after wiring will produce a DAG cycle. The audit will flag candidates."
- **Hard rule #4 (clearance Params):** Lists `MovementShaftClearance` and `MountingScrewClearance` as the initial decoupled clearances; explicitly states do **not** overload `WallThickness` to express either.
- **§Project-specific quirks** includes:
  > `ClockFace-blank` and `ClockFace-lines` sketches attach to XZ_Plane; `ClockFace-number` attaches to XY_Plane. Inconsistent. A stub reorient macro at `macros/reorient_blank_lines_to_xy.FCMacro` is staged but **not executed**. Do not derive new face SKUs from `ClockFace-blank` until the reorient runs. See `WARNINGS.md` for full context.
- **Print profile**: "**No successful test print yet — profile TBD.**" (table omitted)
- **Memory files**: "No project-scoped memories yet — this is a fresh project."

## File operations

### Create (copied verbatim from workspace root, no edits)
- `Clocks/CAD_STANDARDS.md`
- `Clocks/MCP_TOOLS_REFERENCE.md`
- `Clocks/tools.md`

### Create (filled with project-specific content)
- `Clocks/CLAUDE.md` — from `CLAUDE_TEMPLATE.md`, every `[FILL: …]` replaced
- `Clocks/intent.md` — content per §intent.md above
- `Clocks/plan.md` — content per §plan.md outline above
- `Clocks/README.md` — overview, SKU table, links to spec
- `Clocks/.gitignore` — `*.FCBak`, `__pycache__/`, `gcode/`, `.DS_Store`
- `Clocks/WARNINGS.md` — captures audit findings + plane-inconsistency note

### Create (copied from canonical reference: `Daytona Coupe/Spade Connector Distribution Block - 4854104/`)
- `Clocks/scripts/audit_parametric.py`

### Create (empty placeholders)
- `Clocks/gcode/.gitkeep`
- `Clocks/images/.gitkeep`
- `Clocks/macros/` directory

### Create (stub macro — not executed)
- `Clocks/macros/reorient_blank_lines_to_xy.FCMacro` — header comment describing intent + a guarded `raise NotImplementedError("Review and uncomment plan body before executing.")`

### Create via FreeCAD MCP (GUI required)
- `Clocks/Params.FCStd` — empty App::VarSet document. Bootstrap macro creates the document, adds an empty `VarSet` object, saves. No properties added yet.

### Delete (after user confirmation in the implementation phase)
- `Clocks/ClockFace.FCStd` — confirmed duplicate of `ClockFace-blank.FCStd`. Bradley confirmed during brainstorm.

### Untouched
- `ClockBracket.FCStd`, `ClockFace-blank.FCStd`, `ClockFace-lines.FCStd`, `ClockFace-number.FCStd`
- All `*.FCBak` files (gitignored, not deleted)
- `3mf/`, `stl/` directories and all contents

### Git + remote (must be part of the bootstrap, not deferred)

The `Clocks/` folder is not a git repo today. Per Bradley's standard, project setup includes remote-repo creation:

1. `git init` inside `Clocks/`.
2. Stage all scaffolding (created files above) + existing FCStds + `stl/` + `3mf/`. **Do not stage** `*.FCBak` (gitignored).
3. First commit with a message summarizing the retroactive bootstrap.
4. Create a **public** GitHub remote (default per Bradley's preference — paid private hosting is avoided).
5. `git push -u origin main`.
6. The spec file at `docs/superpowers/specs/2026-06-04-clocks-bootstrap-design.md` lands in the initial commit alongside everything else.

## Audit + WARNINGS.md plan

After scaffolding is in place but before the bootstrap is declared complete:

1. Run `python3 scripts/audit_parametric.py` against the four kept FCStds.
2. Capture results in `Clocks/WARNINGS.md` with one section per file. For each file, list:
   - Unbound dimensional constraints (literal-numeric debt)
   - Sketches attached to feature faces (DAG risk)
   - Sketches with zero constraints
3. Add a top-level `WARNINGS.md` section titled **"Sketch-plane inconsistency (XZ vs XY)"** describing the issue and pointing to `macros/reorient_blank_lines_to_xy.FCMacro`.
4. Add a top-level `WARNINGS.md` section titled **"No XLinks today — intended topology is aspirational"** stating that every FCStd is currently independent, common dimensions are duplicated, and wiring up XLinks is follow-on work that must happen *after* Params migration (so XLinks propagate Params expressions, not literal-number debt).
5. Update `CLAUDE.md §Files in this project` to mark each FCStd ⚠️ with a count of violations and a one-line summary; cross-reference `WARNINGS.md`.

The bootstrap does **not** fix any audit violation. It only records them.

## Pending follow-on work (out of scope for this bootstrap)

These are deliberately deferred. They are listed so the implementation plan and `WARNINGS.md` can cross-reference them.

1. **Params migration** — populate `Params.FCStd` with the parameters listed in §plan.md and rewrite every literal-numeric sketch constraint in the four FCStds as `<<Params>>#VarSet.<Var>` expressions.
2. **Sketch-plane reorient** — `ClockFace-blank` and `ClockFace-lines` from XZ_Plane to XY_Plane via `macros/reorient_blank_lines_to_xy.FCMacro`, using new `PartDesign::Plane` datums and re-attaching existing sketches. Must run **after** Params migration, so re-anchored sketches use Params expressions, not literals.
3. **XLink wiring** — establish XLinks from `ClockFace-lines` / `ClockFace-number` to `ClockFace-blank` datum geometry. Must run **after** Params migration so the XLinks propagate Params-driven dimensions, not duplicated literals. Order: Params migration → reorient → XLink wiring.
4. **First test print** — produce the print profile table in CLAUDE.md from a real PLA print of `ClockFace-lines` + `ClockBracket`.

## Acceptance criteria

The bootstrap implementation is complete when **all** of the following hold:

- [ ] Every file listed under §"File operations → Create" exists in `Clocks/`.
- [ ] `Clocks/CLAUDE.md` contains zero `[FILL: …]` markers.
- [ ] `Clocks/Params.FCStd` opens in FreeCAD and contains exactly one `App::VarSet` object with no properties.
- [ ] `python3 Clocks/scripts/audit_parametric.py` runs (clean output not required at this stage; violations are expected and documented).
- [ ] `Clocks/WARNINGS.md` lists every audit violation and the plane-inconsistency note.
- [ ] `Clocks/ClockFace.FCStd` no longer exists.
- [ ] `Clocks/macros/reorient_blank_lines_to_xy.FCMacro` exists with header + `NotImplementedError` guard.
- [ ] Git status shows the scaffolding additions; no existing FCStd appears modified.
- [ ] `Clocks/` matches the directory layout mandated by `PROJECT_BOOTSTRAP.md`.
- [ ] `Clocks/` is a git repository with a public GitHub remote and an initial commit containing the scaffolding.

## Risks

- **R1 — Bootstrap reverses a wrong assumption.** Bradley initially indicated "live parametric parent (XLink)"; later confirmed no XLinks exist yet. The spec uses the corrected reality. If any FCStd is found to contain a stray XLink during the audit, treat it as a finding (record in WARNINGS.md) and re-confirm with Bradley before continuing.
- **R2 — `ClockFace.FCStd` is not actually a duplicate.** Bradley confirmed during brainstorm, but the implementation plan should `unzip -t` it and diff against `ClockFace-blank.FCStd` before deletion, just in case. Hold the file aside as a `.FCBak`-named archive if any byte differs in non-trivial ways.
- **R3 — Audit script from Spade has assumptions specific to that project.** If it errors when run against Clocks, fix it in `Clocks/scripts/audit_parametric.py` only — never modify the canonical copy.
