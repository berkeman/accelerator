description = "Build a job that prints to stdout.  Fetch and print the output."

def main(urd):
	job = urd.build('example3')
	output = job.output()

	col = "\033[34m"
	nocol = "\033[0m"
	print()
	print(col + "This is the job's printed output:" + nocol)
	print(output)

	print(col + "Note that you can use the \"ax job\" command to show a job's output")
	print("For example, try")
	print("  ax job %s" % (job,))
	print("  ax job -O %s" % (job,))
	print("Do \"ax job -h\" for a full list of options." + nocol)

	print("Files in this example:")
	print("  ", __file__)
	print(urd.info)
