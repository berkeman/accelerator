description = "Demonstrate return-value passing."

def prepare():
	# This runs first
	data = 37
	print("prepare", data)
	return data

def analysis(sliceno, prepare_res):
	# "prepare_res" contains return value from "prepare()"
	data = prepare_res + sliceno
	print("analysis", sliceno, prepare_res)
	return data

def synthesis(analysis_res, prepare_res):
	# "analysis_res" contains an _iterator_ of return values from "analysis()"
	data = list(analysis_res)
	print("synthesis", data, prepare_res)
	return sum(data)
