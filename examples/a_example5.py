description = 'JobWithFile, read normal and sliced files'

from accelerator.job import JobWithFile

options = dict(firstfile=JobWithFile, secondfile=JobWithFile)

def analysis(sliceno):
	print(options.firstfile.load(sliceno=sliceno))

def synthesis():
	print(options.secondfile.load())
