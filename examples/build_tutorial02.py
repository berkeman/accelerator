from os.path import dirname, join

description = "Tutorial: Import, type, sort, and hash partition a file."


def colorprint(s):
	print("\033[34m" + s + "\033[0m")


# File is stored in same directory as this python file.
# In a real project, set "input directory" in config file instead!
filename = join(dirname(__file__), 'data.csv')


def main(urd):
	colorprint('\nImport a CSV-file, type, sort, and hash-partition the imported dataset.\n')

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

	colorprint('\nNote how the output from each build()-call is input to the next one.')
	colorprint('This is how jobs and datasets are passed as inputs to new jobs.')

	colorprint('\n1. Take a look at the dataset_hashpart job\'s information')
	print('    ax job %s' % (imp,))
	colorprint('We can see that the dataset "%s" is input to this job.' % (imp.params.datasets.source,))

	colorprint('\n2. Now take a look at the dataset created by dataset_hashpart.')
	print('    ax ds %s' % (imp,))
	colorprint('The asterisk on the row corresponding to the "astring" column ')
	colorprint('indicates that the dataset is hash-partitioned on this column.')
	colorprint('(It is possible to use the "-s" option to "ax cat" to print')
	colorprint('data from individual slices.)')

	colorprint('\n3. References to all jobs are stored in the urd.joblist object:')
	print(urd.joblist.pretty)
	colorprint('so that they can be fetched easy at a later time.  This will be')
	colorprint('used in the next step.')

