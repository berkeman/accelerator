description = "Append columns to an existing dataset."

def main(urd):
	job = urd.build('dsexample2')
	job = urd.build('dsexample3', source=job)
