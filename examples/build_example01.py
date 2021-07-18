description = "Jobs: Build a job, load its returned value."

def main(urd):

	print('\n# Run method "example1"')
	urd.build('example1')

	print('\n# Run method "example1" again, load and print returned value')
	job = urd.build('example1')

	print('\n# Load and print the job\'s return value')
	result = job.load()
	print(result)
