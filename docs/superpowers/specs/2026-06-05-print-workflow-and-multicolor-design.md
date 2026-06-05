# Print Workflow & Multi-Color — Design Notes

**Date:** 2026-06-05
**Project:** Clocks (several items are workspace-wide candidates — flagged inline)
**Status:** Ideas captured from working session — NOT yet an approved implementation spec
**Type:** Workflow design + modeling direction + bug findings

---

## Why this doc

Capturing the print-pipeline thinking from the 2026-06-05 session so it isn't trapped in
chat (or in unsaved slicer state). Covers: the deliverable model, print-profile reuse,
multi-color strategy, where the 2cv001 macro fits, and two real defects found in the existing
3MFs. Nothing here is built yet; open decisions are listed at the end.

---

## 1. Deliverable model (per printable body)

- **STL** — pure geometry. For publishing (Creality Cloud etc.) and as the import seed.
  FreeCAD owns it; we already export at 0.01 mm deflection (watertight/manifold).
- **Profile 3MF(s)** — a 3MF only carries a print profile if it is a **slicer *project*** 3MF
  (settings live in `Metadata/project_settings.config`). FreeCAD cannot bake a profile in — it
  only writes meshes. So each profile-3MF is produced/owned in **Creality Print**, seeded from
  the STL.
- Shape of it: **per body → 1 STL + N profile-3MFs** (one per target plate). The 3MF doubles
  as a publish artifact (modern format, carries color).

**Suggested layout** (scales to N profiles without name collisions):
```
stl/  ClockFace-lines.stl                 ← geometry / publish
3mf/holoplate/  ClockFace-lines.3mf       ← Creality project, Holo profile
3mf/standard/   ClockFace-lines.3mf       ← Creality project, standard plate
```
**Workspace-wide candidate:** promote this deliverable convention into `PROJECT_BOOTSTRAP.md`.

---

## 2. Print profiles (reuse)

- A tuned profile is fully reusable across **all** projects and **any** object count
  (single part or assembly) — it's geometry-independent.
- **The holo-plate profile is high-value IP** (days of tuning) and currently lives only inside
  one Creality Print install. Two actions:
  1. Save it as a **named Process preset** → appears in every project's process dropdown.
  2. **Export it to a file** (Creality Print preset export / config bundle) and store it in a
     version-controlled home so it survives reinstalls/machines.
- **Proposed home (workspace-wide):** `Commercial License/Profiles/` with
  `Holo-K2Plus.json` etc. + a `README.md` documenting export/import + naming.
- Holo behavior is encoded in the Process settings (first layer, bottom-surface pattern, plate
  temp, flow) on the chosen bed type — confirm whether Creality Print exposes a dedicated
  "holographic" bed type or it's tuned on Textured-PEI. (Open Q1.)

---

## 3. Multi-color strategy — the core idea

**Problem:** the proven black-face / red-tick clock was colored with **paint-by-layer** in the
slicer. That is a per-project **manual step that does not survive a geometry re-export** —
re-import an updated STL and the paint is gone. Goal: eliminate that step.

**Target approach — color = geometry, assigned per object:**
- Make each color region its **own object** so the slicer assigns filament **per object**
  automatically. Per-object assignment is the most portable form — survives re-export, is what
  a base/template 3MF remembers, needs zero painting. Open the plate → confirm CFS slot per
  object → slice.
- For the line face that means exporting **two objects**:
  - **body** (disc + dial) → base-color slot
  - **accents** (tick marks; rim too if desired) → accent-color slot
  - plus **bracket** → its slot
- This single direction solves three things at once:
  1. kills paint-by-layer (color is geometry, not a slicer action),
  2. *is* the multi-color assembly plate,
  3. is exactly the multi-body export the stock macro can't do (§4).

**Cost / requirements — and the two SKUs sit at opposite ends:**
- **`number` is already structured right.** Its 12 numerals are **separate `Part::Extrusion`
  objects**, not fused into the Body. That's exactly the per-object color structure we want:
  include them in the export and assign disc→base / numerals→accent. (The only reason
  `ClockFace-number.3mf` looked broken is a Body-only export dropped them — §5b.)
- **`lines` is the one needing surgery.** Its tick markings are **PartDesign Pads/PolarPatterns
  fused into the single Body** — that's *why* it exported cleanly as one solid, but it means a
  second color requires **un-fusing / splitting the tick volumes back out** into their own
  object (e.g. a separate body, or isolate the pad volumes). Real work, more than number.
- **The bezel rim** (on both face SKUs) is part of the disc revolve; making *it* a separate
  color would need its own split. (Open Q2 decides whether we go there.)
- **Export — VERIFIED 2026-06-05 on `ClockFace-number`:**
  - The **GUI File→Export** path rejects loose Part objects / groups ("no body selected") — this
    is a GUI-command guard, *not* a FreeCAD limit.
  - **Scripting `Mesh.export()` exports anything with a shape** — tested OK on the Body, a single
    numeral `Part::Extrusion`, the `FcClock001` group, and Body+all-numerals.
  - **It keeps objects SEPARATE in 3MF (does not merge):** `Mesh.export([Body]+12 numerals,
    .3mf)` → a 3MF with **13 objects / 13 meshes / 13 build-items**. (STL, by contrast, merges
    everything into one mesh.) So a **multi-object 3MF straight from FreeCAD scripting is the
    mechanism** — fuse the 12 numerals into one accent object → export `[disc, numerals]` → clean
    2-object 3MF.
  - The **only** thing FreeCAD won't write is Creality's per-object **slot** metadata
    (`model_settings.config` `<metadata key="extruder">`). So slot mapping is set once in a
    **Creality Print template**, or **stamped by a small post-export script**. (This is the piece
    worth automating — and the capability the single-body macro lacks.)

**VALIDATED end-to-end (2026-06-05, Creality Print).** The FreeCAD-generated multi-object 3MF
(`~/Downloads/ClockFace-number-PROOF.3mf`) opened in Creality Print as **13 separate objects**;
disc → slot 1 (orange), numerals → slot 3 (red) assigned per object; renders correctly with the
numerals **~1–2 mm proud** (raised relief, *not* engraved — earlier guess corrected). So
FreeCAD → multi-object 3MF → per-object color is **proven**.

**New requirement found in the same test — objects must be ASSEMBLED.** The 13 objects are
independent, so moving the disc leaves the numerals behind, and overlapping objects raise a
"too close / collisions" warning. Fix has two parts:
1. **Fuse the 12 numerals into one accent object** → clean **2-object** plate (disc + numerals).
2. **Mark as an assembly** so they move as one unit — in a Creality/Bambu 3MF this is the
   `<assemble><assemble_item …>` block in `model_settings.config` (present in `Clock.3mf`).
   FreeCAD won't write it → either a one-time "Assemble" in Creality Print, or the export-stamp
   script writes it.

**FULLY VALIDATED (2026-06-05) — the clean 2-object `3mf/ClockFace-number.3mf`.** Opened in
Creality Print → it prompts **"Multi-part object detected … load as a single object with
multiple parts?"** → **Yes**. Result: one object `ClockFace-number` with two **parts**
(`Object_1` disc, `Object_2` text), each assigned its own filament slot, **moving together as a
unit**, numerals proud and crisp on the dial. So the full chain works:
`build → FCCircularText → seat_circular_text_proud → export_face_multicolor_3mf →
Creality Print "multi-part: Yes" → assign 2 slots → slice` — no painting, no manual assemble.

**Key consequence — the `<assemble>` block is NOT needed.** Creality Print's multi-part import
does the grouping *and* per-part coloring on load. So:
- **Workflow as-is** needs zero stamping; the only manual step is assigning the 2 slots after import.
- **Optional stamp script** would only **pre-assign the 2 slots** (`model_settings.config`
  `<metadata key="extruder">` per object) to remove that one step — it does **not** need to write
  `<assemble>`. (Earlier "stamp must write `<assemble>`" is superseded.)

The reusable export tool is `macros/export_face_multicolor_3mf.FCMacro`; the seat-proud tool is
`macros/seat_circular_text_proud.FCMacro`.

**Open Q2:** accent = **ticks only**, or **ticks + rim**? (Decides whether we touch the bezel.)
**Open Q3:** confirm the target mental model is "color = separate objects, one slot each, no
painting ever." (Working assumption: yes.)

---

## 4. The 2cv001 "3D Printer 3mf Workflow" macro — role & limits

Macro: `~/Library/Application Support/FreeCAD/v1-1/Macro/3D_Printer_3mf_Workflow.FCMacro`
(Apache-2.0). It injects FreeCAD's fresh mesh into a **base 3MF that already carries slicer
settings**, preserving all settings files → outputs a project 3MF with the profile **baked in**,
and can launch the slicer.

- **This is how FreeCAD can emit a profile-bearing 3MF** (via the "3MF file for print
  parameters" field = a profile template). Exactly the §1/§2 deliverable for single parts.
- **"Old version / only the object" issue = the fallback path**, not a bug: with no compatible
  base 3MF it writes a bare, namespace-less core 3MF (`build_model_xml`, ~line 945) that Orca/
  Creality imports as a plain object. **Fix = feed it a Creality-Print-made base 3MF** (and set
  `slicer_exe` to Creality Print; default is QIDI Studio). Mismatched base-vs-target slicer
  triggers an "incompatible slicer" fallback to the same bare file (~line 2387).
- **Hard limit — single body** (line 1911 `if len(selection) > 1: … "Multiple selection not
  supported."`). So the macro is good for **single-part profile 3MFs only**. It **cannot** build
  the multi-color / multi-part plate. Assemblies → Creality Print, or a macro modification.

**Decision (working):** use the macro for single-part profile 3MFs; do **not** rely on it for
multi-color assemblies. If we automate multi-object color export, build it ourselves (§3) rather
than fight the macro's single-body design.

---

## 5. Defects found in existing 3MFs (2026-06-05)

### 5a. `Clock.3mf` does not contain the recipe that printed the photo
The committed `3mf/Clock.3mf` is an **early save**: both objects on slot 4 (black), **no paint
data**, `custom_gcode_per_layer.xml` has the `MultiExtruder` flag but **zero actual color
changes**, mesh has no segmentation. It also still holds the **old vertical** line-face geometry.
The good two-color result lives only in an **unsaved Creality Print session**. Action: re-save/
export the good project from Creality Print over the stale file before reusing it as a template.

### 5b. `ClockFace-number.3mf` is missing the numerals — they're not in the Body
- The numerals **are correct, visible geometry** on the dial face (confirmed in the FreeCAD
  view). Earlier "buried" call was **wrong** — corrected here.
- They are **12 separate `Part::Extrusion` objects** (group `FcClock001` + `Comp_Arabic001`/
  `Shape001`), **not part of the PartDesign `Body`**. The committed `ClockFace-number.3mf` is a
  **Body-only export** (single bare object, ~1440 verts), so it omits them → "numbers missing."
- Number's center **bore is now consumed** (`Body` tip = `Pocket`, UpToFirst, Reversed) — so the
  earlier "unconsumed bore" note is outdated.
- **Fix:**
  - *Single-color:* export `Body` **+ the numeral objects** together (not Body-only) and the
    numbers come through.
  - *Multi-color (preferred):* the numerals being a **separate object** is exactly what §3 wants
    — assign disc→base slot, numerals→accent slot. So **number is already well-structured for
    multi-color**, it just needs the export to (a) include the numerals and (b) ideally collapse
    the 12 extrusions into one "numerals" object with the accent slot baked in.
- So this is **not** a quick "the SKU is broken" — the geometry is fine; it's the same
  per-object multi-color export need as the line face (§3).

---

## 6. Open decisions

- **Q1** — Holo: dedicated bed type in Creality Print, or tuned on Textured-PEI? (doc detail)
- **Q2** — Accent color = ticks only, or ticks + rim? (bezel split or not)
- **Q3** — Confirm target model: "color = separate objects, one slot each, no painting."
- **Q4** — Promote the deliverable layout (§1) + `Profiles/` home (§2) to `PROJECT_BOOTSTRAP.md`
  (workspace-wide), or keep Clocks-local for now?
- **Q5** — Number SKU: redesign now (numerals as color object + consume bore), or defer?
- **Q6** — Multi-object color export: one-time Creality Print template vs. a post-export
  slot-stamping script (or a forked multi-body macro)?

## 7. Sequencing (proposed, once decisions land)

1. Rescue assets: re-save good `Clock.3mf` from Creality Print; export + back up the Holo
   profile into `Profiles/`.
2. Confirm the color split (Q2/Q3) and the deliverable/standards scope (Q4).
3. Modeling: **number** is mostly there (numerals already separate, bore already consumed) —
   just collapse the 12 numeral extrusions into one accent object and include it in the export.
   **lines** needs the real work — un-fuse the tick volumes from the Body into a separate accent
   object.
4. Export automation: decide Q6, implement multi-object 3MF with per-object slots.
5. Document the per-project workflow; regenerate the clean deliverables.
