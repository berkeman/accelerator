description = "Build a job launching subjobs."

def main(urd):
	job = urd.build('example8')

	print(job.post.subjobs)
