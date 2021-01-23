description = "Build a job with and without options."

from . import col, nocol

def main(urd):
	print(col + "\nCall method with default options" + nocol)
	job = urd.build('example4')
	print(job.load())

	print(col + "\nCall method with speficied options" + nocol)
	job = urd.build('example4', text='Hello World', anumber=42, thedict=dict(a=1, b='bdf'), c=4711)
	print(job.load())

	print(col + "\nTo see options to a specific job, try for example")
	print("  ax job %s" % (job,))
	print("and check the \"options\" section." + nocol)
