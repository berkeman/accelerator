description = "Dataset: Chain two datasets"

def main(urd):

	# First, create a new dataset.
	# Second, create a second dataset chained to the first

	print('\n# Run a method that creates a dataset')
	job = urd.build('example10')
	print('# (Now, test "bd dsinfo %s" to inspect the dataset!)' % (job,))

	print('\n# Run a method that creates a datasets and chains it to the previous one.')
	job = urd.build('example12', previous=job)
	print('# (Now, test "bd dsinfo %s" to inspect the dataset!)' % (job,))
