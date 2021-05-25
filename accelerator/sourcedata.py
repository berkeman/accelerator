############################################################################
#                                                                          #
# Copyright (c) 2017 eBay Inc.                                             #
# Modifications copyright (c) 2018-2021 Carl Drougge                       #
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

from accelerator import dsutil
from accelerator.compat import PY3

type2iter = {
	'number'   : dsutil.ReadNumber,
	'complex64': dsutil.ReadComplex64,
	'complex32': dsutil.ReadComplex32,
	'float64'  : dsutil.ReadFloat64,
	'float32'  : dsutil.ReadFloat32,
	'int64'    : dsutil.ReadInt64,
	'int32'    : dsutil.ReadInt32,
	'bits64'   : dsutil.ReadBits64,
	'bits32'   : dsutil.ReadBits32,
	'bool'     : dsutil.ReadBool,
	'datetime' : dsutil.ReadDateTime,
	'date'     : dsutil.ReadDate,
	'time'     : dsutil.ReadTime,
	'bytes'    : dsutil.ReadBytes,
	'ascii'    : dsutil.ReadAscii,
	'unicode'  : dsutil.ReadUnicode,
}

from json import JSONDecoder
class ReadJson(object):
	def __init__(self, *a, **kw):
		if PY3:
			self.fh = dsutil.ReadUnicode(*a, **kw)
		else:
			self.fh = dsutil.ReadBytes(*a, **kw)
		self.decode = JSONDecoder().decode
	def __next__(self):
		return self.decode(next(self.fh))
	next = __next__
	def close(self):
		self.fh.close()
	def __iter__(self):
		return self
	def __enter__(self):
		return self
	def __exit__(self, type, value, traceback):
		self.close()
type2iter['json'] = ReadJson

from pickle import loads
class ReadPickle(object):
	def __init__(self, *a, **kw):
		assert PY3, "Pickle columns require python 3, sorry"
		self.fh = dsutil.ReadBytes(*a, **kw)
	def __next__(self):
		return loads(next(self.fh))
	next = __next__
	def close(self):
		self.fh.close()
	def __iter__(self):
		return self
	def __enter__(self):
		return self
	def __exit__(self, type, value, traceback):
		self.close()
type2iter['pickle'] = ReadPickle

def typed_reader(typename):
	if typename not in type2iter:
		raise ValueError("Unknown reader for type %s" % (typename,))
	return type2iter[typename]
