from os.path import dirname, join

description = "Tutorial: Iterate over a chain of datasets."


def colorprint(s):
	print("\033[34m" + s + "\033[0m")


filenames = ('data.csv', 'data2.csv', 'data3.csv')
# Again, files are stored in same directory as this python file.
# In a real project, set "input directory" in config file instead!
filenames = (join(dirname(__file__), x) for x in filenames)


def main(urd):
	colorprint('\nImport a list of files and store references in the Urd database.')

	key = 'example_tutorial05'
	urd.truncate(key, 0)
	for ts, filename in enumerate(filenames, 1):
		print(filename, ts)
		urd.begin(key, ts, caption=filename)
		latest = urd.latest(key).joblist
		imp = urd.build('csvimport', filename=filename, separator='\t', previous=latest.get('csvimport'))
		imp = urd.build('dataset_type',
						source=imp,
						previous=latest.get('dataset_type'),
						column2type=dict(
							adate='datetime:%Y-%m-%d',
							astring='unicode:utf-8',
							anint='number',
							afloat='float64',
						))
		imp = urd.build('dataset_sort', source=imp, sort_columns='adate', previous=latest.get('dataset_sort'))
		imp = urd.build('dataset_hashpart', source=imp, hashlabel='astring', previous=latest.get('dataset_hashpart'))
		urd.finish(key)

	colorprint('\nNow, the import loop has stored references to everything that')
	colorprint('happened in the Urd server.')

	colorprint('\nTo view all Urd "lists", type')
	print('    ax urd')
	colorprint('Each key is composed by <user>/<listname>.')
	print(urd.list())

	colorprint('\nLet\'s look at all entries in the "%s" list.' % (key,))
	print('    ax urd %s/since/0' % (key,))
	colorprint('in "machine" format, it reads')
	print(urd.since(key, 0))
	colorprint('using the "ax urd" command we will get the captions too.')

	colorprint('\nWe can look at an individual Urd-item like this')
	print('    ax urd %s/3' % (key,))
	colorprint('which corresponds to the list in key "%s" at timestamp 3' % (key,))
	colorprint('(Timestamps can be dates, datetimes, integers, or tuples of date/datetimes and integers.')
	print(urd.peek(key, 3))  # peek and not get, since we are not between begin/finish.  See manual.
	colorprint('Command line output is prettier.')
