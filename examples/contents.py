from collections import defaultdict
import glob

def parsetags(line):
	line = line.split(':', 1)[1].rstrip('\n')
	line = [x.strip() for x in line.split(',')]
	return line

tests = defaultdict(set)
for fn in sorted(glob.glob('a_*.py') + glob.glob('build_*.py')):
	with open(fn, 'tr') as fh:
		for line in fh:
			if line.startswith('#tests:') or line.startswith('#build:'):
				for tag in parsetags(line):
					tests[tag].add(fn)

for key, val in tests.items():
	print(key, val)
