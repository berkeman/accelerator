jobs = ('source',)

description = "Load data from source job and return it."

def synthesis():
	data = jobs.source.load()
	return data
