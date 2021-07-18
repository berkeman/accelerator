description = "Jobs: sliced files, stdout and stderror, load any file from a job, jobwithfile"

# Splitta denna i fler exempel

def main(urd):
	print('\n# This job writes sliced files in "myfile1", and a single file')
	print('# "myfile2"')
	job1 = urd.build('example4')

	print('\n# This job reads the sliced and the single file and prints its')
	print('# contents to stdout')
	job2 = urd.build('example5',
					 firstfile=job1.withfile('myfile1', sliced=True),
					 secondfile=job1.withfile('myfile2'),
	)

	print('\n# Read and print stored stdout for synthesis')
	print(job2.output('synthesis'))
	print('\n# Read and print stored stdout for everything')
	print(job2.output())
	print('\n# Read and print stored stdout for analysis process 2')
	print(job2.output(2))

	print('\n# We can also use job.open() to get a file handler.')
	with job1.open('myfile2', 'rb') as fh:
		import pickle
		print('x', pickle.load(fh), 'x')
