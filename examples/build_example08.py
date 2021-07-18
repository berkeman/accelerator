description = "Jobs: equivalent_hashes howto"

#build: depend_extra
def main(urd):
	job = urd.build('examplea')

	thehash = job.params.hash
	print('Take the hash from the built job:')
	print('  "%s"' % (thehash,))
	print('and add it to the method like this')
	print('  "equivalent_hashes = {\'whatever\': (\'%s\',)}"' % (thehash,))
	print('also do some other change to the method while at it to make it different.')
	print('Re-run and the daemon output will be something like')
	print("""  =================================================================================================================
  WARNING: examples.a_examplea has equivalent_hashes, but missing verifier <verifier>
  =================================================================================================================""")
	print('Now, let <verifier> replace the string \'whatever\' in the method.')
	print('Done, the new version of the method is now considered equivalent to the old one.')
