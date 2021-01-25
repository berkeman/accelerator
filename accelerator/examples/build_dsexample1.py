from os.path import dirname, join

description = "Import, type, sort, and hash partition a tabular file."

# file is stored in same directory as this python file
filename = join(dirname(__file__), 'data.csv')


def main(urd):
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


	print("""
Now you can do

  ax ds dataset_hashpart

to show info on the default dataset in the latest dataset_hashpart
job, or equivalently

  ax ds %s

Please check options using "ax ds --help".
""" % (imp,))
