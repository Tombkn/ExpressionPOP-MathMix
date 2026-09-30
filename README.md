# Expression POP + Math Mix

Write Math Mix operations straight into an expression line, with the same names
and formulas as the **Math Mix POP** menu:

```
Color = Color * ifelse(1.0, 0.2, gt(Age, 30.0))
P.y   = zigzag(_PointCy * 4.0, -1.0, 1.0)
heat  = remap(Age, 0.0, 60.0, 0.0, 1.0)
```

This is the Expression POP by **Function Store** ([the ExpressionPOP video](https://www.youtube.com/watch?v=fQco5ADaHyw),
[Instagram](https://www.instagram.com/function.str/))
with a GLSL function library built in. A plain Expression POP only knows raw
GLSL and answers `rangefrom` with *"no matching overloaded function found"*.

Nothing to install, nothing to configure. Drop it in and type.

**Requirements:** TouchDesigner 2025.30000 or newer (POPs are stable from that
build on). Tested on 2025.32820 and 2025.33230, Windows. Nothing else: the
Function Store tools are *not* needed, the component is self-contained.

| In this repository | What it is |
|---|---|
| `ExpressionPOP_MathMix.tox` | the component, this is the only file you need |
| `README.md` | this text, also inside the component (About > Readme) |
| `SELFTEST.md` | one expression line that must come out as all zeros |
| `CHANGELOG.md` | what changed per version |
| `src/mathmix_lib.glsl` | the Math Mix function library, prepended to every shader |
| `src/script1_callbacks_patched.py` | the generator: your lines become the compute shader |
| `src/use_as.py` · `src/datexec1_info.py` | the *Use As* line of the Inputs page · the Info field |
| `src/build_expressionpop_mathmix.py` | rebuilds the `.tox` from the stock Expression POP (see *Build from source*) |

---

## Start here

1. Drag **`ExpressionPOP_MathMix.tox`** into your network.
2. Connect a POP to its input.
3. On the parameter page, press "+" next to *Expr* and write a line.
4. Look at the result: middle-click the node, or put a Null POP behind it.

That is the whole setup. Save your project as usual.

The same text lives inside the component: on the **About** page, press **Readme**.

---

## What you can write

### Attributes that already exist

Anything your input carries (`P`, `N`, `Color`, `Age` …) can be read and written:

```
P = P * 1.5
Color = Color * 0.5
```

### New attributes, just name them

Write a name the input does not have, and it is created for you:

```
heat  = _PointU * 5.0             new attribute, 1 value per point
shift = vec3(_PointU, 1.0, 2.0)   new attribute, 3 values per point
```

The width comes from what you write on the right: a `vec2/3/4(…)` gives 2/3/4
values, anything else gives 1.

If the right side is not a `vec2/3/4(…)` but still has several values, say
`P - _BoundsCenterP`, put the type in front of the name, same as on a Local line:

```
vec3 offset = P - _BoundsCenterP   new attribute, 3 values per point
```

Single components work too: `P.y = 0.0`, `Color.a = 0.5`.

### Built-ins: every `_` name is ready to use

You never have to prepare these. They exist in every expression:

| Built-in | What you get | At 10 points |
|---|---|---|
| `_PointI` | index of this point, from 0 | `0 … 9` |
| `_PointU` | position along the points, 0 to 1 | `0 … 1` |
| `_PointCy` | the same, but it never reaches 1 (cyclic) | `0 … 0.9` |
| `_NumPoints` | how many points there are | `10` |
| `_NumPrims` · `_NumVerts` | the same for primitives / vertices | `10` |
| `_VertI` · `_PrimI` | index within vertices / primitives | `0 … 9` |
| `_VertU` `_VertCy` `_PrimU` `_PrimCy` | the 0-to-1 variants of those | `0 … 1` |
| `_VertPrimI` · `_VertPrimU` · `_NumVertsPrim` | a vertex's place in its primitive | needs primitives |
| `_DimI[0]` | grid coordinate along axis 0 | `0 … 9` |
| `_DimSize[0]` · `_DimU[0]` · `_DimCy[0]` | size / 0-to-1 / cyclic of that axis | `10` · `0…1` · `0…0.9` |
| `_NumDim` | number of dimensions | `1` |
| `_BoundsMinP` · `_BoundsMaxP` · `_BoundsCenterP` | bounding box of the input, as vec3 | measured live |
| `_StepSeconds` | one frame in seconds | `0.01667` at 60 fps |
| `_StepFrames` | one frame | `1` |
| `_Pi` | 3.14159… | `3.142` |
| `_MaxInt` · `_MaxUInt` · `_NoNeighbor` | the usual limit constants | |

Only `_ArrayI` / `_ArrayU` / `_ArrayCy` are unavailable, because those count
inside an array operation, which a per-point expression has no equivalent for.

**Everything in a line is the same for every point, except the built-ins.**
They are the only place where a point knows it is not point 0.

### Math Mix functions

| In Math Mix | Here | Note |
|---|---|---|
| names GLSL already has: `abs sign sqrt floor round ceil fract normalize exp exp2 log2 sin cos tan asin acos atan degrees radians length min max mod dot cross reflect refract mix clamp smoothstep` | same name | GLSL semantics, trigonometry in **radians**. For degrees: `sind cosd tand asind acosd atand` |
| `A ** B` | `pow(A, B)` | |
| `1 / A` | `inv(A)` | `inverse` is the matrix inverse in GLSL, hence the other name. A = 0 stays 0 |
| `int(A)` · `int(A / B)` | `trunc(A)` · `intdiv(A, B)` | |
| `A if C else B` | `ifelse(A, B, C)` | **the condition goes last.** `ifelse(7, 3, gt(u, 0.5))` is 7 when u > 0.5; a plain comparison works too: `ifelse(7.0, 3.0, u > 0.5)` |
| `A > B` … `A != B` | `gt gte lt lte eq ne` | return 1.0 or 0.0 · `eqtol(A, B, tol)` for floats |
| `B <= A < C` and kin | `bltealtc bltaltec bltaltc bltealtec` | |
| `rangefrom rangeto loop zigzag mix clamp smoothstep` | same names | plus `remap(A, from1, from2, to1, to2)` |
| `logB avg exp10 log10 ln square` | same names | `ln` and `log10` return A unchanged for A ≤ 0 |
| `compadd compsub compmult compdiv compavg compmin compmax` | same names | for float, vec2, vec3, vec4. `compdiv` returns 0 on divide-by-zero, like Math Mix |
| `arraylength arrayadd arraymult arrayavg arraymin arraymax` | same names | for float-array attributes |
| `atan2(A, B)` · `angle(A, B)` | same names, in **degrees** | radian twins: `atan2rad` `anglerad` |
| `dbtopow powtodb dbtoamp amptodb` | same names | |
| `RGBtoHSV` · `HSVtoRGB` | same names | vec3 and vec4 |

### Values from outside

A number that should come from a parameter or a CHOP goes in as a uniform:
enter the component (`i`), select `glsl1`, page *Vectors*, add a vector named
`uAmp` (type `float`, value or expression). Then write `heat = _PointU * uAmp`.
The value changes every frame without recompiling the shader.

---

## OutAttr / Local

Every line has a toggle. Leave it **off** unless you need a scratch value.

| Toggle | Use it for |
|---|---|
| **OutAttr** (off) | writing an attribute, the normal case |
| **Local** (on) | a value you want to reuse in the lines below |

Local is a scrap of paper: you work something out, use it twice, and throw it
away. It never becomes an attribute.

```
[Local]    float d = length(P)
[OutAttr]  P     = P * (1.0 + d * 0.1)
[OutAttr]  Color = vec4(d, d, d, 1.0)
```

`length(P)` is calculated **once** and used twice, and there is only one place to
change it later.

**A Local line needs its type on the left.** That is the one rule to remember:

| Mode | You write | Result |
|---|---|---|
| OutAttr | `cool = vec4(3)` | works: attribute `cool` = `[3,3,3,3]` |
| Local | `cool = vec4(3)` | fails: `'cool' : undeclared identifier` |
| Local | `vec4 cool = vec4(3)` | works |

Why: in OutAttr mode `cool` **is** the attribute, and its type is handled for
you. In Local mode `cool` is an ordinary variable inside the shader, and those
need a type, same as in C.

**Where to get that type:** the *Use As* line on the Inputs page prints it in
brackets behind every name. `P[vec3]` means `vec3 d = P * 2.0`,
`Age[float]` means `float a = Age * 2.0`. (Page *Settings* can switch that off.)

Also: Local lines must sit **above** the lines that use them.

---

## Several inputs

Since 1.8 the component takes as many POP inputs as you ask for, and a line can
mix attributes from all of them, the same way the **Math Mix POP** does it.

1. Page **Inputs**. Block **0** is already there: it is the connector the node
   already has, so its *Input POP* field is greyed out — you wire that one on
   the node, same as on the Math Mix POP.
2. Press **+** and you get the **second** input: a new connector on the node.
   Feed it either way, and the **wire always wins**:

   | On that connector | *Input POP* field | What the input reads |
   |---|---|---|
   | a wire on the node | greyed out | the wire |
   | nothing | editable | the POP in the field |
   | nothing, field empty | editable | one point at the origin, so `0.0` |

   So a wired input is locked, exactly like block 0. The field stays editable
   only while no wire occupies the connector — clear it and it lets go again.
3. Each block has a read-only **Use As** line: the **real** point attributes of
   the POP on that connector, written exactly the way you type them in a line,
   each with its GLSL type, then the POP's name. Stretch the dialog if the list
   is long.

```
0   Input POP  [greyed]     Use As   P[vec3], Age[float], N[vec3]                     <-  noise1
1   Input POP  [noise2]     Use As   in1_P[vec3], in1_Age[float], heat[float]         <-  noise2
2   Input POP  [greyed]     Use As   in2_P[vec3], Weights[float[4]]                   <-  attribute1
3   Input POP  [ ]          Use As   in3_                                             <-  (nothing wired)
```

Read it as two answers at once.

**The name** tells you what to type — including whether it needs a prefix at all.
A name gets its `in1_` only where an **earlier input carries the same
attribute**, because that is the only case where the bare name is already taken.
An attribute unique to that input stays bare:

```
input 0  (noise1)      P, Age, N
input 1  (attribute1)  P, d, Age, N, dick, e

Use As, block 1        in1_P, d, in1_Age, in1_N, dick, e
                       └──────┴───────────┘      └────┴──┘
                       taken on input 0          unique, no prefix needed
```

So `dick` and `e` are typed as they are. A bare name always means the **first**
input that carries it, which is exactly the rule the line draws, so what you read
and what the shader does can never drift apart. `in1_P` still works everywhere
and always names input 1 outright.

The line follows what is upstream, so an attribute you add with an Attribute POP
appears here by itself.

One thing overrules an attribute name: a **Local** you declared on an earlier
line. `float d = …` makes `d` your own variable from there on, even when an input
has an attribute `d`, exactly as a local shadows an outer name in C.

**The type in brackets** tells you what a **Local** line needs. `P[vec3]` means
you write `vec3 d = P - in1_P`; `Age[float]` means `float a = Age * 2.0`. It sits
tight behind the name, so the name comes first where you scan for it and stays
one unbroken token. One value shows `[float]` or `[int]`, several `[vec3]` /
`[ivec2]`, an array its length (`[float[4]]`).

Page **Settings** has a toggle *Types in Use As*. Turn it off and the line drops
to bare names, `in1_P, in1_Age, in1_N`, which is the shorter list to copy from
once you know the types.

```
heat  = in1_Heat + Age            Heat from the second input, Age from the first
cp    = in1_P                     copies P of the second input (width 3, taken from it)
dist  = length(P - in1_P)         distance between matching points of both inputs
s     = arrayadd(in1_Weights)     array helpers work per input too
P.y   = P.y + in2_P.y * 0.5       components as usual
```

The result always has the points of the **first** input (like the Math Mix POP).
Attributes that only exist on the other inputs do not pass through; write them
into a new name if you need them (`Heat = in1_Heat`).

Two more things follow from that, and both are on purpose:

- **Only the first input can be written.** `in1_P = …` on the left does not
  write into the second input, it creates a new attribute literally called
  `in1_P`. Prefixes belong on the **right** side.
- **Built-ins always describe the first input.** `_PointI`, `_PointU`,
  `_NumPoints`, `_BoundsCenterP` … are about the points you are writing to.
  There is no `in1__NumPoints`.

How many inputs? TouchDesigner sets no limit (the GLSL POP reports 9999, the
sequence none), and eight wired inputs compile and run here. Reading is the
same for every input: **point** attributes, including float arrays.

**Different point counts.** When another input has fewer points than the first,
*Length Mismatch* on the Inputs page says what a point beyond its range reads,
same menu as the Math Mix POP:

| Length Mismatch | point 7 reads from a 3-point input |
|---|---|
| Hold | its last point (index 2) |
| Repeat *(default)* | index 7 mod 3 = 1, wraps around |
| Zero / One | the constant 0 / 1 |
| None | the raw read, whatever the buffer holds |

An input with a **single** point is always a constant for every point, whatever
the mode.

**A block you added but have not wired yet is fine.** It reads a single point at
the origin, so `in1_P` is a constant `0.0`, and the node keeps working — so you can
press + first and wire second.
Naming an attribute that input does not have still says so plainly:
`'in1_Heat' : undeclared identifier`.

Under the hood this is Dan's **MultiTop** pattern: the Sequence `Inputs` drives
a Replicator that stamps `in2`, `in3` … from `in1`. Each extra input then picks
its source with a `guard{n}` Switch POP:

```
sel{n}   (follows the Input POP field)  ─┐
in{n}    (the connector on the node)  ───┼──>  guard{n}  ──>  glsl1
input_fallback  (one point at 0,0,0)  ───┘
```

The field feeds `sel{n}`, a Select POP **inside** the component, and never
touches the connector — that is what lets a wire, and only a wire, grey the
field out. The one-point fallback is there because an input with zero elements
cannot be declared in the shader at all and would take the whole node down with
it. `in1_P` becomes `TDIn_P(1u, _id1)`, where `_id1` is the index after the
Length Mismatch rule (*View = code* shows it).

---

## When something does not compile

| Message / symptom | Cause | Fix |
|---|---|---|
| `'name' : undeclared identifier`, even though the name is on the line above | that line is *Local* but has no type | write `vec4 cool = vec4(3)` instead of `cool = vec4(3)`. The *Use As* line on the Inputs page prints the type you need in brackets |
| `cannot convert` / `no matching operator` between your own values | mismatched widths, e.g. `cool + vec3(1)` with `vec4 cool` | match them: `cool + vec4(1)` |
| `cannot convert from 'vec3' to 'float'` on a **new** attribute | the width was guessed from the right side, and there is no `vec3(…)` there | put the type in front of the name: `vec3 offset = P - _BoundsCenterP` |
| `undeclared identifier` on an attribute that should exist | typo, or not a **Point** attribute of the **first** input | read the block's *Use As* line on the Inputs page: it lists every name that works, spelled exactly |
| `'in1_Foo' : undeclared identifier` | the second input has no `Foo` — or nothing is wired to that connector, and the one-point stand-in only carries `P` and `N` | check the Inputs page; the prefix counts from 0, so `in1_` is the **second** connector |
| a value from another input is `0` and never changes | that connector is empty, so it reads the one-point stand-in | wire it, or look at the block's *Use As* line: it names the op on that connector |
| *Use As* reads `<- name (no points yet)` | the op on that connector has no point attributes yet: a COMP whose Out POP is empty, or a POP that has not cooked | feed it something; the line follows the connector as soon as points arrive |
| `cannot convert from 'vec3' to 'float'` on a **new** attribute built from another input | the width is only taken over when the line is exactly `name = in1_Attr` | put the type in front: `vec3 d = P - in1_P` |
| a comparison returns 0 or 1 instead of your two values | argument order of `ifelse` | condition last: `ifelse(A, B, C)` means *A if C, else B* |
| a value is 0 when it should not be | integer division, because `1 / 2` is 0 in GLSL | write `1.0 / 2.0`. Whole numbers as arguments are fine: `remap(Age, 0, 60, 0, 1)` works |
| it compiles, but nothing changes downstream | the line is on *Local* | switch to *OutAttr*, or use the local value in an *OutAttr* line below |
| the message does not match what you just typed | the *Info* field can lag one cook | touch the expression to force a cook, then read it again |
| `IGNORED line 0 'dwadwadw': no '=' \| Compiled Successfully` — and *View = code* shows `// ignored line 0 'dwadwadw': no '=' -- write  target = expression` where its code would be | that line has no `=` (or nothing on one side of it), so it produced no code; the rest compiled | every line is `target = expression`, e.g. `P = P * 2.0`; fix or delete the listed line. An ignored line never breaks the others |

Set **View** to *info* for compile messages and to *code* for the shader your
lines produce. Error line numbers match what *code* shows.

---

## Tested

Every release is run against the same list in a live TouchDesigner, with a Point
Generator POP (10 points) in front and a Null POP behind, reading the point
attributes back in Python. Last run: **2025.33230, v1.9.1**.

| Group | What ran | Result |
|---|---|---|
| Self-test | the line from `SELFTEST.md` | `0.0` in all four components on every point |
| Functions | `zigzag loop pow intdiv trunc eqtol bltealtc logB log10 ln exp10 atan2 angle dbtopow powtodb dbtoamp amptodb compsub compmult compdiv RGBtoHSV HSVtoRGB ifelse(bool) tand asind acosd atand square inv rangefrom mix clamp smoothstep` | every value equal to its formula |
| Lines | new attributes, `vec3(…)` width, `vec3 name =` typed width, `cp = P` copies width 3, `P.y = 5.0`, a Local used twice, every `_` built-in listed above | as documented |
| Errors | Local without type · line without `=` · typo in a function name · width guessed too narrow | the exact rows of the table above, ignored line noted in *code* |
| Inputs | wire · field · wire beats field · clearing the field · empty connector · Length Mismatch hold / repeat / zero / one · single point as constant · `in1_Weights` arrays · bare name for an attribute unique to input 1 · a Local shadowing an attribute · two components chained | as documented, *Use As* correct in every state |

## Build from source

You only need this to change the library or the generator. The `.tox` in the
repository is already built.

1. Open a project that has the **Function Store tools** loaded (the stock
   Expression POP is the template the build copies; its path is `SRC` at the top
   of the script).
2. Set `REPO` in `src/build_expressionpop_mathmix.py` to this folder.
3. In the textport:
   ```python
   exec(open(r'<repo>\srcuild_expressionpop_mathmix.py', encoding='utf-8').read())
   ```
4. The script copies the template into `/project1`, swaps in the library, the
   generator, the Inputs page and the docs, and saves `ExpressionPOP_MathMix.tox`
   next to this README.

The Math Mix formulas follow TouchDesigner's own generated code
([Math Mix Combine Functions](https://docs.derivative.ca/Math_Mix_Combine_Functions)).

---

Expression POP by [Function Store](https://www.instagram.com/function.str/) (original creator,
[video](https://www.youtube.com/watch?v=fQco5ADaHyw)). Math Mix library, multi-input page and
this build by [Tom](https://www.instagram.com/tomxbkn/). Multi-input pattern after Dan's MultiTop.
