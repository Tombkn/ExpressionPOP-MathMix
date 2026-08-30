# Expression POP + Math Mix

Write Math Mix operations straight into an expression line, with the same names
and formulas as the **Math Mix POP** menu:

```
Color = Color * ifelse(1.0, 0.2, gt(Age, 30.0))
P.y   = zigzag(_PointCy * 4.0, -1.0, 1.0)
heat  = remap(Age, 0.0, 60.0, 0.0, 1.0)
```

This is the Expression POP by **Function Store** ([the ExpressionPOP video](https://www.youtube.com/watch?v=fQco5ADaHyw))
with a GLSL function library built in. A plain Expression POP only knows raw
GLSL and answers `rangefrom` with *"no matching overloaded function found"*.

Nothing to install, nothing to configure. Drop it in and type.

---

## Start here

1. Drag **`ExpressionPOP_MathMix.tox`** into your network.
2. Connect a POP to its input.
3. On the parameter page, press "+" next to *Expr* and write a line.
4. Look at the result: middle-click the node, or put a Null POP behind it.

That is the whole setup. Save your project as usual.

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

You never have to prepare these. `_PointI` `_PointU` `_PointCy` `_NumPoints`
`_VertI` `_PrimI` `_DimI[0]` `_BoundsCenterP` `_StepSeconds` `_Pi` and the rest
exist in every expression, on every input.

**Everything in a line is the same for every point, except the built-ins.**
They are the only place where a point knows it is not point 0.

Only `_ArrayI` / `_ArrayU` / `_ArrayCy` are unavailable, because those count
inside an array operation, which a per-point expression has no equivalent for.

> **Full reference:** **`README_DE.md`** next to this file lists every built-in
> with the values it produces, every Math Mix function with its counterpart
> here, and what to do when something does not compile. Those tables are
> language-neutral (names and numbers), so they are worth a look even if you do
> not read German.

### Math Mix functions

Names carry over from the Math Mix POP menu: `rangefrom` `rangeto` `loop`
`zigzag` `remap` `compadd` `compavg` `arrayadd` `RGBtoHSV` `atan2` `angle`
`dbtoamp` and the rest. A few had to change because GLSL already uses the name,
and a few behave differently than you might expect:

- `A ** B` becomes `pow(A, B)`, `1 / A` becomes `inv(A)`, `int(A)` becomes `trunc(A)`
- `A if C else B` becomes `ifelse(A, B, C)`, where **the condition goes last**
- comparisons are functions: `gt gte lt lte eq ne`, returning 1.0 or 0.0
- trigonometry runs in **radians** (that is GLSL); for degrees use
  `sind cosd tand …`, while `atan2` and `angle` follow Math Mix and use **degrees**

The complete mapping table is in **`README_DE.md`**.

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

Also: Local lines must sit **above** the lines that use them.
