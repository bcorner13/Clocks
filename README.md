# Clocks

Parametric wall-clock product line for FreeCAD 1.1 → FDM print. One shared mounting bracket
and a parametric face template with interchangeable face SKUs.

## Product line

| File | Role | Orientation | Notes |
|---|---|---|---|
| `ClockFace-blank.FCStd` | Parametric **template** for face SKUs (disc + movement pocket) | XZ-vertical → reorient pending | base for lines/number |
| `ClockFace-lines.FCStd` | SKU: line/tick face markings (Hours ×12, HalfHour ×12) | XZ-vertical → reorient pending | |
| `ClockFace-number.FCStd` | SKU: numeric face markings | **XY-flat (target)** | clean datum-attached model |
| `ClockBracket.FCStd` | Shared wall mounting bracket | independent | |
| `Params.FCStd` | Central VarSet — all parametric variables | n/a | `<<Params>>#VarSet.Var` |

## Status (2026-06-04)

Retroactively bootstrapped to `PROJECT_BOOTSTRAP.md`. Geometry is in progress; `number` is
furthest along (exported STL/3MF). Known parametric debt and the orientation inconsistency
are tracked in [`WARNINGS.md`](WARNINGS.md).

**Roadmap:** Params migration → reorient blank & lines to XY-flat → XLink wiring → first PLA
test print (print profile TBD).

## Layout

- FCStd sources at root; `3mf/` + `stl/` tracked deliverables; `gcode/` regenerable (gitignored).
- `macros/` reviewable FreeCAD macros; `scripts/audit_parametric.py` parametric audit.
- `docs/superpowers/specs/` design specs; `docs/superpowers/plans/` execution plan.

## Standards

Inherits the workspace standards (`CAD_STANDARDS.md`, `PROJECT_BOOTSTRAP.md`,
`MCP_TOOLS_REFERENCE.md`, `tools.md`) and the global parametric rules in `~/.claude/CLAUDE.md`.
Run `python3 scripts/audit_parametric.py` before committing any geometry milestone.
