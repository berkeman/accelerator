description = "Create a dataset with number, string, and json columns."


def prepare(job):
	dw = job.datasetwriter()
	dw.add('anumbercolumn', 'number')
	dw.add('astringcolumn', 'unicode')
	dw.add('ajsoncolumn', 'json')
	return dw


def analysis(prepare_res, sliceno):
	dw = prepare_res
	data = sliceno + 1000
	dw.write(data, str(data) + '-foo', {'n': data, 's': str(data)})
