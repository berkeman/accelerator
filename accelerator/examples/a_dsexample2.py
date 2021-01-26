description = "Create a dataset with number, string, and json columns."

def prepare(job):
	dw = job.datasetwriter()
	dw.add('anumber', 'number')
	dw.add('astring', 'unicode')
	dw.add('ajson', 'json')
	return dw

def analysis(prepare_res, sliceno):
	dw = prepare_res
	dw.write(sliceno, str(sliceno) + '-foo', {'n': sliceno, 's': str(sliceno)})
