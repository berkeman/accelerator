description = "Build a job, then load and print the job's return value."

def main(urd):
	job = urd.build('example1')
	data = job.load()

	col = "\033[34m"
	nocol = "\033[0m"
	print()
	print(col + "This is the job's returned data:" + nocol)
	print(data)
	print(col + "Anything Python pickleable could be passed between jobs and build scripts." + nocol)
