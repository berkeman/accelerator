def prepare(job):
	# Create a datasetwriter with one column
	# named 'test' of type 'number'.
	dw = job.datasetwriter()
	dw.add('test', 'number')
	return dw

def analysis(sliceno, prepare_res):
	dw = prepare_res
	# In this slice, write the sliceno to the dataset
	dw.write(sliceno)
