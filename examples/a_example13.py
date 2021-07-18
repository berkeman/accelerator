datasets = ('source',)

def analysis(sliceno):
	# sum the test column of the source dataset
	# Faster: "return sum(datasets.source.iterate(slinceo, 'test'))"
	c = 0
	for test in datasets.source.iterate(sliceno, 'test'):
		c += test
	return c


def synthesis(analysis_res):
	return analysis_res.merge_auto()
