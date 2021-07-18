datasets = ('parent',)

def prepare(job):
	# Create a datasetwriter with one column named 'strtest' of type
	# 'unicode'.  This dataset has the source dataset as parent,
	# i.e. this dataset adds columns to the parent dataset.
	dw = job.datasetwriter(parent=datasets.parent)
	dw.add('strtest', 'unicode')
	return dw

def analysis(sliceno, prepare_res):
	dw = prepare_res
	# Read each value in the 'test' column and write as
	# strings to the 'strtest' column
	for test in datasets.parent.iterate(sliceno, 'test'):
		dw.write(str(test))
