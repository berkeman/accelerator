description="Build a job, load its returned value.  Inspect job's parameters and post information"

def main(urd):

	print('\n# Run method "example1"')
	urd.build('example1')

	print('\n# Run method "example1" again')
	job = urd.build('example1')

	print('\n# Load and print returned value')
	result = job.load()
	print(result)

	print('\n# Print job post information, including profiling info')
	print(job.post)

	print('\n# Print job parameters')
	print(job.params)

	print('\n# Print job\'s Python interpreter')
	print(job.params.python)