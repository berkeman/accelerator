from os.path import dirname, join

description = "Tutorial: Import several files into a dataset chain"


def colorprint(s):
	print("\033[34m" + s + "\033[0m")


filenames = ('data.csv', 'data2.csv', 'data3.csv')
# Again, files are stored in same directory as this python file.
# In a real project, set "input directory" in config file instead!
filenames = (join(dirname(__file__), x) for x in filenames)


def main(urd):
	colorprint('\nA loop importing three files, creating a chained dataset of all data\n')

	for filename in filenames:
		print(filename)
		imp = urd.build('csvimport', filename=filename, separator='\t', previous=urd.joblist.get('csvimport'))
		imp = urd.build('dataset_type',
						source=imp,
						previous=urd.joblist.get('dataset_type'),
						column2type=dict(
							adate='datetime:%Y-%m-%d',
							astring='unicode:utf-8',
							anint='number',
							afloat='float64',
						))
		imp = urd.build('dataset_sort', source=imp, sort_columns='adate', previous=urd.joblist.get('dataset_sort'))
		imp = urd.build('dataset_hashpart', source=imp, hashlabel='astring', previous=urd.joblist.get('dataset_hashpart'))

	colorprint('\nEach job has a dataset input parameter called previous.')
	colorprint('We assign this input parameter to (a reference) of the job that')
	colorprint('processed the previous file in the list.  This creates a')
	colorprint('dataset chain.')

	colorprint('\nThe flags -s, -S, and -c to "ax ds" are useful when looking')
	colorprint('at chained datasets')
	print('    ax ds -s %s' % (imp,))
	print('    ax ds -S %s' % (imp,))
	print('    ax ds -c %s' % (imp,))
	colorprint('See info and more options using')
	print('    ax ds --help')

	colorprint('\nThis is a small example, so we can print all of it using')
	print('    ax cat -c %s' % (imp,))
	
	colorprint('\nThe point of chaining is that it allows datasets to grow in')
	colorprint('number of rows, with linear time complexity, without changing')
	colorprint('any existing processing state.  This means that we can add')
	colorprint('new rows to a dataset, but we always have access to all previous')
	colorprint('imports of the data.  Nothing is modified, data is just appended.')
