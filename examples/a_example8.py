description = "prepare, analysis, and synthesis + return values"


def prepare():
	return 'this is prepare'

def analysis(sliceno, prepare_res):
	return 'this is analysis' + str(sliceno) + prepare_res

def synthesis(analysis_res, prepare_res):
	x = ','.join(analysis_res)
	print('analysis_res:', x)
	print('prepare_res:', prepare_res)
	return prepare_res + x
