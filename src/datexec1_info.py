# datexec1: glsl1_info changed -> refresh the Info par.
# The generator (script1_callbacks) owns the Info text since v1.9: compile result
# plus the lines it ignored (no '=' ...). Handing the fresh compile text over here
# keeps the two in one place. The stock behaviour stays as a fallback in case the
# generator DAT is missing or an older one is dropped in.

def onTableChange(dat, prevDAT, info):
	gen = op('script1_callbacks')
	if gen is not None and hasattr(gen.module, 'UpdateInfo'):
		gen.module.UpdateInfo(dat.text)
		return
	text = dat.text
	for junk in ('=============', '==========', 'Compute Shader Compile Results:'):
		text = text.replace(junk, '')
	parent.ExpressionPOP.par.Info = text
	return
