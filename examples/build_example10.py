description = "Dataset: Create and append a column"

def main(urd):

	# First, create a new dataset.
	# Second, add a new column to the first dataset.

	print('\n# Run a method that creates a dataset')
	job = urd.build('example10')
	print('# (Now, test "ax ds %s" to inspect the dataset!)' % (job,))

	print('\n# Run a method that appends a column to the dataset')
	job = urd.build('example11', parent=job)
	print('# (Now, test "ax ds %s" to inspect the dataset!)' % (job,))
