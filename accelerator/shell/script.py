############################################################################
#                                                                          #
# Copyright (c) 2020 Carl Drougge                                          #
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

from glob import glob
from os.path import join, dirname, basename
from importlib import import_module
from collections import defaultdict

from accelerator.compat import terminal_size


def printdesc(name, description, columns, indent=2):
	max_len = columns - 4 - len(name)
	description = description.split('\n')[0]
	if description and max_len > 10:
		if len(description) > max_len:
			max_len -= 4
			parts = description.split()
			description = ''
			for part in parts:
				if len(description) + len(part) + 1 > max_len:
					break
				description = '%s %s' % (description, part,)
			description += ' ...'
		print(' ' * indent + '%s: %s' % (name, description,))
	else:
		print(' ' * indent + '%s' % (name,))


def main(argv, cfg):
	prog = argv.pop(0)
	if '--help' in argv or '-h' in argv:
		print('usage: %s [method]' % (prog,))
		print('gives description and options for method,')
		print('or lists methods with no method specified.')
		return
	columns = terminal_size().columns

	allscripts = []
	for package in cfg.method_directories:  # prio order
		scripts = dict()
		if '.' in package:
			path = dirname(import_module(package).__file__)
		else:
			path = join(cfg.project_directory, package)
		for item in sorted(glob(join(path + '/build*.py'))):
			name = basename(item[:-3])
			module = import_module('.'.join((package, name)))
			scripts[name] = getattr(module, 'description', '').strip('\n').rstrip('\n')
		allscripts.append((package, scripts))

	if argv:
		# arguments:
		# ax show dev                  - dev is a package, not a method.  This returns nothing
		# ax show dev.                 - print description for "dev.build"
		# ax show import               - print description for "import.build_import"
		# ax show build_import           "
		# ax show import.import          "
		# ax show import.build_import    "
		for name in argv:
			description = None
			if '.' in name:
				argpack, argname = name.rsplit('.', 1)
			else:
				argpack, argname = False, name
			if argname == '':
				argname = 'build'
			if not argname.startswith('build'):
				argname = 'build_' + argname
			for package, name2desc in allscripts:
				if argpack:
					if argpack == package:
						description = name2desc.get(argname)
				else:
					description = name2desc.get(argname)
				if description is not None:
					printdesc("%s.%s" % (package, argname), description, columns, indent=0)
					break
	else:
		if allscripts:
			for package, name2desc in allscripts:
				print('%s:' % (package,))
				for name, description in name2desc.items():
					printdesc(name, description, columns)
