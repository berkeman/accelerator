def main(urd):

	# Build a job, load its returned value.
	# Inspect job's parameters and post information


	print('\n# Run method "example1"')
	urd.build('example1')


	print('\n# Run method "example1" again, load and print returned value')
	job = urd.build('example1')
	result = job.load()
	print(result)


	print('\n# Print job post information, including profiling info')
	print(job.post)


	print('\n# Print job parameters')
	print(job.params)


	print('\n# Print job\'s Python interpreter')
	print(job.params.python)

