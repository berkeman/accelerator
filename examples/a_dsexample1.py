from collections import Counter

datasets = ('source',)

def analysis(sliceno):
	v = Counter()
	for s, n in datasets.source.iterate(sliceno, ('astring', 'anint')):
		v[s] += n
	return v

def synthesis(analysis_res):
	v = analysis_res.merge_auto()
	for item in sorted(v.items()):
		print(item)
	return v
