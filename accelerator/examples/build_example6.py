description = "Build a job that demonstrates return-value passing."

from . import col, nocol

def main(urd):
	job = urd.build('example6')

	print(col + "\nReturn value is" + nocol)
	print(job.load())

	print(col + "\nOutput to stdout is" + nocol)
	print(job.output())
