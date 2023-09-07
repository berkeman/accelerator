############################################################################
#                                                                          #
# Copyright (c) 2017 eBay Inc.                                             #
# Modifications copyright (c) 2019-2023 Carl Drougge                       #
# Modifications copyright (c) 2019-2020 Anders Berkeman                    #
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

import os
import re

from collections import namedtuple, OrderedDict
from functools import wraps

from accelerator.compat import unicode, PY2, PY3, open, iteritems, FileNotFoundError
from accelerator.error import NoSuchJobError, NoSuchWorkdirError, NoSuchDatasetError, AcceleratorError


# WORKDIRS should live in the Automata class, but only for callers
# (methods read it too, though hopefully only through the functions in this module)

WORKDIRS = {}


def dirnamematcher(name):
	return re.compile(re.escape(name) + r'-[0-9]+$').match


def _assert_is_normrelpath(path, dirtype):
	norm = os.path.normpath(path)
	if (norm != path and norm + '/' != path) or norm.startswith('/'):
		raise AcceleratorError('%r is not a normalised relative path' % (path,))
	if norm == '..' or norm.startswith('../'):
		raise AcceleratorError('%r is above the %s dir' % (path, dirtype))


def _cachedprop(meth):
	@property
	@wraps(meth)
	def wrapper(self):
		if meth.__name__ not in self._cache:
			self._cache[meth.__name__] = meth(self)
		return self._cache[meth.__name__]
	return wrapper

_cache = {}
_nodefault = object()

class Job(unicode):
	"""
	A string representing a jobid, with extra properties to get
	information and data from an existing job.  Decays to a (unicode)
	string when pickled.
	"""

	__slots__ = ('workdir', 'number', '_cache')

	def __new__(cls, jobid, method=None):
		k = (jobid, method)
		if k in _cache:
			return _cache[k]
		obj = unicode.__new__(cls, jobid)
		try:
			obj.workdir, tmp = jobid.rsplit('-', 1)
			obj.number = int(tmp)
		except ValueError:
			raise NoSuchJobError('Not a valid jobid: "%s".' % (jobid,))
		obj._cache = {}
		if method:
			obj._cache['method'] = method
		_cache[k] = obj
		return obj

	@classmethod
	def _create(cls, name, number):
		return Job('%s-%d' % (name, number,))

	@_cachedprop
	def method(self):
		"""
		Name of the method that created the job.  When used in a build script, the
		build()-call "name" parameter overrides this.
		"""

		return self.params.method

	@_cachedprop
	def input_directory(self):
		"""Return the name of the input directory where project input files
		are stored."""
		return self.params.get('input_directory', None)

	@property
	def path(self):
		"""Return the filesystem path to this job."""
		if self.workdir not in WORKDIRS:
			raise NoSuchWorkdirError('Not a valid workdir: "%s"' % (self.workdir,))
		return os.path.join(WORKDIRS[self.workdir], self)

	def filename(self, filename, sliceno=None):
		"""Create a full filename for a file stored in this job."""
		if sliceno is not None:
			filename = '%s.%d' % (filename, sliceno,)
		return os.path.join(self.path, filename)

	def open(self, filename, mode='r', sliceno=None, encoding=None, errors=None):
		"""Wrapper around open() that can read files from other jobs.  Note
		that it will not permit writes."""
		assert 'r' in mode, "Don't write to other jobs"
		if 'b' not in mode and encoding is None:
			encoding = 'utf-8'
		return open(self.filename(filename, sliceno), mode, encoding=encoding, errors=errors)

	def files(self, pattern='*'):
		"""Return a set of all files created by the job."""
		from fnmatch import filter
		return set(filter(self.post.files, pattern))

	def withfile(self, filename, sliced=False, extra=None):
		"""Return a ``JobWithFile`` object pointing to a file in this job."""
		return JobWithFile(self, filename, sliced, extra)

	@_cachedprop
	def params(self):
		"""All parameters for this job.  (Basically a dump of the job's ``setup.json``)"""
		from accelerator.extras import job_params
		return job_params(self)

	@_cachedprop
	def version(self):
		# this is self.params.version, but without fully loading the params
		# (unless already loaded).
		if 'params' in self._cache:
			return self._cache['params'].version
		from accelerator.setupfile import load_setup
		return load_setup(self).version

	@_cachedprop
	def post(self):
		"""Post build information for this job.  (Basically a dump of the job's ``post.json``.)"""
		from accelerator.extras import job_post
		return job_post(self)

	def load(self, filename='result.pickle', sliceno=None, encoding='bytes', default=_nodefault):
		"""Load a pickle file from this job."""
		from accelerator.extras import pickle_load
		try:
			return pickle_load(self.filename(filename, sliceno), encoding=encoding)
		except FileNotFoundError:
			if default is _nodefault:
				raise
			return default

	def json_load(self, filename='result.json', sliceno=None, unicode_as_utf8bytes=PY2, default=_nodefault):
		"""Load a JSON file from this job."""
		from accelerator.extras import json_load
		try:
			return json_load(self.filename(filename, sliceno), unicode_as_utf8bytes=unicode_as_utf8bytes)
		except FileNotFoundError:
			if default is _nodefault:
				raise
			return default

	def dataset(self, name='default'):
		"""Return a ``Dataset`` object for a dataset in this job."""
		from accelerator.dataset import Dataset
		return Dataset(self, name)

	@_cachedprop
	def datasets(self):
		"""Return a ``Datasetlist`` of all datasets in this job."""
		from accelerator.dataset import job_datasets
		return job_datasets(self)

	def output(self, what=None):
		"""
		Return what the job printed to stdout and stderr.
		The parameter "what" could be an integer specifying a specific slice,
		or one of 'prepare', 'analysis', 'synthesis', or None
		"""
		if what == 'parts':
			as_parts = True
			what = None
		else:
			as_parts = False
		if isinstance(what, int):
			fns = [what]
		else:
			assert what in (None, 'prepare', 'analysis', 'synthesis'), 'Unknown output %r' % (what,)
			if what in (None, 'analysis'):
				fns = list(range(self.params.slices))
				if what is None:
					fns = ['prepare'] + fns + ['synthesis']
			else:
				fns = [what]
		res = OrderedDict()
		for k in fns:
			fn = self.filename('OUTPUT/' + str(k))
			if os.path.exists(fn):
				with open(fn, 'rt', encoding='utf-8', errors='backslashreplace') as fh:
					res[k] = fh.read()
		if as_parts:
			return res
		else:
			return ''.join(res.values())

	def link_result(self, filename='result.pickle', linkname=None):
		"""Put a symlink in result_directory pointing to a file in this job.
		Only use this in a build script."""
		from accelerator.g import running
		assert running == 'build', "Only link_result from a build script"
		from accelerator.shell import cfg
		_assert_is_normrelpath(filename, 'job')
		if linkname is None:
			linkname = os.path.basename(filename.rstrip('/'))
		_assert_is_normrelpath(linkname, 'result')
		if linkname.endswith('/'):
			if filename.endswith('/'):
				linkname = linkname.rstrip('/')
			else:
				linkname += os.path.basename(filename)
		source_fn = os.path.join(self.path, filename)
		assert os.path.exists(source_fn), "Filename \"%s\" does not exist in jobdir \"%s\"!" % (filename, self.path)
		result_directory = cfg['result_directory']
		dest_fn = result_directory
		for part in linkname.split('/'):
			if not os.path.exists(dest_fn):
				os.mkdir(dest_fn)
			elif dest_fn != result_directory and os.path.islink(dest_fn):
				raise AcceleratorError("Refusing to create link %r: %r is a symlink" % (linkname, dest_fn))
			dest_fn = os.path.join(dest_fn, part)
		try:
			os.remove(dest_fn + '_')
		except OSError:
			pass
		os.symlink(source_fn, dest_fn + '_')
		os.rename(dest_fn + '_', dest_fn)

	def chain(self, length=-1, reverse=False, stop_job=None):
		"""Like ``Dataset.chain`` but for jobs."""
		if isinstance(stop_job, dict):
			assert len(stop_job) == 1, "Only pass a single stop_job={job: name}"
			stop_job, stop_name = next(iteritems(stop_job))
			if stop_job:
				stop_job = Job(stop_job).params.jobs.get(stop_name)
		chain = []
		current = self
		while length != len(chain) and current and current != stop_job:
			chain.append(current)
			current = current.params.jobs.get('previous')
		if not reverse:
			chain.reverse()
		return chain

	# Look like a string after pickling
	def __reduce__(self):
		return unicode, (unicode(self),)


class CurrentJob(Job):
	"""The currently running job (as passed to the method),
	with extra functions for writing data."""

	__slots__ = ('input_directory',)

	def __new__(cls, jobid, params):
		obj = Job.__new__(cls, jobid, params.method)
		obj._cache['params'] = params
		obj.input_directory = params.input_directory
		return obj

	def finish_early(self, result=None):
		"""Finish job (successfully) without running later stages."""
		from accelerator.launch import _FinishJob
		raise _FinishJob(result)

	def save(self, obj, filename='result.pickle', sliceno=None, temp=None, background=False):
		"""
		Save obj as a Python pickle file in the current job's directory.

		If called in ``analysis()``, data from all slices could be
		saved to the same "filename" by setting ``sliceno``.

		If ``temp`` is set, the saved file will be removed upon job
		completion.

		Set ``background`` to move the actual save operation to a
		separate process.
		"""
		from accelerator.extras import pickle_save
		return pickle_save(obj, filename, sliceno, temp=temp, background=background)

	def json_save(self, obj, filename='result.json', sliceno=None, sort_keys=True, temp=None, background=False):
		"""
		Save obj as a JSON file in the current job's directory.

		In addition to the arguments it shares with ``save()``, it is
		possible to sort the keys in the JSON output for
		reproducibility using the ``sort_keys`` argument.
		"""
		from accelerator.extras import json_save
		return json_save(obj, filename, sliceno, sort_keys=sort_keys, temp=temp, background=background)

	def datasetwriter(self, columns={}, filename=None, hashlabel=None, hashlabel_override=False, caption=None, previous=None, name='default', parent=None, meta_only=False, for_single_slice=None, copy_mode=False, allow_missing_slices=False):
		"""
		Use this to create a dataset.

		:param dict columns: Dictionary from column names to data types.
		:param str filename: Name of dataset.
		:param str hashlabel: set to a colum's name if hash partitioned.

		"""
		from accelerator.dataset import DatasetWriter
		return DatasetWriter(columns=columns, filename=filename, hashlabel=hashlabel, hashlabel_override=hashlabel_override, caption=caption, previous=previous, name=name, parent=parent, meta_only=meta_only, for_single_slice=for_single_slice, copy_mode=copy_mode, allow_missing_slices=allow_missing_slices)

	def open(self, filename, mode='r', sliceno=None, encoding=None, errors=None, temp=None):
		"""
		"Mostly like standard open, but with ``sliceno`` and ``temp`` just like ``save()``.
		It must be used as context manager

		    with job.open(...) as fh:

		and the file will have a temp name until the with block ends.
		"""
		if 'r' in mode:
			return Job.open(self, filename, mode, sliceno, encoding, errors)
		if 'b' not in mode and encoding is None:
			encoding = 'utf-8'
		if PY3 and 'x' not in mode:
			mode = mode.replace('w', 'x')
		def _open(fn, _mode):
			# ignore the passed mode, use the one we have
			return open(fn, mode, encoding=encoding, errors=errors)
		from accelerator.extras import FileWriteMove
		fwm = FileWriteMove(self.filename(filename, sliceno), temp=temp)
		fwm._open = _open
		return fwm

	def register_file(self, filename):
		"""
		Record a file produced by this job.  Normally you would use
		``job.open()`` to have this happen automatically, but if the
		file was produced in a way where that is not practical you can
		use this to register it.
		"""
		filename = self.filename(filename)
		assert os.path.exists(filename)
		from accelerator.extras import saved_files
		saved_files[filename] = 0

	def input_filename(self, *parts):
		"""
		Return a full filename to a file stored in the
		``input_directory``.
		"""
		return os.path.join(self.input_directory, *parts)

	def open_input(self, filename, mode='r', encoding=None, errors=None):
		"""
		Like standard ``open()``, but opens files stored in the
		``input_directory``.
		"""
		assert 'r' in mode, "Don't write to input files"
		if 'b' not in mode and encoding is None:
			encoding = 'utf-8'
		return open(self.input_filename(filename), mode, encoding=encoding, errors=errors)


class NoJob(Job):
	"""
	A empty string that is used for unset job arguments, with some properties
	that may still make sense on an unset job.
	Also provides .load() and .load_json() methods that return None as long
	as no filename or sliceno was specified, and .files() that always returns
	an empty set.
	"""

	__slots__ = ()

	# functions you shouldn't call on this
	filename = link_result = open = params = path = post = withfile = None

	workdir = None
	method = output = ''
	number = version = -1

	def __new__(cls):
		return unicode.__new__(cls, '')

	def dataset(self, name='default'):
		raise NoSuchDatasetError('NoJob has no datasets')

	@property
	def datasets(self):
		from accelerator.dataset import DatasetList
		return DatasetList()

	def files(self, pattern='*'):
		return set()

	def load(self, filename=None, sliceno=None, encoding='bytes', default=_nodefault):
		if default is not _nodefault:
			return default
		if filename is not None or sliceno is not None:
			raise NoSuchJobError('Can not load named / sliced file on <NoJob>')
		return None

	def json_load(self, filename=None, sliceno=None, unicode_as_utf8bytes=PY2, default=_nodefault):
		return self.load(filename, sliceno, default=default)

NoJob = NoJob()


class JobWithFile(namedtuple('JobWithFile', 'job name sliced extra')):
	__slots__ = ()

	def __new__(cls, job, name, sliced=False, extra=None):
		assert not name.startswith('/'), "Specify relative filenames to JobWithFile"
		return tuple.__new__(cls, (Job(job), name, bool(sliced), extra,))

	def filename(self, sliceno=None):
		if sliceno is None:
			assert not self.sliced, "A sliced file requires a sliceno"
		else:
			assert self.sliced, "An unsliced file can not have a sliceno"
		return self.job.filename(self.name, sliceno)

	def load(self, sliceno=None, encoding='bytes', default=_nodefault):
		"""blob.load this file"""
		from accelerator.extras import pickle_load
		try:
			return pickle_load(self.filename(sliceno), encoding=encoding)
		except FileNotFoundError:
			if default is _nodefault:
				raise
			return default

	def json_load(self, sliceno=None, unicode_as_utf8bytes=PY2, default=_nodefault):
		from accelerator.extras import json_load
		try:
			return json_load(self.filename(sliceno), unicode_as_utf8bytes=unicode_as_utf8bytes)
		except FileNotFoundError:
			if default is _nodefault:
				raise
			return default

	def open(self, mode='r', sliceno=None, encoding=None, errors=None):
		return self.job.open(self.name, mode, sliceno, encoding, errors)
