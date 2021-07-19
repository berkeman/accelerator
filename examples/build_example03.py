description = "Jobs: sliced files, stdout and stderror, load any file from a job, jobwithfile"


def colorstring(s):
	return "\033[34m" + s + "\033[0m"


# @@@@@@@@@@@ Splitta denna i fler exempel

def main(urd):
	print(colorstring('\n# This job writes sliced files in "myfile1", and a single file'))
	print(colorstring('# "myfile2"'))
	job1 = urd.build('example4')

	print(colorstring('\n# These are the files created by / residing in job %s.' % (job1,)))
	print(job1.files())

	print(colorstring('\n# This job reads the sliced and the single file and prints its'))
	print(colorstring('# contents to stdout'))
	job2 = urd.build('example5',
					 firstfile=job1.withfile('myfile1', sliced=True),
					 secondfile=job1.withfile('myfile2'),
	)

	print(colorstring('\n# Read and print stored stdout from %s synthesis') % (job2,))
	print(job2.output('synthesis'))
	print(colorstring('# Read and print stored stdout from %s everything') % (job2,))
	print(job2.output())
	print(colorstring('# Read and print stored stdout from %s analysis process 2') % (job2,))
	print(job2.output(2))

	print(colorstring('# We can also use job.open() to get a file handler and do any'))
	print(colorstring('kind of file operations.'))
	with job1.open('myfile2', 'rb') as fh:
		import pickle
		print(pickle.load(fh))
