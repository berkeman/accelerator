############################################################################
#                                                                          #
# Copyright (c) 2021 Anders Berkeman                                       #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License");          #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#  http://www.apache.org/licenses/LICENSE-2.0                              #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
#                                                                          #
############################################################################

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import sys
from glob import glob
from os.path import join, dirname, basename
from importlib import import_module
from collections import defaultdict
from argparse import RawTextHelpFormatter
from . import printdesc
from accelerator.compat import terminal_size, ArgumentParser


def main(argv, cfg):
	descr = "gives description for build script, or list build scripts."
	parser = ArgumentParser(
		prog=argv.pop(0),
		description=descr,
		formatter_class=RawTextHelpFormatter,
	)
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-l', '--list', action='store_true', help='short listing')
	parser.add_argument('string', nargs='*', default=[], help='substring used for matching')
	args = parser.parse_intermixed_args(argv)
	columns = terminal_size().columns

	allscripts = defaultdict(dict)
	for package in cfg.method_directories:
		if '.' in package:
			path = dirname(import_module(package).__file__)
		else:
			path = join(cfg.project_directory, package)
		for item in sorted(glob(join(path + '/build*.py'))):
			name = basename(item[:-3])
			try:
				module = import_module('.'.join((package, name)))
			except Exception as e:
				print('\x1b[31m' + '/'.join((package, name)) + '.py:', e, '\x1b[m', file=sys.stderr)
				continue
			allscripts[package][name] = getattr(module, 'description', '').strip('\n').rstrip('\n')

	if not args.string:
		# no args => list everything in short format
		args.string = sorted(x + '.' for x in allscripts)
		args.list = True
	alreadyprinted = set()
	for arg in args.string:
		lastpack = None
		for package, name2desc in sorted(allscripts.items()):
			for name, desc in sorted(name2desc.items()):
				key = '.'.join((package, name))
				if arg in key:
					if key not in alreadyprinted:
						if lastpack != package:
							print(package)
							lastpack = package
						printdesc(name, desc, columns)
						alreadyprinted.add(key)
