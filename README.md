# Expression POP + Math Mix

Write Math Mix operations straight into an expression line, with the same names
and formulas as the **Math Mix POP** menu:

```
Color = Color * ifelse(1.0, 0.2, gt(Age, 30.0))
P.y   = zigzag(_PointCy * 4.0, -1.0, 1.0)
heat  = remap(Age, 0.0, 60.0, 0.0, 1.0)
```

This is the Expression POP by **Function Store**
([video](https://www.youtube.com/watch?v=fQco5ADaHyw), [Instagram](https://www.instagram.com/function.str/))
with a GLSL function library built in. A plain Expression POP only knows raw GLSL
and answers `rangefrom` with *"no matching overloaded function found"*.

**Requirements:** TouchDesigner 2025.30000 or newer. Tested on 2025.32820 and
2025.33230 (Windows). The Function Store tools are *not* needed; the component is
self-contained.

| File | What it is |
|---|---|
| `ExpressionPOP_MathMix.tox` | the component, the only file you need |
| `README.md` · `SELFTEST.md` · `CHANGELOG.md` | this text (also inside: About > Readme) · a one-line self-test · history |
| `src/` | library (`mathmix_lib.glsl`), generator, Inputs page code, build script |

---

## Start here

1. Drag **`ExpressionPOP_MathMix.tox`** into your network.
2. Connect a POP to its input.
3. Press **+** next to *Expr* and write a line: `target = expression`.
4. Middle-click the node, or put a Null POP behind it.

---

## What you can write

**Existing attributes** are read and written by name: `P = P * 1.5`, `Color = Color * 0.5`.
Components too: `P.y = 0.0`, `Color.a = 0.5`.

**New attributes** appear when you name them. Their width comes from the right side:

| You write | Width |
|---|---|
| `heat = _PointU * 5.0` | 1 (float) |
| `shift = vec3(_PointU, 1.0, 2.0)` | 3, from the `vec2/3/4(…)` |
| `cp = P` | the width of `P`, because the line only copies an attribute |
| `vec3 offset = P - _BoundsCenterP` | 3, because you said so |

If the right side has several values but does not start with `vec2/3/4(…)`,
put the type in front of the name (last row), else you get *cannot convert from 'vec3' to 'float'*.

**Uniforms:** a value from a parameter or CHOP goes into `glsl1` (inside the
component), page *Vectors*, as e.g. `uAmp`. Then write `heat = _PointU * uAmp`.

### Built-ins (every `_` name is ready to use)

| Built-in | What you get | At 10 points |
|---|---|---|
| `_PointI` · `_PointU` · `_PointCy` | index · 0-to-1 · 0-to-1 without reaching 1 | `0…9` · `0…1` · `0…0.9` |
| `_NumPoints` · `_NumPrims` · `_NumVerts` | counts | `10` |
| `_VertI` `_VertU` `_VertCy` · `_PrimI` `_PrimU` `_PrimCy` | the same for vertices / primitives | |
| `_VertPrimI` · `_VertPrimU` · `_NumVertsPrim` | a vertex's place in its primitive | needs primitives |
| `_DimI[0]` · `_DimSize[0]` · `_DimU[0]` · `_DimCy[0]` · `_NumDim` | grid coordinates of a 2D/3D layout | |
| `_BoundsMinP` · `_BoundsMaxP` · `_BoundsCenterP` | bounding box of the input, vec3 | measured live |
| `_StepSeconds` · `_StepFrames` · `_Pi` | `0.01667` at 60 fps · `1` · `3.14159` | |
| `_MaxInt` · `_MaxUInt` · `_NoNeighbor` | limit constants | |

Not available: `_ArrayI` / `_ArrayU` / `_ArrayCy` (they count inside an array
operation, which a per-point line has no equivalent for). Everything else in a
line is the same for every point; the built-ins are the only place a point knows
which one it is.

---

## Functions

Types: **f** = float, **vN** = vec2, vec3 and vec4. A function listed with "f, vN"
takes and returns any of those widths, component by component. Arguments written as
`0`, `60` are fine; only `1 / 2` is integer division in GLSL, so write `1.0 / 2.0`.

### Plain GLSL, unchanged (radians)

`abs sign sqrt floor round ceil trunc fract step normalize length dot cross reflect refract`
`exp exp2 log log2 pow sin cos tan asin acos atan degrees radians min max mod mix clamp smoothstep`

### Math Mix names, one argument

| Function | Types | Math Mix / meaning |
|---|---|---|
| `square(A)` | f, vN | `A * A` |
| `inv(A)` | f, vN | `1 / A`, stays 0 for A = 0 (`inverse` is GLSL's matrix inverse) |
| `exp10(A)` | f, vN | `10 ** A` |
| `log10(A)` · `ln(A)` | f | return A unchanged for A ≤ 0, like Math Mix |
| `trunc(A)` | f, vN | `int(A)` |
| `sind cosd tand asind acosd atand` | f | trigonometry in **degrees** (GLSL `sin`… stay radians) |
| `dbtopow powtodb dbtoamp amptodb` | f | audio dB conversions |
| `RGBtoHSV(A)` · `HSVtoRGB(A)` | vec3, vec4 | alpha passes through |

### Math Mix names, two arguments

| Function | Types | Math Mix / meaning |
|---|---|---|
| `pow(A, B)` | f, vN | `A ** B` |
| `intdiv(A, B)` | f | `int(A / B)` |
| `logB(A, B)` | f | log of A to base B, 0 where undefined |
| `avg(A, B)` | f, vN | `(A + B) / 2` |
| `gt gte lt lte eq ne` `(A, B)` | f, vN | `A > B` … `A != B`, return **1.0 / 0.0** per component |
| `eqtol(A, B, tol)` | f | equal within a tolerance |
| `atan2(A, B)` · `angle(A, B)` | f · vec2, vec3 | in **degrees**; radian twins `atan2rad`, `anglerad` |

### Math Mix names, three and more arguments

| Function | Types | Math Mix / meaning |
|---|---|---|
| `rangefrom(A, B, C)` | f, vN (B, C as f or vN) | A from [B, C] to 0…1 |
| `rangeto(A, B, C)` | f, vN (B, C as f or vN) | A from 0…1 to [B, C] |
| `remap(A, from1, from2, to1, to2)` | f | both in one |
| `loop(A, B, C)` · `zigzag(A, B, C)` | f, vN (B, C as f or vN) | sawtooth · ping-pong between B and C |
| `ifelse(A, B, C)` | A, B: f, vN · C: f, vN, `bool`, `bvecN` | **`A if C else B`, condition last.** `ifelse(7, 3, gt(u, .5))` or `ifelse(7, 3, u > .5)` |
| `bltealtc bltaltec bltaltc bltealtec` `(A, B, C)` | f | `B <= A < C` · `B < A <= C` · `B < A < C` · `B <= A <= C`, return 1.0 / 0.0 |
| `mix(A, B, t)` · `clamp(A, lo, hi)` · `smoothstep(lo, hi, A)` | f, vN | plain GLSL, same names as Math Mix |

### One vector → one number

| Function | Types |
|---|---|
| `compadd compsub compmult compdiv compavg compmin compmax` `(A)` | f, vN → f. `compdiv` returns 0 on divide-by-zero, like Math Mix |

### Float-array attributes (e.g. `Weights[4]` from an Attribute POP)

| Function | Returns |
|---|---|
| `arraylength(Name)` | number of entries |
| `arrayadd arraymult arrayavg arraymin arraymax` `(Name)` | the reduction over this point's array |

---

## OutAttr / Local

Every line has a toggle. **OutAttr** (off, the default) writes an attribute.
**Local** (on) is a scratch value for the lines below; it never becomes an attribute.

```
[Local]    float d = length(P)
[OutAttr]  P     = P * (1.0 + d * 0.1)
[OutAttr]  Color = vec4(d, d, d, 1.0)
```

**A Local line needs its type on the left**: `vec4 cool = vec4(3)`, not `cool = vec4(3)`
(*'cool' : undeclared identifier*). The type is printed for you on the Inputs page,
see below. Local lines must sit above the lines that use them.

---

## Several inputs

The component takes as many POP inputs as you ask for and a line can mix them, as
the Math Mix POP does.

**Page Inputs.** Block 0 is the connector the node already has. **+** adds the next
connector. Each block has an *Input POP* field and a read-only *Use As* line:

```
0   Input POP  [greyed]     Use As   P[vec3], Age[float], N[vec3]                <-  noise1
1   Input POP  [noise2]     Use As   in1_P[vec3], in1_Age[float], heat[float]    <-  noise2
2   Input POP  [ ]          Use As   in2_                                        <-  (nothing wired)
```

| Connector | Field | The input reads |
|---|---|---|
| a wire on the node | greyed out | the wire (the wire always wins) |
| nothing | editable | the POP named in the field |
| nothing, field empty | editable | one point at the origin, so `0.0` |

**Use As tells you two things.**

- **The name to type.** A name gets its `in1_` / `in2_` prefix only where an earlier
  input already has that attribute; a name unique to that input is typed bare. A bare
  name always means the first input that carries it. `in1_P` always works and
  always means input 1 (the **second** connector, Math Mix counts from 0).
- **The type in brackets**, `P[vec3]`, `Age[float]`, `Weights[float[4]]`. That is the
  word a Local line needs: `vec3 d = P - in1_P`. **Page Settings > *Types in Use As***
  switches the brackets off for a short bare list (`in1_P, in1_Age, in1_N`) and on again.

```
heat  = in1_Heat + Age            Heat from the second input, Age from the first
dist  = length(P - in1_P)         distance between matching points
s     = arrayadd(in1_Weights)     array helpers work per input
```

**Rules that follow from "the result has the points of the first input":**

- Only the first input can be written. `in1_P = …` on the left creates a new
  attribute literally called `in1_P`.
- Attributes that exist only on other inputs do not pass through; copy them:
  `Heat = in1_Heat`.
- Built-ins (`_PointI`, `_NumPoints`, `_BoundsCenterP` …) always describe the first input.
- A Local you declared earlier (`float d = …`) shadows an attribute `d` of any input.

**Length Mismatch** (Inputs page) says what a point reads from an input with fewer points:

| Mode | Point 7 reads from a 3-point input |
|---|---|
| Hold | its last point (index 2) |
| Repeat *(default)* | index 7 mod 3 = 1 |
| Zero / One | the constant 0 / 1 |
| None | the raw read |

A single-point input is a constant for every point. An unwired block is fine: it
reads the origin and the node keeps working, so you can press + first and wire second.
No input limit; eight wired inputs are verified.

---

## When something does not compile

Set **View** to *info* for messages and *code* for the shader; line numbers match.

| Message / symptom | Fix |
|---|---|
| `'name' : undeclared identifier`, name is on the line above | that line is Local without a type: `vec4 cool = vec4(3)`. The type is on the Inputs page |
| `cannot convert from 'vec3' to 'float'` on a new attribute | type in front: `vec3 offset = P - _BoundsCenterP` |
| `cannot convert` / `no matching operator` between your own values | match the widths: `cool + vec4(1)` |
| `undeclared identifier` on an attribute that should exist | typo, or not a point attribute of that input: the *Use As* line lists every valid name |
| `'in1_Foo' : undeclared identifier` | the second connector has no `Foo`, or nothing is wired to it (the one-point stand-in only has `P` and `N`) |
| a value from another input is `0` and never changes | that connector is empty; wire it, *Use As* names what it reads |
| `'sindd' : no matching overloaded function` | typo in a function name, see the Functions section |
| a comparison returns 0 or 1 instead of your two values | `ifelse(A, B, C)` is *A if C else B*, condition last |
| a value is 0 when it should not be | integer division: `1.0 / 2.0` |
| `IGNORED line 0 'abc': no '='` | that line has no `=`; the others still compile. *View = code* shows `// ignored line …` where its code would be |
| it compiles, nothing changes downstream | the line is on Local |
| *Use As* reads `<- name (no points yet)` | the op on that connector has no points yet |

---

## Tested

Run in a live TouchDesigner (2025.33230, v1.9.1) with a Point Generator POP in front
and the attributes read back in Python: the `SELFTEST.md` line (all zeros), every
function above against its formula, new / typed / component attributes, Local lines,
all built-ins, every row of the table above, and the whole Inputs page (wire, field,
wire beats field, Length Mismatch modes, single point, arrays through `in1_`, bare
unique names, Local shadowing, two components chained).

## Build from source

Only needed to change the library or the generator; the `.tox` is already built.
Set `REPO` in `src/build_expressionpop_mathmix.py`, then in the textport:

```python
exec(open(r'<repo>\src\build_expressionpop_mathmix.py', encoding='utf-8').read())
```

Formulas follow TouchDesigner's own
[Math Mix Combine Functions](https://docs.derivative.ca/Math_Mix_Combine_Functions).

---

## Credits

Expression POP by [Function Store](https://www.instagram.com/function.str/) (original creator).
Math Mix library, Inputs page and this build by [Tom](https://www.instagram.com/tomxbkn/).
Multi-input pattern after Dan's MultiTop.
