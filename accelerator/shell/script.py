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
from . import printdesc
from accelerator.compat import terminal_size


def main(argv, cfg):
	prog = argv.pop(0)
	if '--help' in argv or '-h' in argv:
		fh = sys.stdout if argv else sys.stderr
		print('usage: %s [script|package.script]' % (prog,), file=fh)
		print('gives description for build script, or list build scripts.', file=fh)
		print(file=fh)
		print('examples:', file=fh)
		print('  "%s dev"       - dev is a package, not a script.  This returns nothing' % (prog,), file=fh)
		print('  "%s dev."      - print description for "dev.build"' % (prog,), file=fh)
		print('  "%s foo"       - print description for first "build_foo" in package prio order' % (prog,), file=fh)
		print('  "%s import.foo - print description for "import.build_foo"' % (prog,), file=fh)
		return
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

	if not argv:
		argv = sorted(x + '.' for x in allscripts)
	for arg in argv:
		if '.' in arg:
			argpack, argname = arg.rsplit('.', 1)
			if not argname:
				print(argpack)
				for name, desc in sorted(allscripts.get(argpack, {}).items()):
					printdesc(argpack + '.' + name, desc, columns)
				continue
		else:
			argpack, argname = None, arg
		lastpack = None
		for package, name2desc in sorted(allscripts.items()):
			#print(argpack, argname, package, name2desc)
			if (argpack and (argpack == package)) or (not argpack):
				for name, desc in sorted(name2desc.items()):
					if '_' in name and argname in name.split('_', 1)[1]:
						if lastpack != package:
							print(package)
							lastpack = package
						printdesc(package + '.' + name, desc, columns)
#				printdesc("%s.%s" % (package, argname), description, columns, indent=0)
