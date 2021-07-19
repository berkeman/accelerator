from accelerator import Job


description = "Jobs: Subjob"


def colorstring(s):
	return "\033[34m" + s + "\033[0m"


def main(urd):
	print(colorstring('\n# This job will execute a subjob'))
	job = urd.build('example6')

	print(colorstring('\n# Print subjob info'))
	for job in job.post.subjobs:
		print('subjob', dict(job=job, method=Job(job).method))
