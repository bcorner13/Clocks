# New Clock Face — Workflow (e.g. Roman numerals, fun fonts)

Repeatable recipe to make a new face variant and get a no-painting, 3-color print plate
(dial / bezel / text). Macros live in `macros/` and are symlinked into FreeCAD's Macro menu.

## Steps

1. **Duplicate the template (FreeCAD).**
   Open `ClockFace-number.FCStd`, then **File → Save As → `ClockFace-<variant>.FCStd`**
   (e.g. `ClockFace-roman`). Use Save-As, *never* rename/`mv` the file — that breaks the Params
   cross-document link. Keep `Params.FCStd` open.

2. **Swap the numbers.**
   Delete the existing `FcClock001` group (the 12 numeral `ShapeString` + `Extrusion` objects).
   Run the **FCCircularText** macro with your new font / Roman numerals / characters. Place the
   text ring so it sits on the dial (inside radius ≈ 58.5 = `FaceDiameter/2 − BezelWidth`).
   Extrusion height doesn't matter — the next step re-seats it.

3. **Seat the text proud of the dial.**
   With the new face active, run **`seat_circular_text_proud`** (Macro menu). It lifts every text
   glyph onto the dial face and makes it stand proud by `NumeralReliefHeight` (1.5 mm),
   Params-bound, XY/rotation preserved. Eyeball it, then **save** the FCStd.

4. **Export the multi-color 3MF.**
   With the face active, run **`export_face_multicolor_3mf`** (Macro menu). It writes
   `3mf/ClockFace-<variant>.3mf` as **3 objects**: dial + bezel ring + text. (Bezel split radius
   is auto-read from Params. Set `SPLIT_BEZEL = False` at the top of the macro for a 2-object
   disc+text export instead.)
   *Optional STL for publishing:* export the Body + text fused if you want a single-color STL.

5. **Slice (Creality Print).**
   Open `3mf/ClockFace-<variant>.3mf`. On the **"Multi-part object detected"** prompt → **Yes**
   (loads as one object with parts → they move together AND take per-part filament).
   Assign 3 slots — dial / bezel / text — then **Slice**. No painting.

## Notes
- Steps 3–4 are the two project macros; FCCircularText is a third-party macro you already use.
- The bezel becomes its own color for free because step 4 splits the disc at the bezel radius —
  no slicer paint-by-layer needed.
- Everything stays Params-driven, so changing `FaceDiameter` / `BezelWidth` / `FacePlateThickness`
  / `NumeralReliefHeight` in `Params.FCStd` updates all faces.
- Run `python3 scripts/audit_parametric.py` before committing a face (should stay clean).
