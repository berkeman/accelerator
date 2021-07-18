description = "Dataset: Iterate"

def main(urd):

	# Create a new dataset.
	print('\n# Run a method that creates a dataset')
	job = urd.build('example10')

	# Iterate over this dataset and print return value
	job = urd.build('example13', source=job)
	print("# Job returns the sum:", job.load())
