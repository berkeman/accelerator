description = "Store a sliced file"

options = dict(filename='aslicedfile')

def analysis(sliceno, job):
	data = 'a' + str(sliceno)

	job.save(data, options.filename, sliceno=sliceno, temp=False)
