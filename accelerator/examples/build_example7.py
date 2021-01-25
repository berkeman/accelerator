description = "Advanced, store and load sliced files."

def main(urd):
	filename='aslicedfile'
	store = urd.build('example7_store', filename=filename)
	load = urd.build('example7_load', filename=filename, sourcejob=store)

	print("""
Files stored in the "store" job:
""" + str(store.files()))
