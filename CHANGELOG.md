# Changelog

## 1.9.1 (2026-10-01)

- **An empty extra connector now really reads `0.0`.** The one-point stand-in
  (`input_fallback`) was a Point Generator POP with its default random sphere, so
  `in1_P` on an unwired block read a random position such as `(0.33, -0.39, 0.53)`
  while the README said `0.0`. The stand-in now sits at the origin (radius 0, random
  off): `in1_P` is `(0, 0, 0)` exactly, `in1_N` stays a finite unit vector.
- Verified in TouchDesigner 2025.33230, see the *Tested* section of the README:
  the self-test line, 21 single functions against their formulas, attributes /
  components / Local lines / built-ins, every compile-error row of the README
  table, and the whole Inputs page (wire, field, wire beats field, Length Mismatch
  hold / repeat / zero / one, single point, arrays through `in1_`, bare names for
  unique attributes, a Local shadowing an attribute, chaining two components).
- README rewritten for GitHub: shorter, every function listed with its types
  (float / vec2 / vec3 / vec4), the *Types in Use As* toggle, requirements, build steps.

## 1.9 (2026-09-12)

A line without `=` no longer disappears in silence.

- **Ignored lines show up in Info.** `dwadwadw` on a line used to produce an
  empty `main()`, which compiles, so Info read *Compiled Successfully* with no hint
  that the line had been dropped. The parser still skips a line it cannot split
  at `=` (no `=`, nothing left of it, nothing right of it), but the generator now
  owns the Info text: `IGNORED line 0 'dwadwadw': no '=' | Compiled Successfully`
  (the ignored part first, because the Info field is narrow), and *View = code*
  carries the same note as a `// ignored line 0 ...` comment where the line's code
  would have been. Written one frame after a
  generator cook that changed the list (`run(..., delayFrames=1)`, never from
  inside the cook: reading `glsl1_info` there closes a dependency loop back to
  `script1`) and again from `datexec1` when `glsl1_info` changes, so the compile
  result and the ignored list never lag each other. Only written when the text
  differs.
- **`ifelse` takes a GLSL comparison.** `ifelse(1.0, 0.0, P.x > 0.0)` failed with
  *no matching overloaded function*: the library only knew the Math Mix form with
  a 1.0/0.0 condition (`gt(P.x, 0.0)`). Overloads with `bool` / `bvec2..4` as the
  condition are added, so both spellings work.
- **Use As turned red when the wire came out of a COMP.** Chaining two Expression
  POPs (or feeding one from a Base with an Out POP) put `'td.baseCOMP' object has no
  attribute 'pointAttributes'` on the node: the line read the attributes off the
  wire's owner. It now reads them off the POP inside the component that the shader
  sees anyway (`in1` / `in{n}` for a wire, `sel{n}` for the field), and a source
  without points shows `<- name (no points yet)` instead of an error. The code moved
  to `src/use_as.py`.
- `src/datexec1_info.py` is the new text of the stock `datexec1`; the stock
  behaviour stays in it as a fallback for an older generator.
- README: one more row in the compile table.


Several POP inputs, combined in one line the way the Math Mix POP does it.

### Writing lines

- `in1_P`, `in1_Color` … read the **second** input, `in2_…` the third; the first
  input keeps plain names. That is the Math Mix POP convention, where the prefix
  counts from 0. `in1_P` compiles to `TDIn_P(1u, _id1)`.
- **A prefix is only needed where the name is taken.** A bare name means the
  FIRST input that carries it, so an attribute unique to the second input
  (`mass`, where the first input has none) is written bare. The Use As line draws
  the same rule from the other side — it prints a prefix exactly where an earlier
  input has that attribute — so the page and the shader cannot drift apart.
  `in1_mass` keeps working and always names input 1 outright.
- **A Local shadows an attribute of the same name**, as it would in C. Without
  that, `float d = …` on a Local line followed by `P = P + N * d` silently read
  an attribute `d` off another input: it compiled, and quietly meant something
  else. Names declared on earlier Local lines are now excluded from attribute
  substitution.
- `_id1` is declared once per input a line actually uses, after the **Length
  Mismatch** rule: `id % n` (repeat), `min(id, n-1)` (hold), or the value guarded
  to 0 / 1. A single-point input is a constant, as on the Math Mix POP.
- Array helpers take the prefix too: `arrayadd(in1_Weights)` reads input 1 at
  its own index.
- A line that only copies one attribute (`cp = P`, `cp = in1_P`, `uv = in1_P.xy`)
  takes that attribute's width — now for plain input-0 attributes too, where the
  width used to be guessed as 1 and `cp = P` needed an explicit `vec3`. Any other
  right side keeps the old rule, so put the type in front when the guess would be
  too narrow.
- Limits that follow from the design, all deliberate: the output keeps the points
  of the **first** input; attributes that exist only on the other inputs do not
  pass through (write `Heat = in1_Heat` to keep one); only the first input is
  writable, so `in1_P` on the LEFT creates an attribute of that literal name
  instead of writing into input 1; and built-ins (`_PointI`, `_NumPoints`,
  `_BoundsCenterP` …) always describe the first input.
- No input limit: the GLSL POP reports `maxInputs` 9999 and the sequence has no
  `maxBlocks`. Eight wired inputs compile and evaluate correctly.

### Inputs page

- A Sequence `Inputs`, one block per connector, plus a **Length Mismatch** menu
  (hold / repeat / zero / one / none, default repeat).
- Block **0** ships with the component and is the connector the node already
  has, so its *Input POP* field is greyed out, like block 0 on the Math Mix POP.
  **+** gives the second input.
- On blocks 1+ the field greys out whenever a **wire** occupies that connector.
  The wire always wins.
- Read-only **Use As** line per block, built in the `use_as` DAT: the real point
  attributes of the POP on that connector, prefixed only where an earlier input
  has the same name, each with its GLSL type in brackets tight behind the name
  (`in1_P[vec3], in1_Age[float]   <-   noise2`), so the name stays one unbroken
  token. Nothing wired shows the prefix alone. The type is exactly the word a
  Local line needs, which answers the one rule that keeps biting.
  `pointAttributes` is metadata and a cook dependency, so the line also follows
  an upstream Attribute POP.

### Settings page

- New page **Settings** for how the component presents itself, as opposed to
  what it computes.
- **Types in Use As** (`Showtypes`, default on): with it off, the Use As lines
  drop to bare names (`in1_P, in1_Age, in1_N`). The Use As expression reads the
  toggle directly, and a parameter expression depends on every parameter it
  reads, so the lines redraw the moment it flips — no callback involved.

### How it is built

- Dan's **MultiTop** pattern: `replicator_in` stamps `in2`, `in3` … from `in1`
  (`numreplicants = max(1, numBlocks)`) and its callback wires each one to the
  next input of `glsl1`, removing its helpers again with the block.
- Each extra input passes a `guard{n}` Switch POP that picks, in order: the wire
  on `in{n}`, else `sel{n}` (a Select POP following the *Input POP* field), else
  `input_fallback`, a single point. Its index is an expression
  (`0 if op('in2').numPoints() else (1 if op('sel2').numPoints() else 2)`)
  because a wire pulled on the component fires no callback, but it does dirty
  the inPOP, so the Switch flips by itself.
- Two bugs this shape exists to prevent, both hit during development:
  - An inPOP whose connector is empty has 0 elements, and TouchDesigner cannot
    build buffer declarations for it (`array size must be a positive integer`).
    Pressing **+** used to kill the whole shader until you wired the input, even
    when no line mentioned it. The one-point fallback stands in, and a
    single-point input is a constant anyway, so an unwired input reads `0.0`.
  - If the *Input POP* field wires the connector itself, "wired on the node" and
    "typed in the field" become the same thing in the data model, and the rule
    above greys the field out the moment you use it, with no way back. Routing
    the field through `sel{n}` keeps them distinguishable.
- `parexec_inputs` no longer wires anything: it re-cooks the generator one frame
  later when a field or *Length Mismatch* changes, and its `StyleBlocks()` puts
  the Use As expression on new blocks, called from the replicator callback. A
  block added with **+** inherits `enableExpr` and `readOnly`, but not the
  expression.

### Verified, TouchDesigner 2025.32820

Two Point Generator POPs (10 points with `Age` = 7, and 10 / 3 / 1 points with
`Heat` = 3 and `Weights[4]` = 2): `heat = in1_Heat + Age` gives 10 on every
point, `cp = in1_P` equals the second input's P, `arrayadd(in1_Weights) +
arraylength(in1_Weights)` gives 12, `float(in1_P.x == in1_P.x)` is declared
float. With 3 points on the second input every Length Mismatch mode reads exactly
hold / repeat / zero / one; with 1 point every point reads point 0 in every mode.
Eight inputs sum to 28. All six field/wire states behave: wire locks the field,
field alone stays editable, wire beats field, pulling either falls back, and
**-** removes `in{n}`, `sel{n}` and `guard{n}` together.

Cost on a 3050-point input: Use As 0.016 ms per block, guard index 0.003 ms, the
generator's new multi-input work 0.013 ms — together about 0.03 ms, roughly two
tenths of a percent of a 60 fps frame. The generator itself cooks in 0.38 ms and,
exactly as the stock Function Store Expression POP does, once per frame while the
input animates: its `onCook` reads `op('in1').pointAttributes` and therefore
depends on that input. Everything added here reads attribute metadata only, never
point values, so nothing new stalls the GPU.

## 1.7 (2026-09-01)

- README is self-contained English: built-in table, Math Mix mapping, and the
  compile-error table now live here. `README_DE.md` and the `readme_de` DAT are gone.
- About page pulse **Readme** opens the internal `readme` DAT (`parexec_readme`).
- Multiple inputs are documented, not implemented. One POP input, same as
  Function Store's Expression POP; extra COMP connectors need a pattern like
  Dan's MultiTop (Sequence + Replicators + Parameter Execute). Merge upstream
  if you need several streams in one expression.

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
