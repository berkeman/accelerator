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
from accelerator.compat import str_types, PY3

_convfuncs = {
	'number'   : dsutil.WriteNumber,
	'complex64': dsutil.WriteComplex64,
	'complex32': dsutil.WriteComplex32,
	'float64'  : dsutil.WriteFloat64,
	'float32'  : dsutil.WriteFloat32,
	'int64'    : dsutil.WriteInt64,
	'int32'    : dsutil.WriteInt32,
	'bits64'   : dsutil.WriteBits64,
	'bits32'   : dsutil.WriteBits32,
	'bool'     : dsutil.WriteBool,
	'datetime' : dsutil.WriteDateTime,
	'date'     : dsutil.WriteDate,
	'time'     : dsutil.WriteTime,
	'bytes'    : dsutil.WriteBytes,
	'ascii'    : dsutil.WriteAscii,
	'unicode'  : dsutil.WriteUnicode,
	'parsed:number'   : dsutil.WriteParsedNumber,
	'parsed:complex64': dsutil.WriteParsedComplex64,
	'parsed:complex32': dsutil.WriteParsedComplex32,
	'parsed:float64'  : dsutil.WriteParsedFloat64,
	'parsed:float32'  : dsutil.WriteParsedFloat32,
	'parsed:int64'    : dsutil.WriteParsedInt64,
	'parsed:int32'    : dsutil.WriteParsedInt32,
	'parsed:bits64'   : dsutil.WriteParsedBits64,
	'parsed:bits32'   : dsutil.WriteParsedBits32,
}

def typed_writer(typename):
	if typename not in _convfuncs:
		raise ValueError("Unknown writer for type %s" % (typename,))
	return _convfuncs[typename]

def typed_reader(typename):
	from accelerator.sourcedata import type2iter
	if typename not in type2iter:
		raise ValueError("Unknown reader for type %s" % (typename,))
	return type2iter[typename]

from json import JSONEncoder, loads
class WriteJson(object):
	min = max = None
	def __init__(self, *a, **kw):
		assert 'default' not in kw, "default not supported for Json, sorry"
		if PY3:
			self.fh = dsutil.WriteUnicode(*a, **kw)
			self.encode = JSONEncoder(ensure_ascii=False, separators=(',', ':')).encode
		else:
			self.fh = dsutil.WriteBytes(*a, **kw)
			self.encode = JSONEncoder(ensure_ascii=True, separators=(',', ':')).encode
	def write(self, o):
		self.fh.write(self.encode(o))
	@property
	def count(self):
		return self.fh.count
	@property
	def compression(self):
		return self.fh.compression
	def close(self):
		self.fh.close()
	def __enter__(self):
		return self
	def __exit__(self, type, value, traceback):
		self.close()
_convfuncs['json'] = WriteJson

class WriteParsedJson(WriteJson):
	"""This assumes strings are the object you wanted and parse them as json.
	If they are unparseable you get an error."""
	def write(self, o):
		if isinstance(o, str_types):
			o = loads(o)
		self.fh.write(self.encode(o))
_convfuncs['parsed:json'] = WriteParsedJson

from pickle import dumps
class WritePickle(object):
	min = max = None
	def __init__(self, *a, **kw):
		assert PY3, "Pickle columns require python 3, sorry"
		assert 'default' not in kw, "default not supported for Pickle, sorry"
		self.fh = dsutil.WriteBytes(*a, **kw)
	def write(self, o):
		self.fh.write(dumps(o, 4))
	@property
	def count(self):
		return self.fh.count
	@property
	def compression(self):
		return self.fh.compression
	def close(self):
		self.fh.close()
	def __enter__(self):
		return self
	def __exit__(self, type, value, traceback):
		self.close()
_convfuncs['pickle'] = WritePickle
