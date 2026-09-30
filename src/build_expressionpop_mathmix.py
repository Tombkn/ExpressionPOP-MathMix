# ---------------------------------------------------------------------------
#  build_expressionpop_mathmix.py — builds ONE Expression POP with the Math Mix
#  library built in (ExpressionPOP_MathMix.tox). No installer, no install steps.
#
#  Base: the Function Store Expression POP template (FunctionStore_tools_2023).
#  Run in the TouchDesigner textport, with the Function Store tools loaded:
#
#     exec(open(r'<repo>\src\build_expressionpop_mathmix.py', encoding='utf-8').read())
#
#  REPO below must point at the folder that holds README.md / SELFTEST.md
#  and the src/ folder (mathmix_lib.glsl, script1_callbacks_patched.py, datexec1_info.py, use_as.py).
#  The finished .tox is saved next to the README.
# ---------------------------------------------------------------------------
import os

REPO    = r'C:\VisualStuff\Touchdesigner All\AllFiles\Cursor Base\touchdesigner_project_folder\Patreon\PopToGLSL\with_expressionPOP_MathMixLib'
SRC_DIR = os.path.join(REPO, 'src')     # mathmix_lib.glsl, script1_callbacks_patched.py, datexec1_info.py
DOC_DIR = REPO                          # README.md, SELFTEST.md
OUT_TOX = os.path.join(REPO, 'ExpressionPOP_MathMix.tox')

SRC     = '/FunctionStore_tools_2023/OpTemplates/OPTemplates1/mathmixPOP/expression/expression'
PARENT  = '/project1'
NAME    = 'ExpressionPOP_MathMix'
VERSION = '1.9.1'


def _read(folder, name):
    return open(os.path.join(folder, name), encoding='utf-8').read()


parent, src = op(PARENT), op(SRC)
if parent is None or src is None:
    raise RuntimeError(f'PARENT ({PARENT}) or SRC ({SRC}) not found')

old = parent.op(NAME)
if old is not None:
    old.destroy()

comp = parent.copy(src, name=NAME)
comp.nodeX, comp.nodeY = 400, 400
comp.color = (0.95, 0.70, 0.25)
comp.comment = 'Function Store Expression POP with the Math Mix GLSL library built in'

gen      = comp.op('script1_callbacks')
code_dat = comp.op('null_glsl')
glsl     = comp.op('glsl1')

# 1) keep the stock generator as a reference, BEFORE it is overwritten
if comp.op('script1_callbacks_orig') is None and 'mathmix_lib' not in gen.text:
    bak = comp.copy(gen, name='script1_callbacks_orig')
    bak.nodeX, bak.nodeY = gen.nodeX + 200, gen.nodeY - 150
    bak.comment = 'stock Function Store generator, unchanged (reference)'


def _ensure(opType, name, x, y):
    o = comp.op(name)
    if o is None:
        o = comp.create(opType, name)
        o.nodeX, o.nodeY = x, y
    return o


# 2) the library + a parking DAT for the generated array helpers
lib = _ensure(textDAT, 'mathmix_lib', gen.nodeX, gen.nodeY - 150)
lib.text = _read(SRC_DIR, 'mathmix_lib.glsl')
lib.comment = 'Math Mix GLSL library, prepended to the generated code'
helpers = _ensure(textDAT, 'mathmix_helpers', gen.nodeX, gen.nodeY - 250)
helpers.comment = 'generated per cook: arrayadd(Name) & co. Empty until an expression uses one.'

# 3) the library reaches the compiler without showing up in View=code
shader = _ensure(mergeDAT, 'mathmix_shader', code_dat.nodeX + 200, code_dat.nodeY - 150)
shader.comment = 'what glsl1 compiles: mathmix_lib + array helpers + null_glsl'
for i, s in enumerate((lib, helpers, code_dat)):
    shader.inputConnectors[i].connect(s)
glsl.par.computedat = shader

# 4) the patched generator
gen.text = _read(SRC_DIR, 'script1_callbacks_patched.py')

# 4b) v1.6: the generator owns glsl1's Output Attributes list. The stock par
#     expression (`...split('=')[0]`) yields 'P.y' for `P.y = ...`, so P was never
#     allocated for writing. Constant + empty; the generator fills it per cook.
glsl.par.outputattrs.mode = ParMode.CONSTANT
glsl.par.outputattrs.val = ''

# 4c) v1.9: the generator owns the Info par (compile result + ignored lines).
#     The stock datexec1 copied glsl1_info into Info on its own; it now hands the
#     fresh compile text to the generator instead, so both halves land in one text.
info_exec = comp.op('datexec1')
if info_exec is not None:
    info_exec.text = _read(SRC_DIR, 'datexec1_info.py')
    info_exec.comment = 'glsl1_info changed -> script1_callbacks.UpdateInfo(): compile result + ignored lines'

# 5) ship the docs inside the component
for nm, fn, dy in (('readme', 'README.md', 0), ('selftest', 'SELFTEST.md', -300)):
    d = _ensure(textDAT, nm, gen.nodeX + 400, gen.nodeY + dy)
    d.text = _read(DOC_DIR, fn)
if (old_de := comp.op('readme_de')) is not None:
    old_de.destroy()

# 6) version + Readme pulse on the EXISTING About page (no extra page: compile
#    errors already show in the Info par / out_info; the pulse is wired by
#    parexec_readme below)
about = [pg for pg in comp.customPages if pg.name == 'About']
if about:
    if comp.par['Mathmixversion'] is None:
        p = about[0].appendStr('Mathmixversion', label='Math Mix Library')[0]
        p.readOnly = True
        p.startSection = True
        p.help = 'Version of the built-in Math Mix GLSL library.'
    if comp.par['Openreadme'] is None:
        p = about[0].appendPulse('Openreadme', label='Readme')[0]
        p.help = 'Open the built-in README DAT.'
p = comp.par['Mathmixversion']
if p is not None:
    p.default = VERSION
    p.val = VERSION

# 6c) About > Readme opens the readme DAT
readme = comp.op('readme')
pe = _ensure(
    parameterexecuteDAT,
    'parexec_readme',
    readme.nodeX + 200 if readme else gen.nodeX + 600,
    readme.nodeY if readme else gen.nodeY,
)
pe.text = (
    "def onPulse(par):\n"
    "\tif (readme := parent().op('readme')):\n"
    "\t\treadme.openViewer(unique=True)\n"
    "\treturn\n"
)
pe.par.op.expr = 'parent()'
pe.par.fromop.expr = 'parent()'
pe.par.pars = 'Openreadme'
pe.par.onpulse = True
pe.par.valuechange = False
pe.comment = 'About > Readme opens the readme DAT'

# 9) v1.8: several POP inputs — Dan's MultiTop pattern. A Sequence 'Inputs' (one block per
#    connector) drives a Replicator that stamps in2, in3 ... from in1 and wires each to the
#    next connector of glsl1. Inside a line the second input's attributes are in1_P,
#    in1_Color ... (Math Mix POP naming: the prefix counts from 0, the first input stays plain).
in1 = comp.op('in1')
if comp.par['Inputs'] is None:
    ipage = comp.appendCustomPage('Inputs')
    ipage.appendSequence('Inputs', label='Input')
    ipage.appendPOP('Pop', label='Input POP')       # base names; blockSize pulls them into the sequence
    ipage.appendStr('Names', label='Use As')
    comp.seq.Inputs.blockSize = 2
    comp.seq.Inputs.numBlocks = 1                   # block 0 IS the connector the node already has
    m = ipage.appendMenu('Lengthmismatch', label='Length Mismatch')[0]
    m.menuNames = ['hold', 'repeat', 'zero', 'one', 'none']
    m.menuLabels = ['Hold', 'Repeat', 'Zero', 'One', 'None']
    m.default = 'repeat'
    m.val = 'repeat'
    m.startSection = True

# 9a) Settings: how the component presents itself, not what it computes.
if comp.par['Showtypes'] is None:
    spage = comp.appendCustomPage('Settings')
    t = spage.appendToggle('Showtypes', label='Types in Use As')[0]
    t.default = True
    t.val = True
comp.par.Showtypes.help = (
    'Show each attribute’s GLSL type behind its name on the Inputs page, P[vec3] instead of P. '
    'That is the word a Local line needs, so leave it on while writing lines; turn it off for a '
    'short list of bare names to copy from.'
)
comp.sortCustomPages('Custom', 'Inputs', 'Settings', 'About')
comp.par.Inputs.help = (
    'One block per POP connector. Block 0 is the connector the node already has; + adds the second '
    'input, and so on. Use As shows how to reach each input in an expression line.'
)
comp.par.Inputs0pop.help = (
    'A POP that feeds this connector without a wire; clearing it disconnects the connector. '
    'Greyed out on block 0 (the connector the node already has) and whenever a wire on the node '
    'occupies this connector — the wire wins, same as on the Math Mix POP.'
)
comp.par.Inputs0names.help = (
    'Read-only. The point attributes of the POP on this connector, each written the way you type it '
    'in a line, with its GLSL type in brackets behind it. A name only carries its in1_ / in2_ prefix '
    'where an EARLIER input has the same attribute; a name unique to this input is typed bare. '
    'The type is the word a Local line needs: P[vec3] means "vec3 d = P * 2.0". Settings can switch '
    'the types off. Stretch the dialog to see them all.'
)
comp.par.Lengthmismatch.help = (
    'What a point reads from an input that has FEWER points, as on the Math Mix POP. '
    'Hold: the last point. Repeat: wrap around. Zero / One: that constant. None: read raw. '
    'A single-point input is always a constant.'
)

# 9b) a 1-point stand-in for an Inputs block whose connector is still empty.
#     Without it, pressing + put a 0-element inPOP on glsl1 and the shader stopped compiling
#     with "array size must be a positive integer" -- TouchDesigner cannot declare buffers for
#     an input with no elements. That hit the normal order of work (press +, THEN wire), so
#     every extra input goes through a Switch POP that falls back to this one point. A
#     single-point input is a constant anyway (Length Mismatch), so an unwired extra input
#     reads 0.0 instead of turning the node red.
fallback = _ensure(pointgeneratorPOP, 'input_fallback', in1.nodeX - 200, in1.nodeY - 200)
fallback.par.numpoints = 1
# v1.9.1: the one point sits at the ORIGIN. A Point Generator with its default random sphere
# put the stand-in at a random position, so an empty connector read e.g. (0.33, -0.39, 0.53)
# for in1_P instead of the 0.0 the docs promised. Radius 0 + random off = P exactly (0, 0, 0);
# N stays a finite unit vector, so in1_N still compiles.
fallback.par.random = False
for k in ('radiusx', 'radiusy', 'radiusz'):
    setattr(fallback.par, k, 0)
fallback.comment = 'what an extra input reads while its connector is empty (1 point at the origin = constant 0.0)'

rep = _ensure(replicatorCOMP, 'replicator_in', in1.nodeX - 400, in1.nodeY + 200)
rep.par.method = 'bynum'
rep.par.numreplicants.expr = 'max(1, parent().seq.Inputs.numBlocks)'
rep.par.opprefix = 'in'
rep.par.master = 'in1'
rep.par.destination.expr = 'parent()'
rep.par.layout = 'off'                              # positions come from the callback
rep.par.callbacks = 'replicator_in_callbacks'
rep.comment = 'one inPOP per block of the Inputs sequence; in1 is the master and stays'
# TD spawns this DAT (docked) together with the Replicator, at an arbitrary spot:
# _ensure only positions what it creates, so place it every time.
cb = _ensure(textDAT, 'replicator_in_callbacks', rep.nodeX, rep.nodeY - 200)
cb.nodeX, cb.nodeY = rep.nodeX, rep.nodeY - 200
cb.text = '''# replicator_in: one inPOP per block of the Inputs sequence (Dan's MultiTop pattern).
# in1 is the master and stays and goes straight to glsl1; in2, in3 ... are stamped from it,
# stacked above in1, and reach glsl1 through their own guard{n} Switch POP.
#
# The guard is what keeps the node out of the red between "press +" and "wire it": an inPOP
# whose connector is empty has 0 elements, and TouchDesigner cannot build buffer declarations
# for that ("array size must be a positive integer"), which killed the whole shader even when
# no line mentioned that input. The Switch falls back to input_fallback, a single point, and a
# single-point input is a constant -- so an unwired extra input reads 0.0 instead of failing.

ROW_X = (1075, 1275, 1475)     # sel{n} / in{n} / guard{n}, left to right
ROW_Y = -2000                  # clear of everything above; the network's own ops end at -1700
ROW_STEP = -200                # one row per extra input, downwards


def _feedFor(c):
	"""Everything that decides what input {n} actually reads, built on demand.

	    sel{n}  ---\\
	    in{n}   ----> guard{n} --> glsl1
	    fallback --/

	in{n} is the connector on the node, sel{n} follows the block's Input POP field, and
	input_fallback is one point. The Switch prefers the wire, then the field, then the
	fallback. Two reasons for this shape:
	  - The field must NOT wire the connector. If it does, "wired on the node" and "typed in
	    the field" are the same thing in the data model, and the rule "a wire greys the field
	    out" locks the field the moment you use it, with no way back.
	  - An input with 0 elements cannot be declared in the shader at all ("array size must be
	    a positive integer") and takes the whole node down, so an empty input never reaches
	    glsl1 -- the single point stands in, and a single-point input is a constant anyway.
	"""
	n = c.digits                                       # in2 -> 2
	k = n - 1                                          # -> block 1, prefix in1_
	row = ROW_Y + ROW_STEP * k

	sel = op('sel%d' % n) or parent().create(selectPOP, 'sel%d' % n)
	sel.nodeX, sel.nodeY = ROW_X[0], row
	e = 'parent().par.Inputs%dpop.eval()' % k
	if sel.par.pop.expr != e:
		sel.par.pop.expr = e
	sel.comment = 'whatever the Input POP field of block %d names (empty if unset)' % k

	c.nodeX, c.nodeY = ROW_X[1], row
	c.par.label = 'in%d_' % k

	g = op('guard%d' % n) or parent().create(switchPOP, 'guard%d' % n)
	g.nodeX, g.nodeY = ROW_X[2], row
	g.inputConnectors[0].connect(c)
	g.inputConnectors[1].connect(sel)
	if (fb := op('input_fallback')) is not None:
		g.inputConnectors[2].connect(fb)
	# An EXPRESSION on purpose: a wire pulled on the component fires no callback, but it does
	# dirty in{n}, so the Switch re-evaluates and flips on its own (verified in both directions).
	expr = "0 if op('in%d').numPoints() else (1 if op('sel%d').numPoints() else 2)" % (n, n)
	if g.par.index.expr != expr:
		g.par.index.expr = expr
	g.comment = 'the wire on in%d, else the Input POP field, else the 1-point fallback' % n
	return g


def onRemoveReplicant(comp, replicant):
	if replicant.name == 'in1':
		return
	for nm in ('guard%d' % replicant.digits, 'sel%d' % replicant.digits):
		if (o := op(nm)) is not None:
			o.destroy()
	replicant.destroy()
	return


def onReplicate(comp, allOps, newOps, template, master):
	glsl = op('glsl1')
	for c in sorted(newOps, key=lambda o: o.digits):   # in2 before in3: connectors grow one at a time
		k = c.digits - 1                              # in2 -> connector 1 -> in1_ prefix
		if glsl is not None and k < len(glsl.inputConnectors):
			glsl.inputConnectors[k].connect(_feedFor(c))
	# a block added with + copies enableExpr but NOT the Use As expression -- restyle here,
	# this callback is the one thing that reliably runs when the block count changes.
	if (pe := op('parexec_inputs')) is not None:
		pe.module.StyleBlocks(parent())
	return
'''
cb.comment = 'replicator_in callbacks: wire in2, in3 ... to glsl1'

# 9c) the Use As line lives in its own plain textDAT: a parameter reading a module makes the
#     parameter depend on that DAT, and pointing it at parexec_inputs (which itself depends on
#     the parameters it watches) closes a cook dependency loop. A plain DAT has no such edge.
ua = _ensure(textDAT, 'use_as', rep.nodeX + 400, rep.nodeY)
ua.nodeX, ua.nodeY = rep.nodeX + 400, rep.nodeY
ua.text = _read(SRC_DIR, 'use_as.py')     # v1.9: attributes via in{n} / sel{n}, never the wire's owner
ua.comment = 'builds the read-only Use As line of each Inputs block'

pi = _ensure(parameterexecuteDAT, 'parexec_inputs', rep.nodeX + 200, rep.nodeY)
pi.text = '''# Inputs page. A POP in a sequence block feeds that connector without a wire
# (Dan's MultiTop pattern); Length Mismatch rebuilds the shader. StyleBlocks() keeps
# every block's read-only "Use As" line and the greying of "Input POP" in sync.

# Read-only per block: the REAL point attributes of whatever feeds this input, each with the
# prefix you type in a line (block 0 plain, block 1 in1_, block 2 in2_ -- Math Mix POP naming),
# then the op's name. The wire on the node wins over the field, same order the guard switches in.
# Nothing at all -> only the prefix, no made-up attribute list. pointAttributes is metadata (no
# readback) and a cook dependency, so the line follows an upstream Attribute POP as well.
# The Use As line is built in the 'use_as' DAT, not inline and NOT in this DAT: it has to look
# at every EARLIER input to decide whether a name needs its prefix, which is too much for one
# expression -- and reading THIS module from a parameter would close a cook dependency loop,
# because a Parameter Execute DAT already depends on the parameters it watches.
NAMES_EXPR = "me.op('use_as').module.UseAs(me, me.curBlock.index)"

# Greyed out like the Math Mix POP: always on block 0 (the connector the node already has), and
# on any block whose connector carries a wire -- the wire wins, so the field cannot contradict it.
# This is only safe because the field does NOT wire the connector any more: it feeds sel{n}, a
# Select POP inside the component (see replicator_in_callbacks). When the field made the wire
# itself, as it did before, "wired" and "typed" are the same thing in the data model and the
# field greys itself out the moment you set it, with no way back.
ENABLE_EXPR = (
	"me.curBlock.index > 0 and ("
	"me.curBlock.index >= len(me.inputConnectors)"
	" or not me.inputConnectors[me.curBlock.index].connections)"
)


def StyleBlocks(comp=None):
	"""Apply the read-only Use As expression and the enable rule to every block.

	A block added with + inherits enableExpr and readOnly, but NOT the expression
	(it arrives in CONSTANT mode and reads empty), so this runs again after every
	block count change -- called from replicator_in_callbacks.onReplicate.
	Guarded: only write when the value actually differs, an unconditional write recooks."""
	comp = comp or parent()
	for block in comp.seq.Inputs.blocks:
		p = block.par.Names
		if p is not None and p.expr != NAMES_EXPR:
			p.expr = NAMES_EXPR
			p.readOnly = True
		q = block.par.Pop
		if q is not None and q.enableExpr != ENABLE_EXPR:
			q.enableExpr = ENABLE_EXPR
	return


def onValueChange(par, prev):
	"""Both Input POP and Length Mismatch only need the shader written again.

	Nothing is wired here any more. The Input POP field reaches its input through
	sel{n} (a Select POP whose POP parameter follows this field), so setting it
	leaves the component's connector untouched -- which is what lets a wire on the
	node, and only a wire, grey the field out.
	Deferred by one frame: the Select POP picks up the new POP on the next cook, and
	the generator has to read the attributes AFTER that, not before."""
	if (gen := op('script1')) is not None:
		run('args[0].cook(force=True)', gen, delayFrames=1, fromOP=gen)
	return
'''
pi.par.op.expr = 'parent()'
pi.par.fromop.expr = 'parent()'
pi.par.pars = 'Inputs*pop Lengthmismatch'
pi.par.valuechange = True
pi.comment = 'Inputs > POP wires the connector; Length Mismatch recooks; StyleBlocks() styles the blocks'

pi.module.StyleBlocks(comp)         # style block 0 now; + restyles via the replicator callback

# 6b) ship with one empty expression line and the viewer on the POP
comp.seq.Expr.numBlocks = 1
if comp.par['Expr0expression'] is not None:
    comp.par.Expr0expression = ''
    comp.par.Expr0leftmode = 0
comp.par.View = comp.par.View.default

# 7) rebuild everything once
for n in ('script1', 'null_glsl', 'mathmix_shader', 'glsl1'):
    o = comp.op(n)
    if o is not None:
        o.cook(force=True)

# 8) save the .tox next to the README
comp.save(OUT_TOX)

print(f'built: {comp.path}')
print(f'  mathmix_lib      {len(lib.text)} chars')
print(f'  generator        {len(gen.text)} chars (stock generator kept: {comp.op("script1_callbacks_orig") is not None})')
print(f'  glsl1.computedat {glsl.par.computedat.eval()}')
print(f'  inputs           {comp.seq.Inputs.numBlocks} block(s), {len(comp.inputConnectors)} connector(s), mismatch={comp.par.Lengthmismatch.eval()}')
print(f'  children         {len(comp.children)}')
print(f'  saved            {OUT_TOX} ({os.path.getsize(OUT_TOX)} bytes)')
