from accelerator import Job
import sys

options = {'prefix': str, 'version': int}

def check(num, *want):
	job = Job('%s-%d' % (options.prefix, num))
	assert job.params.version == options.version
	assert job.params.versions.python_path
	if job.params.version > 2:
		assert job.params.versions.accelerator
	ds = job.dataset()
	want_lines = [len(w) for w in want]
	assert ds.lines == want_lines, '%s should have had %r lines but has %r' % (ds, want_lines, ds.lines,)
	for sliceno, want in enumerate(want):
		got = list(ds.iterate(sliceno, ('a', 'b',)))
		assert got == want, '%s slice %d should have had %r but had %r' % (ds, sliceno, want, got,)

def synthesis(job):
	check(
		0,
		[(b'111', b'fits in 1 byte'), (b'44444', b'fits in 5 bytes')],
		[(b'-2', b'also fits in 1 byte'), (b'55555555555', b'fits in 9 bytes')],
		[(b'333', b'needs 3 bytes'), (b'666666666666666666666', b'fits in 10 bytes')],
	)
	check(
		1,
		[(111, 'fits in 1 byte'), (44444, 'fits in 5 bytes')],
		[(-2, 'also fits in 1 byte'), (55555555555, 'fits in 9 bytes')],
		[(333, 'needs 3 bytes'), (666666666666666666666, 'fits in 10 bytes')],
	)
	check(
		2,
		[(111, 'fits in 1 byte'), (-2, 'also fits in 1 byte'), (55555555555, 'fits in 9 bytes'), (333, 'needs 3 bytes'), (666666666666666666666, 'fits in 10 bytes')],
		[],
		[(44444, 'fits in 5 bytes')],
	)
	# Test for accidental recursion.
	sys.setrecursionlimit(49)
	ds51 = Job('%s-%d' % (options.prefix, 51)).dataset()
	assert len(ds51.chain()) == 50, '%s should have had a dataset chain of length 50' % (job,)
	# And check the chain actually contains the expected stuff (i.e. nothing past the first ds).
	# (Also to check that iterating the chain doesn't recurse more.)
	ds2 = Job('%s-%d' % (options.prefix, 2)).dataset()
	assert list(ds2.iterate(None)) == list(ds51.iterate_chain(None))
