options = dict(text='Default', anumber=37, thedict=dict(), c=int)

description = "Return data gathered from input options and exit."

def synthesis():
	return (options.text, options.anumber, options.thedict, options.c)
