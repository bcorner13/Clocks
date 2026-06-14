# Profiles — canonical clock-face base

Home for **`ClockFace.base.3mf`** — the single source of truth that bakes print settings into
every exported face.

## What `ClockFace.base.3mf` is

A Creality Print **project** `.3mf`, saved from a *verified* 3-part face plate (the Roman plate),
containing all three things FreeCAD can't write:

- **print profile** — `Metadata/project_settings.config` (this plate: 0.12 layer, 2 walls, 15%
  infill, Textured PEI, your temps);
- **3-part structure** — dial / bezel / text as parts;
- **slot assignment + assemble** — which part prints in which CFS slot, grouped so they move together.

Because every face variant shares this structure and profile, **one base serves them all.**

## How to create / update it

In Creality Print, open a known-good 3-part plate (Roman is the reference), with the slots
assigned the way you want as defaults, then **File → Save Project As → `Profiles/ClockFace.base.3mf`**.

Re-tuned the profile (e.g. dialed in the holo plate)? Re-save the base from Creality and **every
face inherits the new settings** on its next export. Single source of truth.

This file is **tracked** in git (it's a valuable asset), unlike scratch exports in `archive/`.

## How the export uses it (the injector)

`macros/export_face_multicolor_3mf.FCMacro` will gain a `BASE_3MF` pointer to this file. On export
it:
1. copies this base,
2. swaps in the active face's three meshes (base / bezel / text, matched by order),
3. keeps `project_settings.config`, `model_settings.config`, slots, and assemble untouched,
4. writes `3mf/<DocLabel>.3mf` — opens in Creality already settings-loaded, 3-part, slot-colored.

Same trick as the 2cv001 macro ("reference a base 3MF, swap geometry, keep the rest"), just
multi-part aware. See `docs/superpowers/specs/2026-06-05-print-workflow-and-multicolor-design.md` §8.

## Status

⏳ **Base not saved yet.** The injector is built/verified against the real base once
`ClockFace.base.3mf` exists here — its exact internal structure (one-object-with-parts vs
separate-objects-with-assemble) decides the swap details, so it's developed against the actual file,
not blind.

## Also a candidate home for

Exported slicer **process profiles** (e.g. the days-tuned holo-plate profile) — back them up here or
at a workspace-level `Commercial License/Profiles/` if shared across projects. (Parked.)
