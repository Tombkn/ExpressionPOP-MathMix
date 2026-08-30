# ---------------------------------------------------------------------------
#  build_expressionpop_mathmix.py — builds ONE Expression POP with the Math Mix
#  library built in (ExpressionPOP_MathMix.tox). No installer, no install steps.
#
#  Base: the Function Store Expression POP template (FunctionStore_tools_2023).
#  Run in the TouchDesigner textport, with the Function Store tools loaded:
#
#     exec(open(r'<repo>\src\build_expressionpop_mathmix.py', encoding='utf-8').read())
#
#  REPO below must point at the folder that holds README.md / README_DE.md /
#  SELFTEST.md and the src/ folder (mathmix_lib.glsl, script1_callbacks_patched.py).
#  The finished .tox is saved next to the READMEs.
# ---------------------------------------------------------------------------
import os

REPO    = r'C:\VisualStuff\Touchdesigner All\AllFiles\Cursor Base\touchdesigner_project_folder\Patreon\PopToGLSL\with_expressionPOP_MathMixLib'
SRC_DIR = os.path.join(REPO, 'src')     # mathmix_lib.glsl, script1_callbacks_patched.py
DOC_DIR = REPO                          # README.md, README_DE.md, SELFTEST.md
OUT_TOX = os.path.join(REPO, 'ExpressionPOP_MathMix.tox')

SRC     = '/FunctionStore_tools_2023/OpTemplates/OPTemplates1/mathmixPOP/expression/expression'
PARENT  = '/project1'
NAME    = 'ExpressionPOP_MathMix'
VERSION = '1.6'


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
comp.comment = 'Function Store Expression POP mit fest eingebauter Math-Mix-GLSL-Bibliothek'

gen      = comp.op('script1_callbacks')
code_dat = comp.op('null_glsl')
glsl     = comp.op('glsl1')

# 1) keep the stock generator as a reference, BEFORE it is overwritten
if comp.op('script1_callbacks_orig') is None and 'mathmix_lib' not in gen.text:
    bak = comp.copy(gen, name='script1_callbacks_orig')
    bak.nodeX, bak.nodeY = gen.nodeX + 200, gen.nodeY - 150
    bak.comment = 'unveraenderter Function-Store-Generator (Referenz)'


def _ensure(opType, name, x, y):
    o = comp.op(name)
    if o is None:
        o = comp.create(opType, name)
        o.nodeX, o.nodeY = x, y
    return o


# 2) the library + a parking DAT for the generated array helpers
lib = _ensure(textDAT, 'mathmix_lib', gen.nodeX, gen.nodeY - 150)
lib.text = _read(SRC_DIR, 'mathmix_lib.glsl')
lib.comment = 'Math-Mix-GLSL-Bibliothek — wird vor den generierten Code gehaengt'
helpers = _ensure(textDAT, 'mathmix_helpers', gen.nodeX, gen.nodeY - 250)
helpers.comment = 'pro Cook erzeugt: arrayadd(Name) & co. Leer, solange keine Expression sie nutzt.'

# 3) the library reaches the compiler without showing up in View=code
shader = _ensure(mergeDAT, 'mathmix_shader', code_dat.nodeX + 200, code_dat.nodeY - 150)
shader.comment = 'was glsl1 kompiliert: mathmix_lib + Array-Helfer + null_glsl'
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

# 5) ship the docs inside the component
for nm, fn, dy in (('readme', 'README.md', 0), ('readme_de', 'README_DE.md', -150), ('selftest', 'SELFTEST.md', -300)):
    d = _ensure(textDAT, nm, gen.nodeX + 400, gen.nodeY + dy)
    d.text = _read(DOC_DIR, fn)

# 6) version on the EXISTING About page (no extra page, no check button: a pulse
#    par without an extension would be dead, and compile errors already show in
#    the Info par / out_info)
about = [pg for pg in comp.customPages if pg.name == 'About']
if about and comp.par['Mathmixversion'] is None:
    p = about[0].appendStr('Mathmixversion', label='Math Mix Library')[0]
    p.readOnly = True
    p.startSection = True
    p.help = 'Version der fest eingebauten Math-Mix-GLSL-Bibliothek.'
p = comp.par['Mathmixversion']
if p is not None:
    p.default = VERSION
    p.val = VERSION

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

# 8) save the .tox next to the READMEs
comp.save(OUT_TOX)

print(f'built: {comp.path}')
print(f'  mathmix_lib      {len(lib.text)} chars')
print(f'  generator        {len(gen.text)} chars (stock generator kept: {comp.op("script1_callbacks_orig") is not None})')
print(f'  glsl1.computedat {glsl.par.computedat.eval()}')
print(f'  children         {len(comp.children)}')
print(f'  saved            {OUT_TOX} ({os.path.getsize(OUT_TOX)} bytes)')
