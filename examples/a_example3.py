jobs = ('first', 'second',)

def synthesis(job):
	res1=jobs.first.load()
	res2=jobs.second.load()
	s = 'Hello from \"%s\"' % (job.method,)
	s += '\n  second job is \"%s\"' % (jobs.second.method,)
	s += '\n  first job took %f seconds' % (jobs.first.post.profile.total,)
	s += '\n  now I store something in \"ex3file\"'
	job.save(dict(a=3, b='foo'), 'ex3file')
	return s
