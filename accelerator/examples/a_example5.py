description = "Create one text file and one pickle file."

def synthesis(job):

	data = "some text"

	with job.open('atextfile.txt', 'wt') as fh:
		fh.write(data)

	job.save(data, 'apicklefile')
