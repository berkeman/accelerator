from os.path import dirname

from . import col, nocol

description = col + """
All examples are available here:
  """ + dirname(__file__) + """
Run them like this
  ax run example<x>""" + nocol

def main(urd):
	print("Examples are stored here:  \"%s\"" % (dirname(__file__),))
