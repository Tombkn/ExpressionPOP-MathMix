# Changelog

## 1.6 (2026-08-30)

Fixes

- Component targets: `P.y = ...`, `Color.a = ...`, `C[0] = ...` compiled to `P.y[id]` and never
  allocated `P` for writing (`'P' : undeclared identifier`). The left side is now split into name and
  component (`P[id].y`), and the generator fills the Output Attributes of `glsl1` itself instead of
  the stock parameter expression, which took `P.y` as the attribute name.
- Array functions: `arrayadd`, `arraymult`, `arrayavg`, `arraymin`, `arraymax` returned 0 for every
  point except the first. The helper used the two-argument accessor `TDIn_X(id, i)`, which reads
  input number `id`; it now uses `TDIn_X(0u, id, i)`.

New

- Explicit width for a new attribute: `vec3 offset = P - _BoundsCenterP` (type in front of the name,
  OutAttr mode, same spelling as a Local line). Without a type the width is still guessed from the
  right side: `vec3(...)` gives 3, anything else 1.
- A new attribute written by component (`foo.z = 1.0`) is declared wide enough for that component.
- `selftest` DAT inside the component: the line from SELFTEST.md, ready to copy.
- `readme` / `readme_de` DATs inside the component match README.md / README_DE.md in this folder.
- Documented: values from a parameter or CHOP go in as a uniform on the Vectors page of `glsl1`.

Verified in TouchDesigner 2025.32820 with a Point Generator POP (10 points) and an Attribute POP
adding `Color`, `Age` and `Weights[4]`: every README example, the self-test line (all zeros on every
point), the array functions on every point, typed and component targets, the OutAttr/Local toggle.

## 1.5

- Toggling OutAttr -> Local -> OutAttr left a stale `cannot convert from 'vec4' to 'float'` error.
  A deferred cook after a changed attribute declaration clears it.

## 1.4

- New attributes are created from the expression alone (`myval = _PointU * 5.0`): the generator
  declares them on the GLSL POP, width inferred from the right side.

## 1.0 to 1.3

- Math Mix function library (`src/mathmix_lib.glsl`) prepended to the generated shader without
  showing up in View = code, parser tolerant to `==` / `>=` / `<=` / `!=`, `// comments` and a
  trailing `;`, `_` built-ins mapped to their GLSL POP equivalents, array helpers generated per
  attribute, `#line 1` so error line numbers match View = code.
