description = "Jobs: Subjob"

from accelerator import Job

def main(urd):
	print('\n# This job will execute a subjob')
	job = urd.build('example6')

	print('\n# Print subjob info')
	for job in job.post.subjobs:
		print('subjob', job, Job(job).method)
