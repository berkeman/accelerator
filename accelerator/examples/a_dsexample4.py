datasets = ('source',)

def analysis(sliceno):
	v = []
	for n, s in datasets.source.iterate_chain(sliceno, ('anint', 'astring')):
		v.append((n, s))
	return v

def synthesis(analysis_res):
	v = analysis_res.merge_auto()
	for item in v:
		print(item)
	return v
