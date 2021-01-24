from os.path import dirname

description = """ 
All examples are available here:
  """ + dirname(__file__) + """
Run them like this
  ax run example<x>"""

def main(urd):
	print("Examples are stored here:  \"%s\"" % (dirname(__file__),))
