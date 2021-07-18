description = "Write a sliced file in analysis, one file in synthesis, and return some data."

def analysis(sliceno, job):
	# save one file per analysis process...
	filename = 'myfile1'
	data = 'this is the analysis %d data' % (sliceno,)
	job.save(data, filename, sliceno=sliceno)


def synthesis(job):
	# ...and one file in the synthesis process...
	filename = 'myfile2'
	data = 'this_is_the_synthesis data'
	job.save(data, filename)

	# ...and let's return some data too.
	returndata = 'this is the returned data'
	return returndata
