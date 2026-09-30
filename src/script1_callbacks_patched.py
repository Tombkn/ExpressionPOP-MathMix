import re

# ---------------------------------------------------------------------------
#  Expression POP generator (script1_callbacks) — patched for mathmix_lib  (v1.9)
#  Drop-in replacement for the text of the 'script1_callbacks' DAT.
#
#  Changes vs. the original generator:
#   1. LIBRARY  — rangefrom(), loop(), compadd(), RGBtoHSV() ... become available
#                 WITHOUT appearing in the shader this generator writes: the
#                 installer's mergeDAT 'mathmix_shader' prepends 'mathmix_lib'
#                 on the way to glsl1, while View=code keeps showing the plain
#                 main() the stock generator would produce. Without that merge
#                 DAT (generator used standalone) the library is inlined as before.
#   2. PARSER   — the line is split at the first REAL '=' (not part of ==, >=,
#                 <=, !=), so comparisons inside an expression are safe.
#   3. ARRAYS   — arrayadd/arraymult/arrayavg/arraymin/arraymax/arraylength(Name)
#                 are generated per ARRAY attribute (float arrays). They read with
#                 the full accessor TDIn_X(0u, id, i): the two-argument form is
#                 (input, element), so TDIn_X(id, i) silently read input #id and
#                 returned 0 for every point but the first (fixed in v1.6).
#   4. BUILTINS — _PointI, _PointU, _PointCy, _NumPoints, _DimI[0], _Pi ... are
#                 mapped to their GLSL POP equivalents (see BUILTIN_SUBST).
#   5. Attribute names are replaced only where they are used as values — not
#                 inside function calls (angle(...)) or member access (x.angle).
#   6. Trailing ';' and '// comments' in a line are tolerated; a broken line
#                 never empties the shader (text is assigned last).
#   8. NEW ATTRIBUTES — an expression whose left side names an attribute the
#                 input does not have (myval = _PointU * 5.0) used to fail with
#                 "'myval' : undeclared identifier": par.outputattrs supplies the
#                 NAME, but the GLSL POP also needs the TYPE. _syncOutputAttrs()
#                 now fills glsl1's attr sequence automatically. Width is inferred
#                 from the right-hand side (vec3(...) -> 3, otherwise the widest
#                 local it mentions, else 1). Guarded: only written when the
#                 declaration actually changes, else the cook loops.
#   7. _StepFrames / _StepSeconds / _NoNeighbor and _BoundsMinP / _BoundsMaxP /
#                 _BoundsCenterP are resolved when the shader is built (see
#                 _dynamicBuiltins) - the bounds are read from the input POP only
#                 when an expression actually mentions them.
#   9. COMPONENT TARGETS (v1.6) — `P.y = ...`, `Color.a = ...`, `C[0] = ...` used
#                 to fail with "'P' : undeclared identifier": the target became
#                 `P.y[id]` (not GLSL) and glsl1's Output Attributes got "P.y"
#                 instead of "P", so P was never allocated for writing. The left
#                 side is now split into base + component (`P[id].y`), and the
#                 generator OWNS glsl1.par.outputattrs (base names of all OutAttr
#                 lines) instead of the stock par expression. A new attribute
#                 written by component (`foo.z = 1.0`) is declared wide enough
#                 to hold that component.
#  10. EXPLICIT WIDTH (v1.6) — `vec3 offset = P - _BoundsCenterP` in OutAttr mode:
#                 the width of a new attribute is guessed from the right side
#                 (vec3(...) -> 3, else 1), which cannot see that P is a vec3.
#                 A type on the left names the width outright, same spelling as
#                 a Local line; the type is dropped from the generated code.
#  11. SEVERAL INPUTS (v1.8) — the component grows one connector per block of its
#                 Inputs sequence (Dan's MultiTop pattern: Replicator stamps in2, in3 ...
#                 from in1 and wires them to glsl1). In a line, the second input's
#                 attributes are in1_P, in1_Color ..., the third input's in2_P ...
#                 (Math Mix POP naming: 0-based prefix, first input stays plain).
#                 in1_P becomes TDIn_P(1u, _id1); _id1 is that input's index after the
#                 Length Mismatch policy (hold / repeat / zero / one / none, as on the
#                 Math Mix POP). A single-point input reads as a constant. Array helpers
#                 work per input too: arrayadd(in1_Weights). Output still follows input 0.
#  13. IGNORED LINES (v1.9) — a line the parser cannot split at '=' (no '=', or nothing
#                 on one side of it) used to vanish without a trace: the shader stayed
#                 empty, glsl1 compiled the empty main() and Info read "Compiled
#                 Successfully" for `dwadwadw`. The generator now OWNS the Info text:
#                 UpdateInfo() writes compile result + the ignored lines, called at the
#                 end of every cook and from datexec1 when glsl1_info changes.
# ---------------------------------------------------------------------------

LIB_DAT = 'mathmix_lib'          # sibling textDAT holding mathmix_lib.glsl
SHADER_DAT = 'mathmix_shader'    # installer's mergeDAT: lib + helpers + visible code -> glsl1
HELPERS_DAT = 'mathmix_helpers'  # sibling textDAT the generated array helpers are parked in
LINE_RESET = '#line 1'           # GLSL error lines count from main() again, not from the library
RESERVED = {'id'}                # tokens the generated code relies on; never treated as attribute names

# Math Mix built-in attributes -> GLSL POP. `id` is the element index declared in main().
BUILTIN_SUBST = {
	'_PointI': 'id', '_VertI': 'id', '_PrimI': 'id',
	'_PointU': '(float(id) / float(max(TDNumElements(), 2u) - 1u))',
	'_VertU':  '(float(id) / float(max(TDNumElements(), 2u) - 1u))',
	'_PrimU':  '(float(id) / float(max(TDNumElements(), 2u) - 1u))',
	'_PointCy': '(float(id) / float(TDNumElements()))',
	'_VertCy':  '(float(id) / float(TDNumElements()))',
	'_PrimCy':  '(float(id) / float(TDNumElements()))',
	'_NumPoints': 'TDInputNumPoints(0u)',
	'_NumPrims':  'TDInputNumPrims(0u)',
	'_NumVerts':  'TDInputNumVerts(0u)',
	'_VertPrimI': 'TDInputVertPrimIndex(id)',
	'_VertPrimU': '(float(TDInputVertPrimIndex(id)) / float(max(TDInputNumVertsPerPrimFromVert(0u, id), 2u) - 1u))',
	'_NumVertsPrim': 'TDInputNumVertsPerPrimFromVert(0u, id)',
	'_NumDim': 'cTDDimSize',
	'_StepFrames': '1.0',
	'_NoNeighbor': '4294967296.0',     # Math Mix sentinel (0xFFFFFFFF as float)
	'_Pi': '3.14159265358979',
	'_MaxUInt': '0xFFFFFFFFu',
	'_MaxInt': '2147483647',
}
# indexed built-ins: _DimI[0], _DimSize[1], _DimU[0], _DimCy[0]
DIM_SUBST = [
	(r'\b_DimI\[(\d+)\]',    r'TDDimCoords(id)[\1]'),
	(r'\b_DimSize\[(\d+)\]', r'TDDimension()[\1]'),
	(r'\b_DimU\[(\d+)\]',    r'(float(TDDimCoords(id)[\1]) / float(max(TDDimension()[\1], 2u) - 1u))'),
	(r'\b_DimCy\[(\d+)\]',   r'(float(TDDimCoords(id)[\1]) / float(TDDimension()[\1]))'),
]
# _StepSeconds and the _Bounds* built-ins depend on the project / the input POP and
# are resolved per cook -> _dynamicBuiltins(). Only _ArrayI/_ArrayU/_ArrayCy stay
# unavailable: they are the loop counter inside an array operation, which a plain
# per-element expression has no equivalent for.

# per-attribute array reductions, generated on demand (float array attributes).
# {n} attribute name, {k} input number, {key} helper suffix ('Weights' / 'in1_Weights').
ARRAY_HELPERS = {
	'arrayadd':  'float _arrayadd_{key}(uint id) {{ float s = 0.0; for (uint i = 0u; i < cTDArraySize_{n}; i++) s += float(TDIn_{n}({k}u, id, i)); return s; }}',
	'arraymult': 'float _arraymult_{key}(uint id) {{ float p = 1.0; for (uint i = 0u; i < cTDArraySize_{n}; i++) p *= float(TDIn_{n}({k}u, id, i)); return p; }}',
	'arrayavg':  'float _arrayavg_{key}(uint id) {{ float s = 0.0; for (uint i = 0u; i < cTDArraySize_{n}; i++) s += float(TDIn_{n}({k}u, id, i)); return s / float(cTDArraySize_{n}); }}',
	'arraymin':  'float _arraymin_{key}(uint id) {{ float m = float(TDIn_{n}({k}u, id, 0u)); for (uint i = 1u; i < cTDArraySize_{n}; i++) m = min(m, float(TDIn_{n}({k}u, id, i))); return m; }}',
	'arraymax':  'float _arraymax_{key}(uint id) {{ float m = float(TDIn_{n}({k}u, id, 0u)); for (uint i = 1u; i < cTDArraySize_{n}; i++) m = max(m, float(TDIn_{n}({k}u, id, i))); return m; }}',
}
ARRAY_CALL_RE = re.compile(r'\b(arraylength|arrayadd|arraymult|arrayavg|arraymin|arraymax)\(\s*(\w+)\s*\)')
ASSIGN_RE = re.compile(r'(?<![=<>!])=(?!=)')     # first '=' that is not part of ==, >=, <=, !=
# (11) in1_P -> attribute P of input 1 (the SECOND connector). Same guards as a plain
# attribute: not after '.', not before '(' — and not inside another identifier.
INPUT_ATTR_RE = re.compile(r'(?<![\w.])in(\d+)_([A-Za-z_]\w*)\b(?!\s*\()')
MISMATCH_MODES = ('hold', 'repeat', 'zero', 'one', 'none')   # Length Mismatch menu, as on the Math Mix POP
INFO_DAT = 'glsl1_info'          # sibling infoDAT with the compile result of glsl1
INFO_JUNK = ('=============', '==========', 'Compute Shader Compile Results:')   # decoration in glsl1_info
IGNORE_NO_ASSIGN = "no '='"
IGNORE_NO_LEFT = "nothing left of '='"
IGNORE_NO_RIGHT = "nothing right of '='"
_ignored: list[tuple[int, str, str]] = []   # (block index, line as typed, reason) of the last cook

SHADER_TEMPLATE = """
<INSERT DEFINES HERE>
void main() {
	const uint id = TDIndex();
	if(id >= TDNumElements())
		return;
	<INPUT_INDICES_HERE>
	<SUBSTITUTE_EXPRESSIONS_HERE>
}
"""


def onSetupParameters(scriptOp):
	page = scriptOp.appendCustomPage('Custom')
	p = page.appendFloat('Valuea', label='Value A')
	p = page.appendFloat('Valueb', label='Value B')
	return


def onPulse(par):
	return


def make_glsl_define(idx, leftSide, rightSide, leftMode=0):
	define_name = f'POP_EXPRESSION_{idx}'
	define_text = f'#define {define_name}'
	if leftMode == 0:
		base, rest = _splitTarget(leftSide)          # (9) 'P.y' -> 'P[id].y', 'C[0]' -> 'C[id][0]'
		define_expression = f'{base}[id]{rest} = ({rightSide})'
	else:
		define_expression = f'{leftSide} = {rightSide}'
	return (define_name, define_text, define_expression)


def _leftMode(value) -> int:
	"""Expr_leftmode cell -> 0 (out attribute) / 1 (local). Tolerates '', 'True', '1.0'."""
	s = str(value).strip().lower()
	if s in ('', '0', 'false', 'off', 'attribute', 'out'):
		return 0
	if s in ('1', 'true', 'on', 'local'):
		return 1
	try:
		return 1 if int(float(s)) else 0
	except ValueError:
		return 0


def _isArrayAttrib(attr) -> bool:
	isArray = getattr(attr, 'isArray', None)
	if isArray is not None:
		return bool(isArray)
	return int(getattr(attr, 'arraySize', 1) or 1) > 1


def _boundsSubst(inPOP):
	"""_BoundsMinP / _BoundsMaxP / _BoundsCenterP as vec3 literals, read from the input POP.
	CPU read of P - only called when an expression actually uses one of them."""
	try:
		pts = list(inPOP.points('P'))
	except Exception:
		pts = []
	if not pts:
		z = 'vec3(0.0)'
		return {'_BoundsMinP': z, '_BoundsMaxP': z, '_BoundsCenterP': z}
	mn = [min(pt[i] for pt in pts) for i in range(3)]
	mx = [max(pt[i] for pt in pts) for i in range(3)]
	ct = [(mn[i] + mx[i]) * 0.5 for i in range(3)]
	fmt = lambda v: 'vec3({:.8g}, {:.8g}, {:.8g})'.format(*v)
	return {'_BoundsMinP': fmt(mn), '_BoundsMaxP': fmt(mx), '_BoundsCenterP': fmt(ct)}


def _dynamicBuiltins(inPOP, expressions):
	"""Built-ins that are not a fixed GLSL snippet: timeline step + input bounds."""
	dyn = {}
	try:
		rate = float(me.time.rate) or 60.0
	except Exception:
		rate = 60.0
	dyn['_StepSeconds'] = '{:.10g}'.format(1.0 / rate)
	if '_Bounds' in ' '.join(str(e) for e in expressions):
		dyn.update(_boundsSubst(inPOP))
	return dyn


def substitute_builtins(expr, dynamic=None):
	"""_PointI, _DimU[0], _Pi, _BoundsMinP ... -> GLSL POP equivalents."""
	for pattern, replacement in DIM_SUBST:
		expr = re.sub(pattern, replacement, expr)
	table = dict(BUILTIN_SUBST)
	table.update(dynamic or {})
	for name in sorted(table, key=len, reverse=True):
		expr = re.sub(r'\b' + re.escape(name) + r'\b', table[name], expr)
	return expr


def substitute_arrays(expr, arrayNames, helpers, used):
	"""arrayadd(Name) -> _arrayadd_Name(id) + helper definition; arraylength(Name) -> float(cTDArraySize_Name).
	(11) arrayadd(in1_Name) reads input 1 at that input's own index: _arrayadd_in1_Name(_id1).
	arrayNames: {token: (input number, attribute name)}, e.g. {'Weights': (0, 'Weights'), 'in1_Weights': (1, 'Weights')}.
	Only for real array attributes — anything else is left alone (and fails visibly in GLSL)."""
	def repl(m):
		fn, token = m.group(1), m.group(2)
		if token not in arrayNames:
			return m.group(0)
		k, name = arrayNames[token]
		if fn == 'arraylength':
			return f'float(cTDArraySize_{name})'
		used.add(k)
		helpers[f'{fn}_{token}'] = ARRAY_HELPERS[fn].format(n=name, k=k, key=token)
		return f'_{fn}_{token}({_indexVar(k)})'
	return ARRAY_CALL_RE.sub(repl, expr)


def _indexVar(k) -> str:
	"""The element index to read input k at: `id` for input 0, `_id1` / `_id2` ... otherwise."""
	return 'id' if k == 0 else f'_id{k}'


def _glslZero(attr, one=False) -> str:
	"""A GLSL literal in the attribute's own type: 0.0 / vec3(0.0) / 0 / ivec2(0); 1.0 ... for `one`."""
	isInt = getattr(attr, 'type', float) in (int, bool)
	size = int(getattr(attr, 'size', 1) or 1)
	v = ('1' if one else '0') if isInt else ('1.0' if one else '0.0')
	if size <= 1:
		return v
	return f'{"ivec" if isInt else "vec"}{size}({v})'


def substitute_input_attribs(expr, inputAttribs, mode, used, skip=frozenset()):
	"""in1_P -> TDIn_P(1u, _id1): attribute P of the SECOND input (Math Mix POP naming, the prefix
	counts from 0). in0_P is the same as plain P. `used` collects the input numbers a line touches,
	so main() declares only the index variables it needs (_inputIndexLines).
	A point beyond a shorter input's range follows the Length Mismatch policy: hold / repeat move
	the INDEX (in _inputIndexLines), zero / one replace the VALUE right here, none reads raw.
	Unknown names are left alone, so the GLSL error names them (in1_Foo : undeclared identifier)."""
	def repl(m):
		k, name = int(m.group(1)), m.group(2)
		if m.group(0) in skip:                       # a Local of that exact name shadows it
			return m.group(0)
		attrs = inputAttribs.get(k)
		if attrs is None or name not in attrs:
			return m.group(0)
		used.add(k)
		if k == 0:
			return f'TDIn_{name}()'
		read = f'TDIn_{name}({k}u, _id{k})'
		if mode in ('zero', 'one'):
			return f'((_n{k} <= 1u || id < _n{k}) ? {read} : {_glslZero(attrs[name], mode == "one")})'
		return read
	return INPUT_ATTR_RE.sub(repl, expr)


def _inputIndexLines(used, mode) -> str:
	"""One `_nK` / `_idK` pair per extra input a line reads, resolved by the Length Mismatch policy.
	A single-point input is a constant (index 0 for every point), same as the Math Mix POP."""
	lines = []
	for k in sorted(u for u in used if u > 0):
		n, idx = f'_n{k}', f'_id{k}'
		if mode == 'hold':
			pick = f'min(id, {n} - 1u)'
		elif mode == 'repeat':
			pick = f'(id % {n})'
		else:                                   # zero / one / none: same index, the VALUE is guarded
			pick = 'id'
		lines.append(f'const uint {n} = TDInputNumPoints({k}u);')
		lines.append(f'const uint {idx} = ({n} <= 1u) ? 0u : {pick};')
	return '\n\t'.join(lines)


def _inputAttribs(inPOP):
	"""{input number: {attribute name: attribute}} for every wired input of glsl1.
	Input 0 is in1 (the POP handed in); 1, 2 ... are whatever in2, in3 ... carry right now."""
	table = {0: {a.name: a for a in inPOP.pointAttributes}}
	glsl = op(GLSL_OP)
	if glsl is None:
		return table
	for k, conn in enumerate(glsl.inputConnectors):
		if k == 0 or not conn.connections:
			continue
		try:
			table[k] = {a.name: a for a in conn.connections[0].owner.pointAttributes}
		except Exception:
			table[k] = {}
	return table


def _mismatchMode() -> str:
	"""Length Mismatch parameter of the component: what a point reads from an input with FEWER points."""
	try:
		p = parent().par['Lengthmismatch']
		m = str(p.eval()).strip().lower() if p is not None else 'repeat'
	except Exception:
		m = 'repeat'
	return m if m in MISMATCH_MODES else 'repeat'


def substitute_attribs(expr, resolve, used, skip=frozenset()):
	"""Age -> TDIn_Age()  — only where the name is used as a VALUE:
	not after '.' (member access), not before '(' (function call), not inside other identifiers.

	(12) A BARE name belongs to the FIRST input that carries it. Usually that is input 0, but
	an attribute only the second input has (`dick`) is unambiguous, so it needs no prefix and
	reads from there: `TDIn_dick(1u, _id1)`. `in1_dick` keeps working and always names input 1
	outright. The Use As line on the Inputs page shows exactly this: a prefix appears only
	where an earlier input carries the same name, i.e. exactly where the bare name is taken.

	resolve: {attribute name: input number that a bare mention reads}.
	skip:    names declared on an earlier Local line. A local SHADOWS an attribute of the same
	         name, as it would in C. Without this, `float d = ...` on a Local line followed by
	         `P = P + N * d` silently reads an attribute `d` off another input instead of the
	         value just computed -- it compiles, and quietly means something else."""
	for name in sorted(resolve, key=len, reverse=True):
		if name in RESERVED or name in skip:
			continue
		pattern = r'(?<![\w.])' + re.escape(name) + r'\b(?!\s*\()'
		if not re.search(pattern, expr):
			continue
		k = resolve[name]
		used.add(k)
		expr = re.sub(pattern, f'TDIn_{name}()' if k == 0 else f'TDIn_{name}({k}u, {_indexVar(k)})', expr)
	return expr


def _header(array_helpers) -> str:
	"""Everything that has to stand before main() — and where it goes.

	Installed (mergeDAT 'mathmix_shader' present): the library is already prepended on
	the way to glsl1 and the array helpers are parked in 'mathmix_helpers', so nothing
	is left to put here — View=code shows the same plain main() the stock generator
	produces, not 230 lines of library.
	Standalone (no merge DAT): inline both, as v1.2 did."""
	helpers = '\n'.join(array_helpers.values())
	if op(SHADER_DAT) is None:
		lib = op(LIB_DAT)
		return '\n'.join(part for part in (lib.text if lib is not None else '', helpers) if part.strip())
	if (parked := op(HELPERS_DAT)) is None:
		return helpers
	# '#line 1' has to be the LAST row before the visible code: it makes the driver count
	# error lines from main() again instead of from the top of the ~230-line library, so
	# 'ERROR: ...:5' points at line 5 of what View=code shows.
	parked_text = f'{helpers}\n{LINE_RESET}' if helpers else LINE_RESET
	if parked.text.rstrip('\n') != parked_text:   # guarded: an unconditional write recooks forever
		parked.text = parked_text
	return ''


GLSL_OP = 'glsl1'                      # sibling GLSL POP whose attr sequence we fill
TYPE_COMPS = {'float': 1, 'vec2': 2, 'vec3': 3, 'vec4': 4}
VEC_CTOR_RE = re.compile(r'^\s*vec([234])\s*\(')
TARGET_RE = re.compile(r'^\s*([A-Za-z_]\w*)\s*(.*?)\s*$')
SWIZZLE_MIN = {ch: i % 4 + 1 for i, ch in enumerate('xyzwrgbastpq')}   # .y needs 2 comps, .a needs 4


def _splitTarget(leftSide):
	"""'P.y' -> ('P', '.y');  'C[0]' -> ('C', '[0]');  'heat' -> ('heat', '')."""
	m = TARGET_RE.match(leftSide)
	if not m:
		return leftSide.strip(), ''
	return m.group(1), m.group(2)


def _minCompsForTarget(rest):
	"""'.y' -> 2, '.xyz' -> 3, '[2]' -> 3, '' -> 1: the narrowest attribute the target fits in."""
	need = 1
	m = re.match(r'\.([xyzwrgbastpq]+)$', rest)
	if m:
		need = max(SWIZZLE_MIN[ch] for ch in m.group(1))
	m = re.match(r'\[(\d+)\]$', rest)
	if m:
		need = max(need, int(m.group(1)) + 1)
	return need


def _localDecl(leftSide):
	"""'float tmp' -> ('tmp', 1). No type prefix -> (None, 0)."""
	parts = leftSide.split()
	if len(parts) == 2 and parts[0] in TYPE_COMPS:
		return parts[1], TYPE_COMPS[parts[0]]
	return None, 0


def _numComps(rightSide, localTypes):
	"""How many components does the right-hand side yield?

	vec3(...) -> 3; otherwise the widest known local it mentions; else 1.
	A HEURISTIC, deliberately conservative: it only decides the WIDTH of a new
	attribute. Guessing too narrow shows up immediately as a GLSL type error,
	never as a silently wrong number."""
	m = VEC_CTOR_RE.match(rightSide)
	if m:
		return int(m.group(1))
	widest = 1
	for name, comps in localTypes.items():
		if re.search(r'(?<![\w.])' + re.escape(name) + r'\b', rightSide):
			widest = max(widest, comps)
	return widest


EXACT_READ_RE = re.compile(r'^\s*([A-Za-z_]\w*)(?:\.([xyzwrgbastpq]{1,4}))?\s*$')


def _exactReadWidth(rawRight, readSizes) -> int:
	"""`cp = P` -> 3, `cp = in1_P` -> 3, `uv = in1_P.xy` -> 2: a line that only copies one
	attribute takes that attribute's width. Anything more (`float(in1_P.x == 0.0)`) -> 0, so
	the usual rule decides; merely mentioning a vec3 must not turn a float result into one.

	readSizes covers every name a right side may use: bare names (resolved to the first input
	that carries them, same as substitute_attribs) and the explicit in{k}_ spellings."""
	m = EXACT_READ_RE.match(rawRight)
	if not m:
		return 0
	size = readSizes.get(m.group(1), 0)
	return len(m.group(2)) if (size and m.group(2)) else size


def _syncOutputAttrs(wanted, outNames):
	"""Declare NEW output attributes on the GLSL POP, and tell it which attributes
	the expressions write to (par.outputattrs).

	Without the declaration, `myval = _PointU * 5.0` fails with "'myval' :
	undeclared identifier": a GLSL POP needs the TYPE of a new attribute, which
	for an existing attribute comes from the input and for a new one from
	nowhere. Without the name list nothing is allocated for writing at all.

	wanted:   [(name, numComponents), ...] attributes the input lacks, in order.
	outNames: base names of every OutAttr line ('P' for `P.y = ...`), in order.
	          The stock component derives this list with a par expression
	          (`...split('=')[0]`), which yields 'P.y' for a component target,
	          so P was never allocated. The generator knows the parsed left
	          sides, so it owns the list (v1.6); the build script clears the
	          stock expression.

	Writes parameters from inside a cook, so every write is GUARDED: only touch
	a par when its value actually differs. An unconditional write re-triggers
	this cook and spins forever (same reason `_header` guards its write to
	mathmix_helpers)."""
	glsl = op(GLSL_OP)
	if glsl is None:
		return
	changed = False
	# 1) which attributes are written
	names = ' '.join(outNames)
	p = glsl.par['outputattrs']
	if p is not None and (p.mode != ParMode.CONSTANT or p.eval() != names):
		p.val = names                            # .val also forces CONSTANT mode
		changed = True
	# 2) type declaration for the attributes the input does not have
	try:
		seq = glsl.seq.attr          # par.attr is a Sequence par: assigning .val does NOT
	except Exception:                # take (it reads 0 even when blocks exist) — use numBlocks
		seq = None
	if seq is not None:
		target = [(n, str(c)) for n, c in wanted]
		current = []
		try:
			for i in range(seq.numBlocks):
				nm = glsl.par['attr%dcustomname' % i]
				if nm is None:
					break
				nc = glsl.par['attr%dnumcomps' % i]
				current.append((nm.eval(), str(nc.eval()) if nc is not None else '1'))
		except Exception:
			current = None
		if current is not None and [c for c in current if c[0]] != target:
			try:
				seq.numBlocks = max(len(target), 1)
				for i, (name, comps) in enumerate(target):
					for suffix, value in (('name', 'custom'), ('customname', name),
										  ('type', 'float'), ('numcomps', comps)):
						q = glsl.par['attr%d%s' % (i, suffix)]
						if q is not None:
							q.val = value
				for i in range(len(target), seq.numBlocks):   # stale slots: blank the name so the
					q = glsl.par['attr%dcustomname' % i]      # POP stops emitting a dropped attribute
					if q is not None:
						q.val = ''
				changed = True
			except Exception:
				pass
	if not changed:
		return
	# A CHANGED declaration only takes effect on the NEXT cook: the GLSL POP is
	# compiling this very frame against the OLD width, so a fresh vec4 attribute
	# is still declared float -> "cannot convert from 'vec4' to 'float'". Nothing
	# cooks afterwards, so that error would sit there until someone recooks by
	# hand — which is exactly what happened when toggling OutAttr -> Local ->
	# OutAttr. One deferred cook clears it. Only reached when something actually
	# changed (the guards above), so this cannot spin.
	run('args[0].cook(force=True)', glsl, delayFrames=1, fromOP=glsl)


def _cleanCompileText(text: str) -> str:
	for junk in INFO_JUNK:
		text = text.replace(junk, '')
	return text.strip()


def UpdateInfo(compileText: str | None = None) -> None:
	"""Write the component's Info par: compile result of glsl1 + the lines this generator
	ignored on its last cook (13). Two callers, two halves of the truth:
	  - onCook, deferred by one frame via run(): the ignored list changed;
	  - datexec1.onTableChange: glsl1_info changed, the compile text is fresh.
	Never called from inside a cook (reading glsl1_info there would close a dependency
	loop back to script1), and written only when the text differs."""
	if compileText is None:
		infoDAT = op(INFO_DAT)
		compileText = infoDAT.text if infoDAT is not None else ''
	text = _cleanCompileText(compileText)
	if _ignored:                                                      # first: the Info field is narrow
		items = ', '.join(f"line {i} '{line}': {why}" for i, line, why in _ignored)
		text = f"IGNORED {items} | {text}"
	comp = parent.ExpressionPOP
	if comp.par.Info.eval() != text:
		comp.par.Info = text


def onCook(scriptOp):
	if not scriptOp.inputs:
		return
	inPOP = op('in1')
	if inPOP is None:
		return
	inDAT = scriptOp.inputs[0]
	attribs = list(inPOP.pointAttributes)
	attribNames = [a.name for a in attribs]
	inputAttribs = _inputAttribs(inPOP)                                   # (11) {k: {name: attr}}
	# (12) A bare name belongs to the FIRST input that carries it: input 0 where it exists,
	# otherwise the lowest-numbered input that does. That is precisely the rule the Use As
	# line draws, which is why a name shown without a prefix can be typed without one.
	resolve, arrayNames, readSizes = {}, {}, {}
	for k in sorted(inputAttribs):
		for n, a in inputAttribs[k].items():
			resolve.setdefault(n, k)
			size = int(getattr(a, 'size', 1) or 1)
			readSizes.setdefault(n, size)
			if _isArrayAttrib(a):
				arrayNames.setdefault(n, (k, n))
			if k > 0:                                                     # explicit spelling always works
				readSizes[f'in{k}_{n}'] = size
				if _isArrayAttrib(a):
					arrayNames[f'in{k}_{n}'] = (k, n)
	mode = _mismatchMode()
	usedInputs = set()
	inExpressions = (inDAT.row('Expr_expression', val=True) or [])[1:]
	inLeftmodes = (inDAT.row('Expr_leftmode', val=True) or [])[1:]

	dynamic = _dynamicBuiltins(inPOP, inExpressions)
	glsl_expressions = {}
	array_helpers = {}
	localTypes = {}          # local name -> components, for width inference
	newAttrs = {}            # name -> components for attributes the input lacks (in order)
	outNames = []            # base name of every OutAttr line, in order, no duplicates
	ignored = []             # (13) lines that produce no code, reported in Info
	for idx, inExpression in enumerate(inExpressions):
		line = re.sub(r'//.*$', '', str(inExpression)).strip()      # (6) drop // comments
		if not line:
			continue
		m = ASSIGN_RE.search(line)                                   # (2) first real '='
		if m is None:
			ignored.append((idx, line[:40], IGNORE_NO_ASSIGN))       # (13) `dwadwadw`
			continue
		leftSide = line[:m.start()].strip()
		rightSide = line[m.end():].strip().rstrip(';').strip()       # (6) tolerate trailing ';'
		if not leftSide:
			ignored.append((idx, line[:40], IGNORE_NO_LEFT))         # (13) `= P * 2.0`
			continue
		if not rightSide:
			ignored.append((idx, line[:40], IGNORE_NO_RIGHT))        # (13) `P =`
			continue
		rawRight = rightSide            # (8) width inference reads the UNSUBSTITUTED text
		rightSide = substitute_builtins(rightSide, dynamic)                   # (4)+(7)
		rightSide = substitute_arrays(rightSide, arrayNames, array_helpers, usedInputs)   # (3)+(11)
		locals_ = frozenset(localTypes)                                  # (12) locals shadow attributes
		rightSide = substitute_input_attribs(rightSide, inputAttribs, mode, usedInputs, locals_)   # (11) in1_P
		rightSide = substitute_attribs(rightSide, resolve, usedInputs, locals_)   # (5)+(12) bare -> first input
		leftMode = _leftMode(inLeftmodes[idx] if idx < len(inLeftmodes) else 0)
		if leftMode:                                                 # (8) remember locals
			nm, comps = _localDecl(leftSide)
			if nm:
				localTypes[nm] = comps
		else:                                                        # (8)+(9) collect written attributes
			typedComps = 0
			parts = leftSide.split()
			if len(parts) == 2 and parts[0] in TYPE_COMPS:           # (10) 'vec3 offset' names the width
				typedComps, leftSide = TYPE_COMPS[parts[0]], parts[1]
			base, rest = _splitTarget(leftSide)                      # 'P.y' / 'C[0]' -> 'P' / 'C'
			if base and base not in outNames:
				outNames.append(base)
			if base and base not in attribNames:                     # new: wide enough for RHS AND target
				exact = _exactReadWidth(rawRight, readSizes)               # (11)+(12) `cp = P` / `cp = in1_P` -> 3
				need = typedComps or max(exact or _numComps(rawRight, localTypes), _minCompsForTarget(rest))
				newAttrs[base] = max(newAttrs.get(base, 1), need)
		define_name, define_text, define_expression = make_glsl_define(idx, leftSide, rightSide, leftMode=leftMode)
		glsl_expressions[define_name] = (define_text, define_expression)

	_syncOutputAttrs(list(newAttrs.items()), outNames)                # (8)+(9) declare + allocate on glsl1
	header = _header(array_helpers)                                   # (1) library out of sight
	code = SHADER_TEMPLATE.replace('<INSERT DEFINES HERE>\n', f'{header}\n' if header else '').lstrip('\n')
	indexLines = _inputIndexLines(usedInputs, mode)                   # (11) _n1/_id1 per extra input used
	code = code.replace('<INPUT_INDICES_HERE>\n\t', f'{indexLines}\n\t' if indexLines else '')
	expressions_text = '\n\t'.join([f'{define_expression};' for define_text, define_expression in glsl_expressions.values()])
	if ignored:                                                       # (13) visible in View = code as well
		notes = '\n\t'.join(f"// ignored line {i} '{line}': {why} -- write  target = expression" for i, line, why in ignored)
		expressions_text = f'{notes}\n\t{expressions_text}' if expressions_text else notes
	code = code.replace('<SUBSTITUTE_EXPRESSIONS_HERE>', expressions_text)
	scriptOp.text = code                                              # assigned last: a bad line never empties the shader
	if ignored != _ignored:                                           # (13) the list changed: show it
		_ignored[:] = ignored
		# Deferred, NOT called here: UpdateInfo() reads glsl1_info, and a read inside this
		# cook would make script1 depend on glsl1_info -> glsl1 -> mathmix_shader -> null_glsl
		# -> ... -> script1, a cook dependency loop. One frame later it is a plain read.
		run('args[0].module.UpdateInfo()', me, delayFrames=1, fromOP=scriptOp)
	return


def onGetCookLevel(scriptOp):
	"""
	sets the scriptOp's cook level, the conditions necessary to cause a cook.
	Return one of the following:
		CookLevel.AUTOMATIC - inputs changed and output being used. TD default behavior.
		CookLevel.ON_CHANGE - inputs changed, output used or not.
		CookLevel.WHEN_USED - every frame when output is being used
		CookLevel.ALWAYS - every frame
	"""
	return CookLevel.AUTOMATIC
