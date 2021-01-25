description = "Load a sliced file"

options = dict(filename='aslicedfile')

jobs = ('sourcejob',)

def analysis(sliceno):
	data = jobs.sourcejob.load(options.filename, sliceno=sliceno)
	print(sliceno, data)
