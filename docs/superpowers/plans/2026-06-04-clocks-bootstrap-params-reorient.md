# Clocks: Bootstrap → Params Migration → Reorient — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring `Clocks/` into `PROJECT_BOOTSTRAP.md` compliance, migrate every literal sketch dimension to a central `Params.FCStd` VarSet, then reorient `ClockFace-blank` and `ClockFace-lines` from vertical (disc in XZ, thickness Y) to flat (disc in XY, thickness Z) so they match `ClockFace-number`'s clean datum-attached structure.

**Architecture:** Three sequential phases. (1) Scaffolding is plain file creation copied from the workspace root + canonical Spade reference, plus `git init` and a public GitHub remote. (2) Params migration uses a single reusable binding helper macro driven by a per-sketch mapping table that an inspection task produces from the live FCStds. (3) Reorient re-attaches existing sketches from feature faces onto datum planes via two reviewable macros; mis-placed marking sketches are recreated bound to Params. Every FreeCAD edit is a reviewable, idempotent macro under `macros/`; nothing is saved until a screenshot is approved.

**Tech Stack:** FreeCAD 1.1.1 via the `freecad` MCP server (xmlrpc, GUI up), Python 3.13, `audit_parametric.py`, git + `gh` CLI.

**Source specs:**
- `docs/superpowers/specs/2026-06-04-clocks-bootstrap-design.md` (scaffolding)
- `docs/superpowers/specs/2026-06-04-clockface-reorient-design.md` (reorient)

**Global rules in force (from `~/.claude/CLAUDE.md`):** everything parametric; no raw coordinate edits; sketches on datum planes only; decoupled clearance Params; changes as macros; cross-doc expressions use `<<Params>>#VarSet.VarName`; never auto-save — snapshot to `*.Session-YYYYMMDD.FCStd` before risky edits.

---

## File Structure (created / modified)

**Created — scaffolding (Phase 1):**
- `Clocks/CLAUDE.md` — from root `CLAUDE_TEMPLATE.md`, all `[FILL: …]` replaced
- `Clocks/intent.md`, `Clocks/plan.md`, `Clocks/README.md`, `Clocks/WARNINGS.md`
- `Clocks/.gitignore`
- `Clocks/CAD_STANDARDS.md`, `Clocks/MCP_TOOLS_REFERENCE.md`, `Clocks/tools.md` (verbatim copies)
- `Clocks/scripts/audit_parametric.py` (copy from canonical Spade reference)
- `Clocks/gcode/.gitkeep`, `Clocks/images/.gitkeep`, `Clocks/macros/` (dir)
- `Clocks/Params.FCStd` (empty App::VarSet doc, via macro)

**Created — macros (Phases 2–3):**
- `Clocks/macros/bind_constraints_to_params.FCMacro` (reusable binding helper)
- `Clocks/macros/populate_params_varset.FCMacro` (creates the Param properties)
- `Clocks/macros/reorient_blank_to_xy.FCMacro`
- `Clocks/macros/reorient_lines_to_xy.FCMacro`

**Modified (Phase 2–3, via macros only, saved after approval):**
- `Clocks/ClockFace-blank.FCStd`, `Clocks/ClockFace-lines.FCStd`, `Clocks/ClockFace-number.FCStd`, `Clocks/ClockBracket.FCStd`

**Deleted (after byte-diff confirmation):**
- `Clocks/ClockFace.FCStd` (duplicate of `ClockFace-blank.FCStd`)

---

## Phase 0 — Pre-flight & snapshots

### Task 0.1: Snapshot every FCStd before any edit

**Files:** Create `Clocks/*.Session-20260604.FCStd` for each of the 5 FCStds.

- [ ] **Step 1: Copy each FCStd to a dated session snapshot**

```bash
cd "/Users/bradleycorner/Documents/3dPrinting/Commercial License/Clocks"
for f in ClockFace-blank ClockFace-lines ClockFace-number ClockBracket ClockFace; do
  cp -n "$f.FCStd" "$f.Session-20260604.FCStd"
done
ls *.Session-20260604.FCStd
```
Expected: 5 snapshot files listed.

- [ ] **Step 2: Verify each snapshot is a valid zip (FCStd is a zip)**

```bash
for f in *.Session-20260604.FCStd; do unzip -t "$f" >/dev/null && echo "OK  $f" || echo "BAD $f"; done
```
Expected: 5 lines all `OK`.

> Snapshots are gitignored (`*.Session-*.FCStd` matched by the `.gitignore` in Task 1.5). They are recovery points, not deliverables.

### Task 0.2: Confirm `ClockFace.FCStd` really duplicates `ClockFace-blank.FCStd`

**Files:** read-only inspection.

- [ ] **Step 1: Compare the two documents' object trees and geometry via MCP**

Run (MCP `execute_python`):
```python
import FreeCAD as App, filecmp
docs={d.Name:d for d in App.listDocuments().values()}
blank=docs["ClockFace_blank"]
# ClockFace.FCStd internal name is "ClockFace"? number is also "ClockFace" -> open dup under a temp
import os
p="/Users/bradleycorner/Documents/3dPrinting/Commercial License/Clocks/ClockFace.FCStd"
dup=App.openDocument(p)
def sig(doc):
    out=[]
    for o in doc.Objects:
        rec=(o.Name,o.TypeId)
        out.append(rec)
    bb=doc.getObject("Body").Shape.BoundBox if doc.getObject("Body") and doc.getObject("Body").Shape.Volume>0 else None
    return out,(round(bb.XLength,3),round(bb.YLength,3),round(bb.ZLength,3)) if bb else None
_result_={"dup":sig(dup),"blank":sig(blank)}
```
Expected: identical object lists and bbox dimensions ⇒ confirmed duplicate.

- [ ] **Step 2: Decision gate**

If signatures match: proceed; `ClockFace.FCStd` will be deleted in Task 1.7.
If they differ: STOP, report the difference to Bradley, keep the file, and remove its deletion from Task 1.7.

---

## Phase 1 — Retroactive bootstrap scaffolding

### Task 1.1: Copy verbatim standards files into the project

**Files:** Create `Clocks/CAD_STANDARDS.md`, `Clocks/MCP_TOOLS_REFERENCE.md`, `Clocks/tools.md`.

- [ ] **Step 1: Copy the three standards docs from the workspace root**

```bash
cd "/Users/bradleycorner/Documents/3dPrinting/Commercial License"
for f in CAD_STANDARDS.md MCP_TOOLS_REFERENCE.md tools.md; do cp "$f" "Clocks/$f"; done
ls -la Clocks/CAD_STANDARDS.md Clocks/MCP_TOOLS_REFERENCE.md Clocks/tools.md
```
Expected: 3 files present. These are read-only references — never edited in place.

### Task 1.2: Copy the audit script from the canonical reference

**Files:** Create `Clocks/scripts/audit_parametric.py`.

- [ ] **Step 1: Copy from the Spade Connector canonical project**

```bash
cd "/Users/bradleycorner/Documents/3dPrinting/Commercial License"
mkdir -p Clocks/scripts
cp "Daytona Coupe/Spade Connector Distribution Block - 4854104/scripts/audit_parametric.py" Clocks/scripts/audit_parametric.py
ls -la Clocks/scripts/audit_parametric.py
```
Expected: file present.

- [ ] **Step 2: Run it against the Clocks FCStds to confirm it executes (violations expected)**

```bash
cd "/Users/bradleycorner/Documents/3dPrinting/Commercial License/Clocks"
python3 scripts/audit_parametric.py 2>&1 | tee /tmp/clocks_audit_baseline.txt | tail -40
```
Expected: it runs and prints findings. If it errors on a Clocks-specific assumption, fix it **only in the Clocks copy** (never the canonical) and re-run. Save the baseline output — Phase 1 records it in WARNINGS.md, Phase 2 must clear it.

### Task 1.3: Create the directory placeholders

**Files:** Create `Clocks/gcode/.gitkeep`, `Clocks/images/.gitkeep`, `Clocks/macros/` dir.

- [ ] **Step 1: Make the folders**

```bash
cd "/Users/bradleycorner/Documents/3dPrinting/Commercial License/Clocks"
mkdir -p gcode images macros
touch gcode/.gitkeep images/.gitkeep
ls -d 3mf stl gcode images macros scripts docs
```
Expected: all directories listed (3mf, stl already exist).

### Task 1.4: Write `intent.md`

**Files:** Create `Clocks/intent.md`.

- [ ] **Step 1: Write the file verbatim from the bootstrap spec §intent.md**

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

### Task 1.5: Write `plan.md`, `README.md`, `.gitignore`

**Files:** Create `Clocks/plan.md`, `Clocks/README.md`, `Clocks/.gitignore`.

- [ ] **Step 1: `plan.md`** — copy the PARAMETERS / FEATURE TREE / CONSTRAINT STRATEGY / VALIDATION content from the bootstrap spec §plan.md verbatim, with the corrected plane facts from the reorient spec (number = XY-flat target; blank/lines reorient to match).

- [ ] **Step 2: `README.md`** — project overview, the SKU table (blank template, lines SKU, number SKU, bracket), links to both specs and this plan, and the current orientation status.

- [ ] **Step 3: `.gitignore`**

```gitignore
*.FCBak
*.Session-*.FCStd
__pycache__/
gcode/
.DS_Store
```

### Task 1.6: Fill `CLAUDE.md` from the template

**Files:** Create `Clocks/CLAUDE.md` from `../CLAUDE_TEMPLATE.md`.

- [ ] **Step 1: Copy the template**

```bash
cd "/Users/bradleycorner/Documents/3dPrinting/Commercial License"
cp CLAUDE_TEMPLATE.md Clocks/CLAUDE.md
grep -c "FILL" Clocks/CLAUDE.md
```
Expected: a positive count of `[FILL: …]` markers to replace.

- [ ] **Step 2: Replace every `[FILL: …]` marker** using the bootstrap spec §"CLAUDE.md fills" content, plus the corrected facts: blank & lines currently vertical (reorient pending until Phase 3), number already XY-flat and the structural model to copy; feature-face attachments in blank/lines are the DAG debt to retarget; clearance Params `MovementShaftClearance` + `MountingScrewClearance` decoupled, never overload `WallThickness`. Preserve every "do not edit" invariant section verbatim.

- [ ] **Step 3: Verify no markers remain**

```bash
grep -n "FILL" Clocks/CLAUDE.md || echo "CLEAN: no FILL markers"
```
Expected: `CLEAN: no FILL markers`.

### Task 1.7: Delete the confirmed duplicate

**Files:** Delete `Clocks/ClockFace.FCStd` (only if Task 0.2 confirmed duplicate).

- [ ] **Step 1: Close it in FreeCAD, then remove the file**

Run (MCP `execute_python`): `App.closeDocument("ClockFace")` for the *duplicate* doc only — verify by `.FileName` first so you don't close `ClockFace-number` (which also has internal name `ClockFace`). Then:
```bash
cd "/Users/bradleycorner/Documents/3dPrinting/Commercial License/Clocks"
rm ClockFace.FCStd
ls ClockFace*.FCStd
```
Expected: `ClockFace.FCStd` gone; the `.Session-20260604.FCStd` snapshot of it remains as archive.

### Task 1.8: Create empty `Params.FCStd`

**Files:** Create `Clocks/Params.FCStd` via MCP.

- [ ] **Step 1: Create the VarSet-only document**

Run (MCP `execute_python`):
```python
import FreeCAD as App
doc=App.newDocument("Params")
vs=doc.addObject("App::VarSet","VarSet")
vs.Label="VarSet"
doc.recompute()
doc.saveAs("/Users/bradleycorner/Documents/3dPrinting/Commercial License/Clocks/Params.FCStd")
_result_=[o.Name for o in doc.Objects]
```
Expected: `["VarSet"]`. No properties yet — populated in Phase 2.

### Task 1.9: Initialize git + public remote, first commit

**Files:** `Clocks/.git`, GitHub remote.

- [ ] **Step 1: Init and stage scaffolding (not snapshots/FCBak)**

```bash
cd "/Users/bradleycorner/Documents/3dPrinting/Commercial License/Clocks"
git init
git add CLAUDE.md intent.md plan.md README.md WARNINGS.md .gitignore \
  CAD_STANDARDS.md MCP_TOOLS_REFERENCE.md tools.md \
  scripts/ macros/ docs/ gcode/.gitkeep images/.gitkeep \
  Params.FCStd ClockBracket.FCStd ClockFace-blank.FCStd ClockFace-lines.FCStd ClockFace-number.FCStd \
  3mf/ stl/
git status --short
```
Expected: staged scaffolding + FCStds + outputs; **no** `*.FCBak` or `*.Session-*` staged.

- [ ] **Step 2: Commit**

```bash
git commit -m "Retroactive bootstrap: scaffold Clocks project per PROJECT_BOOTSTRAP.md

Adds CLAUDE.md, intent/plan/README/WARNINGS, standards copies, audit script,
empty Params.FCStd, and directory layout around existing in-progress FCStds.
Geometry untouched. Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 3: Create the public remote and push**

```bash
cd "/Users/bradleycorner/Documents/3dPrinting/Commercial License/Clocks"
gh repo create Clocks --public --source=. --remote=origin --push
git remote -v
```
Expected: `origin` set to the new public GitHub repo; `main` pushed. (Public per Bradley's default.)

### Task 1.10: Phase-1 checkpoint

- [ ] **Step 1: Verify bootstrap acceptance**

```bash
cd "/Users/bradleycorner/Documents/3dPrinting/Commercial License/Clocks"
for d in 3mf stl gcode images macros scripts docs; do [ -d "$d" ] && echo "dir OK $d"; done
for f in CLAUDE.md intent.md plan.md README.md WARNINGS.md .gitignore Params.FCStd \
  CAD_STANDARDS.md MCP_TOOLS_REFERENCE.md tools.md scripts/audit_parametric.py; do [ -e "$f" ] && echo "file OK $f" || echo "MISSING $f"; done
grep -q FILL CLAUDE.md && echo "FAIL: FILL remains" || echo "CLAUDE clean"
```
Expected: all `OK`, `CLAUDE clean`, no `MISSING`. **STOP and report to Bradley before Phase 2.**

---

## Phase 2 — Params migration

> Reusable approach: one binding helper consumes a per-sketch mapping `{constraintName: ParamName}`. The mapping is produced by an inspection task per FCStd, then reviewed, then applied. Derived Params (e.g. hole Ø = shaft Ø + clearance) are set as expressions inside the VarSet itself.

### Task 2.1: Inspect every dimensional constraint across the four FCStds

**Files:** read-only.

- [ ] **Step 1: Dump named + unnamed dimensional constraints per sketch**

Run (MCP `execute_python`) for each of `ClockFace_blank`, `ClockFace_lines`, `ClockFace`(=number), `ClockBracket`:
```python
import FreeCAD as App
doc=App.getDocument("ClockFace_blank")  # repeat per doc
rows=[]
for o in doc.Objects:
    if o.TypeId!="Sketcher::SketchObject": continue
    for i,c in enumerate(o.Constraints):
        if c.Type in ("Distance","DistanceX","DistanceY","Radius","Diameter","Angle"):
            rows.append((o.Name,i,c.Name or "(unnamed)",c.Type,round(float(c.Value),4)))
_result_=rows
```
Expected: a table of (sketch, index, name, type, value). **Output of this task is the raw material for the mapping in Task 2.2.**

### Task 2.2: Author the Param set + mapping table

**Files:** update `Clocks/plan.md` (Params section), create the mapping used by Task 2.4.

- [ ] **Step 1: Define the VarSet Params** — start from the bootstrap spec list and extend to cover every distinct dimension found in Task 2.1. Initial set (App::PropertyLength unless noted):

```
FaceDiameter, FaceThickness, BezelWidth,
MovementBossDiameter, MovementShaftClearance,
MovementShaftHoleDiameter   (= MovementBossDiameter or shaft Ø + MovementShaftClearance — set as VarSet expression),
MountingScrewClearance, MountingScrewHoleDiameter (derived expression),
WallThickness,
BracketWidth, BracketHeight, BracketThickness,
HourMarkLength, HourMarkWidth, HourMarkPadHeight (=1.0),
HalfHourMarkLength, HalfHourMarkWidth, HalfHourMarkPadHeight (=0.5),
MarkCount (App::PropertyInteger, =12)
```
Add/rename to match Task 2.1 reality — one Param per distinct concept (global rule: one knob, one concern). Name unnamed driving constraints in the sketch first (so binding targets a stable name, not an index).

- [ ] **Step 2: Write the mapping table** `{(doc, sketch, constraintName): ParamName}` into a comment block at the top of `bind_constraints_to_params.FCMacro` (Task 2.3) so the binding is reviewable and re-runnable.

### Task 2.3: Write the reusable binding helper macro

**Files:** Create `Clocks/macros/bind_constraints_to_params.FCMacro`.

- [ ] **Step 1: Write the idempotent helper**

```python
# bind_constraints_to_params.FCMacro
# Binds named sketch constraints to <<Params>>#VarSet.<Param> expressions.
# Idempotent: re-running re-asserts expressions; never appends.
import FreeCAD as App

PARAMS_DOC = "Params"  # internal name of Params.FCStd once open

# MAPPING: (docName, sketchName, constraintName) -> ParamName
MAPPING = {
    # filled from Task 2.2, e.g.:
    # ("ClockFace_blank","Sketch","FaceDia"): "FaceDiameter",
}

def ensure_param(vs, name, ptype="App::PropertyLength", group="Clock", doc="auto"):
    if name not in vs.PropertiesList:
        vs.addProperty(ptype, name, group, doc)

def run():
    if PARAMS_DOC not in [d.Name for d in App.listDocuments().values()]:
        App.openDocument("/Users/bradleycorner/Documents/3dPrinting/Commercial License/Clocks/Params.FCStd")
    vs = App.getDocument(PARAMS_DOC).getObject("VarSet")
    for (dn, sn, cn), pname in MAPPING.items():
        doc = App.getDocument(dn); sk = doc.getObject(sn)
        ensure_param(vs, pname)
        # bind constraint -> Param
        sk.setExpression(f"Constraints.{cn}", f"<<Params>>#VarSet.{pname}")
        doc.recompute()
    App.getDocument(PARAMS_DOC).recompute()
    print("bound", len(MAPPING), "constraints")

run()
```
> `setExpression("Constraints.<Name>", ...)` requires the constraint to be **named**. Task 2.2 Step 1 names any unnamed driving constraint first.

### Task 2.4: Populate the VarSet with real values, then bind

**Files:** Create `Clocks/macros/populate_params_varset.FCMacro`; modify `Params.FCStd` + the four FCStds (in memory; saved in Task 2.6).

- [ ] **Step 1: Write `populate_params_varset.FCMacro`** that `addProperty` each Param (idempotent skip if present), sets its value from Task 2.1's measured numbers, and sets derived Params via `vs.setExpression("MovementShaftHoleDiameter", "...")` etc.

- [ ] **Step 2: Run populate, then run the binding helper**

Run both macros via MCP `execute_python` (exec file contents) or the Macro UI. After each, `recompute` the affected docs.

- [ ] **Step 3: Verify no geometry moved**

For each of the four FCStds, compare `Body.Shape.BoundBox` (XLength/YLength/ZLength rounded to 3dp) before (Task 2.1 era) and after binding.
Expected: **identical bboxes** — binding replaces literals with equal-valued expressions, so geometry must not move. Any change ⇒ a wrong Param value; fix before continuing.

### Task 2.5: Run the audit — must be clean

- [ ] **Step 1: Re-run audit**

```bash
cd "/Users/bradleycorner/Documents/3dPrinting/Commercial License/Clocks"
python3 scripts/audit_parametric.py 2>&1 | tee /tmp/clocks_audit_postparams.txt | tail -40
```
Expected: zero unbound dimensional constraints across blank/lines/number/bracket. (Feature-face DAG warnings on blank/lines may remain — those are cleared in Phase 3.) If unbound dims remain, extend MAPPING and re-run Task 2.4.

### Task 2.6: Save + commit Params migration

- [ ] **Step 1: Save all modified docs (only after Step 2.4.3 bbox check passes)**

Run (MCP): `App.getDocument(name).save()` for Params + the four FCStds.

- [ ] **Step 2: Commit**

```bash
cd "/Users/bradleycorner/Documents/3dPrinting/Commercial License/Clocks"
git add Params.FCStd ClockFace-blank.FCStd ClockFace-lines.FCStd ClockFace-number.FCStd ClockBracket.FCStd macros/ plan.md WARNINGS.md
git commit -m "Params migration: central VarSet + bind literal constraints to <<Params>>

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 3: Phase-2 checkpoint — STOP and report to Bradley before Phase 3.**

---

## Phase 3 — Reorient blank & lines to XY-flat

> Per reorient spec. Re-attach existing (now Params-bound) sketches from feature faces onto datum planes, matching `ClockFace-number`. Recompute and screenshot after each step; recreate a marking sketch (bound to Params) only if re-attach mis-places it. **No save until Bradley approves the screenshot.**

### Task 3.1: Capture number's exact target attachment recipe

**Files:** read-only.

- [ ] **Step 1: Record number's base `Sketch` MapMode/AttachmentSupport/placement and `Sketch001` (XY_Plane) details** via MCP, so blank/lines are re-attached to the identical configuration.
Expected: a concrete target spec (base sketch → XZ_Plane with number's MapMode; pocket sketch → XY_Plane datum).

### Task 3.2: Write & run `reorient_blank_to_xy.FCMacro`

**Files:** Create `Clocks/macros/reorient_blank_to_xy.FCMacro`; modify `ClockFace-blank.FCStd` in memory.

- [ ] **Step 1: Write the idempotent macro** that:
  1. re-attaches `Sketch` (base profile): `AttachmentSupport=[(XZ_Plane,'')]`, `MapMode` per Task 3.1;
  2. re-attaches `Sketch001` (movement pocket): `AttachmentSupport=[(XY_Plane,'')]`, `MapMode='FlatFace'`/`ObjectXY` per number;
  3. `doc.recompute()` and reports any error objects.

- [ ] **Step 2: Run it; recompute; assert orientation**

Run (MCP). Then check:
```python
bb=App.getDocument("ClockFace_blank").getObject("Body").Shape.BoundBox
_result_={"dx":round(bb.XLength,2),"dy":round(bb.YLength,2),"dz":round(bb.ZLength,2),
          "zmin":round(bb.ZMin,2),"zmax":round(bb.ZMax,2),
          "errs":[o.Name for o in App.getDocument("ClockFace_blank").Objects if o.State and 'Error' in str(o.State)]}
```
Expected: `dz≈3` (thickness now along Z), disc spans X & Y (`dx≈dy≈120`), `errs` empty. If the disc built on −Z, set `Revolution.Reversed`/`Pocket.Reversed` and recompute.

- [ ] **Step 3: Screenshot for review**

MCP `get_screenshot` (Isometric + Top). Present to Bradley. **Do not save until approved.**

- [ ] **Step 4: On approval, save**

Run (MCP): `App.getDocument("ClockFace_blank").save()`.

### Task 3.3: Write & run `reorient_lines_to_xy.FCMacro`

**Files:** Create `Clocks/macros/reorient_lines_to_xy.FCMacro`; modify `ClockFace-lines.FCStd` in memory.

- [ ] **Step 1: Write the macro** — same base+pocket re-attach as blank, then re-attach `Sketch002` (Hours) and `Sketch004` (HalfHour) from `Pocket.Face5` → `XY_Plane` datum (or a `PartDesign::Plane` datum offset to the face surface if the markings must sit on the visible face). Recompute the full tree.

- [ ] **Step 2: Run; recompute; assert orientation + patterns intact**

```python
d=App.getDocument("ClockFace_lines"); bb=d.getObject("Body").Shape.BoundBox
_result_={"dz":round(bb.ZLength,2),"dx":round(bb.XLength,2),"dy":round(bb.YLength,2),
          "pp":[ (o.Name,o.Occurrences) for o in d.Objects if o.TypeId=="PartDesign::PolarPattern"],
          "errs":[o.Name for o in d.Objects if o.State and 'Error' in str(o.State)]}
```
Expected: `dz≈3`, disc in XY, both polar patterns present with `Occurrences=12`, `errs` empty.

- [ ] **Step 3: Marking fallback (recreate) if mis-placed**

If a screenshot shows Hours/HalfHour off the face, not centered, or not radial: recreate that sketch on the datum to reproduce the original geometry (segment count + lengths from Task 2.1 / reorient spec), binding each dimension to its `<<Params>>` Param (Params already exist from Phase 2 — no literals). Re-pad and re-pattern. Recompute.

- [ ] **Step 4: Screenshot (Top + Isometric) for review.** **No save until approved.**

- [ ] **Step 5: On approval, save** `ClockFace-lines.FCStd`.

### Task 3.4: Final audit — no feature-face attachments remain

- [ ] **Step 1: Re-run audit + an explicit feature-face check**

```bash
cd "/Users/bradleycorner/Documents/3dPrinting/Commercial License/Clocks"
python3 scripts/audit_parametric.py 2>&1 | tail -40
```
Plus (MCP) assert no sketch in blank/lines has an `AttachmentSupport` pointing at a `Revolution`/`Pocket`/`Pad` face.
Expected: audit clean of unbound dims AND of feature-face DAG flags for blank/lines.

### Task 3.5: Update WARNINGS.md / CLAUDE.md, commit

- [ ] **Step 1: Update docs** — mark blank & lines as datum-attached + XY-flat (orientation inconsistency resolved); leave XLink wiring as the sole remaining follow-on. Note the two real reorient macros supersede the bootstrap spec's stub.

- [ ] **Step 2: Commit**

```bash
cd "/Users/bradleycorner/Documents/3dPrinting/Commercial License/Clocks"
git add ClockFace-blank.FCStd ClockFace-lines.FCStd macros/ WARNINGS.md CLAUDE.md
git commit -m "Reorient blank & lines to XY-flat; retarget sketches to datums

Matches ClockFace-number structure; removes feature-face DAG debt.
Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
git push
```

- [ ] **Step 3: Final report to Bradley** — orientation done; remaining follow-on = XLink wiring + (deferred) STL/3MF re-export.

---

## Self-Review

**Spec coverage:**
- Bootstrap spec file-ops, git+remote, duplicate deletion, empty Params.FCStd, audit→WARNINGS → Phase 1 + Task 2.5/3.4. ✓
- Reorient spec: re-attach-in-place, datum targets, marking recreate-fallback bound to Params, snapshots, no-save-until-approved, exports deferred → Phase 0.1 + Phase 3. ✓
- Ordering (Params → reorient) → Phases 2 then 3. ✓
- Decoupled clearance Params (MovementShaftClearance, MountingScrewClearance) → Task 2.2. ✓

**Placeholder scan:** The only deliberately data-dependent content is the Params↔constraint MAPPING, which Task 2.1 (inspection) produces and Task 2.2 authors before Task 2.3/2.4 consume it — a real task chain, not a TODO. All file paths, git commands, and verification asserts are concrete.

**Type/name consistency:** macro filenames, doc internal names (`ClockFace_blank`, `ClockFace_lines`, `ClockFace`=number, `ClockBracket`), and Param names are used consistently across tasks. Note `ClockFace-number.FCStd` opens under internal name `ClockFace`; the duplicate `ClockFace.FCStd` shares that internal name — Task 1.7 Step 1 disambiguates by `.FileName` before closing.

**Open risk carried into execution:** whether markings re-attach cleanly vs. need recreate (Task 3.3 Step 3) is only knowable at runtime; both branches are specified.
