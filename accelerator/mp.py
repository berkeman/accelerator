############################################################################
#                                                                          #
# Copyright (c) 2021-2022 Carl Drougge                                     #
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

import os
import sys
import select
import signal
import fcntl
import struct
import pickle
import errno
from accelerator.compat import QueueEmpty, monotonic, selectors


assert select.PIPE_BUF >= 512, "POSIX says PIPE_BUF is at least 512, you have %d" % (select.PIPE_BUF,)

PIPE_BUF = min(select.PIPE_BUF, 65536)
MAX_PART = PIPE_BUF - 6


def _nb(fd):
	fl = fcntl.fcntl(fd, fcntl.F_GETFL)
	fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)


def _mk_sel(fd, ev):
	sel = selectors.DefaultSelector()
	sel.register(fd, ev)
	return sel


# This provides some of the functionality of multiprocessing.Queue but
# without using any locks, instead relying on writes up to PIPE_BUF being
# atomic. No threads are used.
#
# Only the creating process can .get(). .get() can take a timeout.
# Only child processes can .put(). .put() blocks until the pipe will take
# all the data.
# A dying writer will never corrupt or deadlock the queue, but can cause a
# memory leak in the reading process (until the queue object is destroyed).
# Large messages are probably quite inefficient.
#
# In short, you often can't use this. And when you do, you have to be careful.

class LockFreeQueue:
	def __init__(self):
		self._r_sel = self._w_sel = None
		self.r, self.w = os.pipe()
		_nb(self.r)
		_nb(self.w)
		self._buf = b''
		self._pid = os.getpid()
		self._partial = {}

	def make_writer(self):
		os.close(self.r)
		self.r = -1
		self._w_sel = _mk_sel(self.w, selectors.EVENT_WRITE)

	def make_reader(self):
		os.close(self.w)
		self.w = -1
		self._r_sel = _mk_sel(self.r, selectors.EVENT_READ)

	def close(self):
		if self._r_sel:
			self._r_sel.close()
			self._r_sel = None
		if self._w_sel:
			self._w_sel.close()
			self._w_sel = None
		if self.r != -1:
			os.close(self.r)
			self.r = -1
		if self.w != -1:
			os.close(self.w)
			self.w = -1

	__del__ = close

	def get(self, block=True, timeout=0):
		assert os.getpid() == self._pid, "can only .get in creating process"
		assert self.w == -1, "call make_reader first"
		if timeout:
			deadline = monotonic() + timeout
		need_data = False
		eof = False
		while True:
			if not eof:
				try:
					data = os.read(self.r, PIPE_BUF)
					if not data:
						eof = True
					self._buf += data
					need_data = False
				except OSError:
					pass
			if len(self._buf) >= 6:
				z, pid = struct.unpack('<HI', self._buf[:6])
				assert pid, "all is lost"
				if len(self._buf) < 6 + z:
					need_data = True
				else:
					data = self._buf[6:6 + z]
					self._buf = self._buf[6 + z:]
					if pid not in self._partial:
						want_len = struct.unpack("<I", data[:4])[0]
						have = [data[4:]]
						have_len = len(have[0])
					else:
						want_len, have, have_len = self._partial[pid]
						have.append(data)
						have_len += len(data)
					if have_len == want_len:
						self._partial.pop(pid, None)
						data = b''.join(have)
						return pickle.loads(data)
					else:
						self._partial[pid] = (want_len, have, have_len)
			if len(self._buf) < 6 or need_data:
				if eof:
					raise QueueEmpty()
				if not block:
					if not self._r_sel.select(0):
						raise QueueEmpty()
				elif timeout:
					time_left = deadline - monotonic()
					if time_left <= 0:
						raise QueueEmpty()
					self._r_sel.select(time_left)
				else:
					self._r_sel.select()

	def put(self, msg):
		pid = os.getpid()
		assert pid != self._pid, "can only .put in other processes"
		assert self.r == -1, "call make_writer first"
		msg = pickle.dumps(msg, pickle.HIGHEST_PROTOCOL)
		msg = struct.pack('<I', len(msg)) + msg
		offset = 0
		while offset < len(msg):
			part = msg[offset:offset + MAX_PART]
			part = struct.pack('<HI', len(part), pid) + part
			offset += MAX_PART
			while True:
				self._w_sel.select()
				try:
					wlen = os.write(self.w, part)
				except OSError as e:
					if e.errno == errno.EAGAIN:
						wlen = 0
					else:
						raise
				if wlen:
					if wlen != len(part):
						print("OS violates PIPE_BUF guarantees, all is lost.", file=sys.stderr)
						while True:
							try:
								# this should eventually make the other side read PID 0
								os.write(self.w, b'\0')
							except OSError:
								pass
					break

	def try_notify(self):
		pid = os.getpid()
		msg = struct.pack('<HII', 6, pid, 2) + b'N.' # pickled None
		try:
			os.write(self.w, msg)
			return True
		except OSError:
			return False


# This is a partial replacement for multiprocessing.Process.
# It doesn't work if you use the rest of the mp machinery (like Queues)
# and always uses os.fork(). It exists because multiprocessing.Process
# has scaling issues with many children.

class SimplifiedProcess:
	def __init__(self, target, args=(), kwargs={}, name=None):
		sys.stdout.flush()
		sys.stderr.flush()
		self.pid = os.fork()
		if self.pid:
			self.name = name
			self._alive = True
			return
		rc = 1
		try:
			target(*args, **kwargs)
			rc = 0
		except KeyboardInterrupt:
			signal.signal(signal.SIGINT, signal.SIG_DFL)
			os.kill(os.getpid(), signal.SIGINT)
		finally:
			os._exit(rc)

	def is_alive(self):
		self._wait(False)
		return self._alive

	def _wait(self, block):
		if not self._alive:
			return
		pid, status = os.waitpid(self.pid, 0 if block else os.WNOHANG)
		if pid:
			assert pid == self.pid
			self._alive = False
			if os.WIFEXITED(status):
				self.exitcode = os.WEXITSTATUS(status)
			elif os.WIFSIGNALED(status):
				self.exitcode = -os.WTERMSIG(status)
			else:
				self.exitcode = -999

	def join(self):
		self._wait(True)