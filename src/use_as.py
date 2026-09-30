# Builds the read-only "Use As" line of each Inputs block. Called from the parameter
# expression that StyleBlocks() installs; see parexec_inputs.


def _sourceFor(comp, k):
	"""(name to show, POP whose attributes the shader sees) for input k, or (None, None).
	Wire first, then the block's Input POP field -- the order guard{n} switches in, so the
	page never claims something the shader disagrees with.

	The attributes are read from the POP INSIDE the component -- in1 / in{k+1} for a wire,
	sel{k+1} for the field -- never from the wire's owner. A wire can come out of a COMP
	(another Expression POP, a Base with an Out POP), and a COMP has no pointAttributes:
	reading them there turned the Use As line red (v1.9)."""
	conns = comp.inputConnectors
	if k < len(conns) and conns[k].connections:
		src = conns[k].connections[0].owner
		inside = comp.op('in%d' % (k + 1))
		return src.name, (inside if inside is not None else src)
	seq = comp.seq.Inputs
	if k < seq.numBlocks:
		target = seq[k].par.Pop.eval()
		if target is not None:
			if target.isCOMP:                      # the Select POP behind the field takes POPs only
				return target.name + ' is a COMP: wire it to the connector instead', None
			inside = comp.op('sel%d' % (k + 1))
			return target.name, (inside if inside is not None else target)
	return None, None


def _attribs(pop):
	"""Point attributes of pop, or [] when it has none (a COMP, or nothing cooked yet)."""
	try:
		return list(pop.pointAttributes)
	except AttributeError:
		return []


def _glslType(a):
	"""The attribute's type, spelled the way you type it on a Local line: one value is
	float / int, more are vec3 / ivec2, an array adds its length -> float[4]."""
	base = (('int' if a.type is int else 'float') if a.size == 1
			else ('ivec' if a.type is int else 'vec') + str(a.size))
	return base + ('[%d]' % a.arraySize if a.isArray else '')


def UseAs(comp, k):
	"""The Use As line of block k: how to reach this input, and what is on it.

	A name carries its in{k}_ prefix ONLY where an EARLIER input has the same attribute --
	the one case where the bare name is already taken. A name unique to this input (`dick` on
	the second input, when the first has none) stays bare and may be typed bare. The generator
	resolves a bare name to the FIRST input carrying it, which is the same rule seen from the
	other side, so the line and the shader can never disagree.

	The type in brackets sits tight AFTER the name: the name is what you scan for, so it comes
	first and stays one unbroken token. Settings > Types in Use As switches the brackets off.
	Reads parameters and attribute metadata only, never point values."""
	prefix = '' if k == 0 else 'in%d_' % k
	name, pop = _sourceFor(comp, k)
	if pop is None:
		return (prefix or '(no prefix)') + '   <-   ' + (name or '(nothing wired)')
	attribs = _attribs(pop)
	if not attribs:
		return (prefix or '(no prefix)') + '   <-   ' + name + ' (no points yet)'
	earlier = set()
	for j in range(k):
		_, s = _sourceFor(comp, j)
		if s is not None:
			earlier.update(a.name for a in _attribs(s))
	types = comp.par.Showtypes.eval()
	parts = [(prefix + a.name if a.name in earlier else a.name)
			 + ('[%s]' % _glslType(a) if types else '')
			 for a in attribs]
	return ', '.join(parts) + '   <-   ' + name
