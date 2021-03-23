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

# ax script                    - lista alla packages + methods
# ax script build              - lista alla "build.py" i alla packages
# ax script build_tests        - hitta och visa ett specifikt script (i package-prioordning)
# ax script foo                - hitta och visa alla build_foo.py i all packages
# ax script dev                - lista alla script i ett givet package
# ax script dev.               - "
# ax script dev.build          - visa dev.build.py
# ax script testo.foo          - visa testo.build_foo.py

def main(argv, cfg):
	prog = argv.pop(0)
	if '--help' in argv or '-h' in argv:
		print('usage: %s [method]' % (prog,))
		print('gives description for build script,')
		print('or lists build scrips with no description.')
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
		for arg in argv:
			arg = arg.rstrip('.')
			if arg in allscripts:
				print('%s:' % (arg,))
				name2desc = allscripts[arg]
				for name, description in name2desc.items():
					printdesc(name, description, columns)
			elif '.' in arg:
				argpack, argname = arg.rsplit('.', 1)
				if argpack in allscripts:
					if not argname.startswith('build'):
						argname = 'build_' + argname
					description = allscripts[argpack].get(argname)
					if description is not None:
						printdesc(argpack + '.' + argname, description, columns)
			else:
				for package in allscripts:
					if not arg.startswith('build'):
						arg = 'build_' + arg
					description = allscripts[package].get(arg)
					if description is not None:
						printdesc(package + '.' + arg, description, columns)
						continue
	else:
		for package, name2desc in allscripts.items():
			print('%s:' % (package,))
			for name, description in name2desc.items():
				if description is not None:
					printdesc(name, description, columns)
