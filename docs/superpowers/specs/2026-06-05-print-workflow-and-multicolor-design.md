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

**Cost / requirements:**
- FreeCAD: accent regions must become **separate bodies/objects**. Tick marks are already their
  own features (easy); the **bezel rim is part of the disc** and would need a split if it's to
  be a separate color.
- Export: FreeCAD alone won't write Creality's per-object slot metadata
  (`model_settings.config` `<metadata key="extruder">`). So the export step needs either a
  **one-time Creality Print template** reused per print, or a **small post-export script** that
  stamps slot assignments onto a multi-object 3MF. (This is the piece worth automating — and
  the same capability the macro lacks.)

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

### 5b. `ClockFace-number.3mf` is missing the numerals — number SKU is unfinished
- The committed `ClockFace-number.3mf` is a **Body-only** geometry export (single bare object,
  ~1440 verts) → numerals excluded.
- In the FCStd the **12 numerals are separate `Part::Extrusion` objects** (group `FcClock001`),
  **not fused into the PartDesign Body**, sitting at **Z 0–2 embedded inside the disc (Z 0–3)**.
  So even exported together they're **buried** — they only read as a **multi-color inlay** (e.g.
  printed face-down, numerals visible on the bottom/front face).
- `Sketch001` "CenterHole" (Ø8) is still **unconsumed** — no movement bore in number.
- **Conclusion:** the number SKU only works *as a multi-color part*. "Fixing the missing
  numbers" = doing the §3 multi-color design for number (numerals as their own color object,
  correctly surfaced), plus consuming the center bore. Not a quick export tweak.

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
3. Modeling: split line-face into body/accent objects (and number into body/numeral objects;
   consume number's bore).
4. Export automation: decide Q6, implement multi-object 3MF with per-object slots.
5. Document the per-project workflow; regenerate the clean deliverables.
