from os.path import dirname, join

description = "Tutorial: Import a file."


def colorprint(s):
	print("\033[34m" + s + "\033[0m")


# File is stored in same directory as this python file
# In a real project, set "input directory" in config file instead!
filename = join(dirname(__file__), 'data.csv')


def main(urd):
	colorprint('\nImport a CSV-file:\n')

	imp = urd.build('csvimport', filename=filename, separator='\t')

	colorprint('\nNow you can try')
	print('    ax ds %s' % (imp,))
	colorprint('  to show info on the imported dataset,')
	print('    ax job %s' % (imp,))
	colorprint('  to show info on the job that created the dataset, and')
	print('    ax cat -H %s' % (imp,))
	colorprint('  to show the contents of the dataset.')

	colorprint('\nAs long as we do not assign names to datasets, they are')
	colorprint('referenced by the default dataset name, which is "default".')
	colorprint('If we are working on the default dataset, we can use the')
	colorprint('reference to the job that created the dataset as a reference')
	colorprint('to the default dataset inside the job.  I.e.')
	print('    ax ds %s' % (imp,))
	colorprint('is equivalent to')
	print('    ax ds %s/default' % (imp,))
	colorprint('which is the formally correct way to refer to the dataset.')
	colorprint('(This also shows using "ax ds".)')
	
	colorprint('\nIt is also possible to write for example')
	print('    ax job csvimport')
	colorprint('etc., in order to get information on the last created csvimport job.')


	colorprint('\nPlease check options using "ax <command> --help".\n')
