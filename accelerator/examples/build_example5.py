description = "Build a job that writes one text file and one pickle file."

from . import col, nocol

def main(urd):
	job = urd.build('example5')

	print(col + "\nFiles in this job")
	print('  ', job.files())

	print("\nwith these absolute filenames:")
	for fn in job.files():
		print('  ', fn, ':', job.filename(fn))

	print("\nThe contents of the pickle file can be loaded directly:")
	print(job.load('apicklefile'))
	print(nocol)

	# Note, job.load() with no options will load the file
	# "result.pickle", if it exists.  This file is holds
	# the job's returned value.
	# Any other file can be loaded by specifying a file name.
