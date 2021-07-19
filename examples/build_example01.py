description = "Jobs: Build a job, load its returned value."


def colorstring(s):
	return "\033[34m" + s + "\033[0m"


def main(urd):
	print(colorstring('\n# Run method "example1"'))
	urd.build('example1')

	print(colorstring('\n# Run method "example1" again'))
	job = urd.build('example1')

	print(colorstring('\n# Load and print the job\'s return value'))
	result = job.load()
	print(result)
