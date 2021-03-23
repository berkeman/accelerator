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
from collections import defaultdict, OrderedDict

from accelerator.compat import terminal_size
from accelerator.shell.parser import printdesc

def main(argv, cfg):
	prog = argv.pop(0)
	if '--help' in argv or '-h' in argv:
		print('usage: %s [method]' % (prog,))
		print('gives description and options for method,')
		print('or lists methods with no method specified.')
		return
	columns = terminal_size().columns

	allscripts = OrderedDict()
	for package in cfg.method_directories:  # prio order
		scripts = dict()
		if '.' in package:
			path = dirname(import_module(package).__file__)
		else:
			path = join(cfg.project_directory, package)
		for item in sorted(glob(join(path, 'build*.py'))):
			name = basename(item[:-3])
			module = import_module('.'.join((package, name)))
			scripts[name] = getattr(module, 'description', '').strip('\n').rstrip('\n')
		allscripts[package] = scripts

	if argv:
		# ax script                    - lista alla packages + methods
        # ax script build              - lista alla "build.py" i alla packages
		# ax script build_tests        - hitta och visa ett specifikt script (i package-prioordning)
		# ax script foo                - hitta och visa alla build_foo.py i all packages
		# ax script dev                - lista alla script i ett givet package
		# ax script dev.               - "
		# ax script dev.build          - visa dev.build.py
		# ax script testo.foo          - visa testo.build_foo.py
		for arg in argv:
			arg = arg.rstrip('.')
			if arg in allscripts:
				# arg is matching a package
				name2desc = allscripts[arg]
				print('%s:' % (package,))
				for name, description in name2desc.items():
					printdesc(name, description or '-', columns)
				# proceed with next arg
				continue
			# Now we know that the argument is not a package.
			# Then, it can be "name" or "package.name" or complete bogus
#			print('# arg', arg)
			if '.' in arg:
				argpack, argname = arg.rsplit('.', 1)
				if argpack in allscripts:
#					print('# dot', argpack, argname)
					if not argname.startswith('build'):
						argname = 'build_' + argname
#					print('# dot', argpack, argname)
					description = allscripts[argpack].get(argname)
#					print('# desc', description)
					if description is not None:
						description = description or '-'
						printdesc(argpack + '.' + argname, description or '-', columns)
						continue
			else:
				for package in allscripts:
					argpack, argname = False, arg
#					print('# nodot', argpack, argname)
					if not argname.startswith('build'):
						argname = 'build_' + argname
#					print('#', package, argname)
#					print('#', allscripts[package])
					description = allscripts[package].get(argname)
					if description is not None:
						description = description or '-'
						printdesc(package + '.' + argname, description or '-', columns)
						continue
	else:
		for package, name2desc in allscripts.items():
			print('%s:' % (package,))
			for name, description in name2desc.items():
				if description is not None:
					description = description or '-'
				printdesc(name, description, columns)
