description = "Dataset: Create a dataset from scratch."

def main(urd):
	print("\nBuild a job that creates a dataset from scratch:\n")
	job = urd.build('dsexample2')

	print("""
Check contents of dataset using

  ax cat -H dsexample2

or

  ax cat -H %s

More info about the dataset

  ax ds -s %s

(For convenience, the jobid can be used as a reference to the default
dataset in a job.  The full name is "%s/default".)""" % (job, job, job))
