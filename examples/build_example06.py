description = "Jobs: prepare, analysis, and synthesis + return values"


def main(urd):
	job = urd.build('example8')
	print('job output:', job.output())
	print('job return value:', job.load())
