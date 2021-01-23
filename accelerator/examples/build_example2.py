description = "Build two linked jobs, then load and print the second job's return value."

def main(urd):
	job1 = urd.build('example1')
	job2 = urd.build('example2', source=job1)
	print(job2.load())
