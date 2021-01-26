from os.path import dirname, join

description = "Create a chained dataset."

# file is stored in same directory as this python file
path = dirname(__file__)

def main(urd):
	imp = None
	for filename in ['data.csv', 'data2.csv', 'data3.csv']:
		# Ideally, you'd use "input_directory" to avoid an absolute path
		filename = join(path, filename)
		imp = urd.build('csvimport', filename=filename, separator='\t', previous=imp)

	urd.build('dsexample4', source=imp)
