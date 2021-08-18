from os.path import dirname, join

description = "Tutorial: Iterate over a chain of datasets."


def colorprint(s):
	print("\033[34m" + s + "\033[0m")


filenames = ('data.csv', 'data2.csv', 'data3.csv')
# Again, files are stored in same directory as this python file.
# In a real project, set "input directory" in config file instead!
filenames = (join(dirname(__file__), x) for x in filenames)


def main(urd):
	colorprint('\nWe\'ve stolen the import loop from "build_tutorial03.py')
	colorprint('Soon, we\'ll show how to do this in a much more elegant way!')

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

	colorprint('\nThe variable "imp" now hold a reference to the last build method,')
	colorprint('which happens to be the dataset_hashpart of the file "data3.csv".')
	colorprint('But remember that the datasets are chained, so all imported data')
	colorprint('is available using this reference.')

	colorprint('Now, let\'s iterate over all imported data')
	job = urd.build('dsexample1', source=imp)
	colorprint('...and the result is (something printed by the job to stdout)')
	print(job.output())
