#!/usr/bin/env python3
"""Audit all FCStd files in the project for parametric integrity.

Flags:
  - Sketches with zero constraints (unconstrained geometry)
  - Sketches with dimensional constraints that lack expression bindings
  - Sketches attached to feature faces (DAG-cycle risk)
  - Features with Length/Offset/Radius/etc. set to a literal number rather than an expression

Run from the project root:
    python3 scripts/audit_parametric.py

Exit code 0 = clean. Non-zero = violations found.

Intended for manual pre-commit use. Can also be wired as a pre-commit hook.
"""
import os
import re
import sys
import tempfile
import zipfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Constraint Types that are "dimensional" (i.e. driven by a numeric value).
# Indices from FreeCAD Sketcher source — these need expression bindings.
DIMENSIONAL_TYPES = {
    5: "ParallelDistance",
    6: "DistanceY",
    7: "DistanceX",
    8: "Distance (length)",
    9: "Radius",
    10: "Angle",
    17: "Diameter",
    18: "Weight",
}


def extract_xml(fcstd_path):
    """Return Document.xml contents of the FCStd ZIP."""
    with zipfile.ZipFile(fcstd_path) as z:
        with z.open("Document.xml") as f:
            return f.read().decode("utf-8")


def find_sketches(xml):
    """Return list of sketch names in the document."""
    return re.findall(r'<Object type="Sketcher::SketchObject" name="(\w+)"', xml)


def get_object(xml, name):
    m = re.search(rf'<Object name="{name}"[^/]*(?:Extensions="True")?>.*?</Object>', xml, re.S)
    return m.group(0) if m else None


def audit_sketch(xml, name):
    issues = []
    body = get_object(xml, name)
    if body is None:
        return [f"[internal] cannot find object body for {name}"]

    cl = re.search(r'<ConstraintList count="(\d+)">(.*?)</ConstraintList>', body, re.S)
    ee = re.search(r'<ExpressionEngine count="(\d+)"[^>]*>(.*?)</ExpressionEngine>', body, re.S)
    fc = re.search(r'<Property name="FullyConstrained"[^>]*>\s*<Bool value="(\w+)"', body)
    attach = re.search(r'AttachmentSupport".*?<Link obj="(\w+)" sub="([^"]*)"', body, re.S)

    cl_count = int(cl.group(1)) if cl else 0
    fully = fc.group(1) == "true" if fc else False

    if cl_count == 0:
        issues.append(f"  UNCONSTRAINED: {name} has 0 constraints")
    elif not fully:
        issues.append(f"  UNDERCONSTRAINED: {name} has {cl_count} constraints but FullyConstrained=false")

    # For dimensional constraints, check that they're bound by expression
    if cl:
        # Index of each dimensional constraint
        dim_indices = []
        for idx, c in enumerate(re.finditer(r'<Constrain [^/]*Type="(\d+)"[^/]*/>', cl.group(2))):
            t = int(c.group(1))
            if t in DIMENSIONAL_TYPES:
                dim_indices.append((idx, DIMENSIONAL_TYPES[t]))

        # Which indices have expression bindings?
        bound_indices = set()
        if ee:
            for m in re.finditer(r'<Expression path="Constraints\[(\d+)\]"', ee.group(2)):
                bound_indices.add(int(m.group(1)))

        for idx, tname in dim_indices:
            if idx not in bound_indices:
                issues.append(f"  UNBOUND DIMENSION: {name}.Constraints[{idx}] is {tname} but has no expression binding — value is a literal number")

    # Attachment DAG risk — sketch attached to feature face (Pocket_/Pad_/Body_ + .FaceN)
    if attach:
        obj, sub = attach.group(1), attach.group(2)
        is_datum = "Plane" in obj or "Axis" in obj or "Origin" in obj
        is_feature_face = bool(re.match(r'Face\d+$', sub or ""))
        if is_feature_face and not is_datum:
            issues.append(f"  DAG RISK: {name} attached to feature face {obj}.{sub} — use a datum plane instead")

    return issues


def audit_feature_dimensions(xml):
    """Check Pad/Pocket/Chamfer/Fillet etc. numeric properties for expression bindings."""
    issues = []
    # Objects of interest
    for type_name in ["PartDesign::Pad", "PartDesign::Pocket", "PartDesign::Chamfer", "PartDesign::Fillet"]:
        for name in re.findall(rf'<Object type="{type_name}" name="(\w+)"', xml):
            body = get_object(xml, name)
            if body is None:
                continue
            ee = re.search(r'<ExpressionEngine count="(\d+)"[^>]*>(.*?)</ExpressionEngine>', body, re.S)
            bound_paths = set()
            if ee:
                for m in re.finditer(r'<Expression path="([^"]+)"', ee.group(2)):
                    bound_paths.add(m.group(1))

            # Check each numeric property
            for prop in ["Length", "Length2", "Radius", "Offset", "Size"]:
                p = re.search(rf'<Property name="{prop}"[^>]*>\s*<Float value="([-\d.]+)"', body)
                if p and abs(float(p.group(1))) > 1e-9:
                    if prop not in bound_paths:
                        issues.append(f"  UNBOUND FEATURE DIM: {name}.{prop} = {p.group(1)} has no expression binding")
    return issues


def main():
    fcstd_files = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # skip venv/git/etc
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("venv", "node_modules", "files")]
        for f in files:
            if f.endswith(".FCStd") and not f.endswith(".FCBak"):
                # skip session snapshots
                if "Session-" in f:
                    continue
                fcstd_files.append(os.path.join(root, f))

    total_issues = 0
    for path in sorted(fcstd_files):
        rel = os.path.relpath(path, PROJECT_ROOT)
        try:
            xml = extract_xml(path)
        except Exception as e:
            print(f"[skip] {rel} (unreadable: {e})")
            continue

        file_issues = []
        for name in find_sketches(xml):
            file_issues.extend(audit_sketch(xml, name))
        file_issues.extend(audit_feature_dimensions(xml))

        if file_issues:
            print(f"\n=== {rel} — {len(file_issues)} issue(s) ===")
            for iss in file_issues:
                print(iss)
            total_issues += len(file_issues)
        else:
            print(f"OK  {rel}")

    print(f"\n{'=' * 60}")
    if total_issues == 0:
        print("✓ All files pass parametric audit.")
        return 0
    print(f"✗ {total_issues} parametric issue(s) across project.")
    print("Fix these before considering any geometry task complete.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
