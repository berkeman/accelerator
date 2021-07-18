description = "Jobs: Build and link two jobs, load and print return values"

def main(urd):

	print('\n# Run methods "example1" + "example2"')
	job1 = urd.build('example1')
	job2 = urd.build('example2', first=job1)  # "first" is an item in the "jobs" list in a_example2.py
	print('\n# Return value from "example1"')
	print(job1.load())
	print('\n# Return value from "example2"')
	print(job2.load())
