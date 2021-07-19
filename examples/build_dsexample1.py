from os.path import dirname, join

description = "Dataset: Import, type, sort, and hash partition a tabular file."


# file is stored in same directory as this python file
filename = join(dirname(__file__), 'data.csv')


def main(urd):
	print("\nImport, type, sort, and hash partition the file \"data.csv\":\n")

	imp = urd.build('csvimport', filename=filename, separator='\t')
	imp = urd.build('dataset_type',
					source=imp,
					column2type=dict(
						adate='datetime:%Y-%m-%d',
						astring='unicode:utf-8',
						anint='number',
						afloat='float64',
					))
	imp = urd.build('dataset_sort', source=imp, sort_columns='adate')
	imp = urd.build('dataset_hashpart', source=imp, hashlabel='astring')

	job = urd.build('dsexample1', source=imp)

	print("""
Now you can do

  ax ds dataset_hashpart

to show info on the default dataset in the latest dataset_hashpart
job, or equivalently

  ax ds %s

To list the data in the dataset, do

  ax cat -H dataset_hashpart

To see the output (to stdout) from the "dsexample1" job, do

  ax job -O dsexample1

Please check options using "ax ds --help" etc.
""" % (imp,))
