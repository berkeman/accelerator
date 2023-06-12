from datetime import datetime
from math import sin
from collections import defaultdict
from accelerator import JobWithFile, Job
from accelerator.svg import SVG

MAXDEPTH = 1000



def alljobdeps(job):
	""" Return a list of all the job's dependencies """
	res = defaultdict(list)
	# jobs
	for key, value in job.params.jobs.items():
		if not isinstance(value, (list, tuple)):
			value = [value, ]
		for val in value:
			if val:
				res['job'].append(val)
	# options Jobwithfile
	for key, value in job.params.options.items():
		if isinstance(value, JobWithFile):
			res['jwf'].append(value.job)
		# @@ handle or sorts of nested options here
	# datasets
	for key, value in job.params.datasets.items():
		if not isinstance(value, (list, tuple)):
			value = [value, ]
		for val in value:
			if val:
				res['ds'].append(val.job)
	# subjobs
#	for key, flag in job.post.subjobs.items():
#		res['sub'].append(Job(key))
	return res['ds'] + res['job'] + res['jwf']  # + res['sub']


def dsdeps(ds):
	ret = dict()
	if ds.parent:
		if isinstance(ds.parent, list):
			for item in ds.parent:
				ret[item] = 'parent'
		else:
			ret[ds.parent] = 'parent'
	if ds.previous:
		ret[ds.previous] = 'previous'
	return ret


def recurse_ds(inputitem, maxdepth=MAXDEPTH):
	edges = set()
	atmaxdepth = set()
	dones = set()
	levels = dict()
	stack = [(inputitem, 0), ]
	while stack:
		current, level = stack.pop()
		if current in dones:
			continue
		levels[current] = level
		if level >= maxdepth:
			atmaxdepth.add(current)
		else:
			for child, relation in dsdeps(current).items():
				stack.append((child, level + 1))
				edges.add((current, child, relation))
		dones.add(current)
	nodes = defaultdict(list)
	for k, v in levels.items():
		nodes[v].append(k)
	nodes = {0: nodes}
	return nodes, edges, atmaxdepth


def recurse_joblist(inputv, maxdepth=MAXDEPTH):
	# Same as recurse_jobs (see comments there), but with arbitrary
	# number of graphs, since jobs in a joblist may not be connected.
	nodes = defaultdict(lambda: defaultdict(list))
	edges = set()
	atmaxdepth = set()
	children = defaultdict(set)
	for item in inputv:
		# We only investigate children of jobs in joblist.
		# That way, we traverse jobs outside current joblist too, but only the first level.
		children[item] = sorted(alljobdeps(item))
	mergeoffsets = dict()
	graphnumber = 0  # There may be more than one graph to plot
	dones = set()
	for inputitem in inputv:
		if inputitem in dones:
			# This node belongs to an already computed graph, so skip it.
			continue
		stack = [(inputitem, 0), ]
		levels = dict()
		while stack:
			current, level = stack.pop()
			levels[current] = level
			if current in dones:
				if level > levels[current]:
					mergeoffsets[current] = max(mergeoffsets.get(current, 0), level - levels[current])
				continue
			if level >= maxdepth:
				atmaxdepth.add(current)
			else:
				for child in children[current]:
					stack.append((child, level + 1))
					edges.add((current, child))
			dones.add(current)
		stack = [(inputitem, 0), ]
		levels = dict()
		while stack:
			current, level = stack.pop()
			level = max(level, levels.get(current, 0))
			level += mergeoffsets.pop(current, 0)
			levels[current] = level
			if current in atmaxdepth:
				continue
			for child in children[current]:
				stack.append((child, level + 1))
		for k, v in levels.items():
			nodes[graphnumber][v].append(k)
		graphnumber += 1
	return nodes, edges, atmaxdepth


def recurse_jobs(inputitem, maxdepth=MAXDEPTH):
	# Create list of edges and nodes for jobs decendingt from inputitem.
	# Each job gets associated with a "level" which is the depth in a
	# job tree such that all edges goes from a lower level to a higher.
	edges = set()  # set of graph edges (i.e. node tuples)
	atmaxdepth = set()  # set of nodes that are at max recursion depth
	node2children = defaultdict(set)  # a "cache" for nodes' children
	mergeoffsets = dict()  # max difference in depth when arriving at node from different paths
	dones = set()  # nodes we are done with
	levels = dict()  # {node: recursionlevel}.  Level will be updated in second recursion.
	stack = [(inputitem, 0), ]  # list of (node, recursionlevel), start at level 0.
	# Phase 1, recurse graph
	while stack:
		current, level = stack.pop()
		if current in dones:
			# We've been here before
			if level > levels[current]:
				# This time the recursion level is deeper.  Therefore,
				# we need to increase level of this node and all nodes
				# below it accordingly.  Save level difference for now
				# and fix in next recursion below.
				mergeoffsets[current] = max(mergeoffsets.get(current, 0), level - levels[current])
			continue
		levels[current] = level
		if level >= maxdepth:
			# add to set of maxdepth nodes, and don't recurse further
			atmaxdepth.add(current)
		else:
			if current not in node2children:
				# populate "cache".  Used by second recursion too!
				node2children[current] = sorted(alljobdeps(current))
			for child in node2children[current]:
				stack.append((child, level + 1))
				edges.add((current, child))
		dones.add(current)
	# Phase 2, recurse again and fix level differences
	levels = dict()
	stack = [(inputitem, 0), ]
	while stack:
		current, level = stack.pop()
		level = max(level, levels.get(current, 0))  # always use the max depth to get here
		level += mergeoffsets.pop(current, 0)
		levels[current] = level
		if current in atmaxdepth:
			continue
		for child in node2children[current]:
			stack.append((child, level + 1))
	# Convert to same format as recurse_joblist
	nodes = defaultdict(list)
	for k, v in levels.items():
		nodes[v].append(k)
	nodes = {0: nodes}
	return nodes, edges, atmaxdepth


def jlist(urdentry, recursiondepth=100):
	g = graph()
	job2urddep = {Job(x[1]): str(k) + '/' + str(item.timestamp) for k, item in urdentry.deps.items() for x in item.joblist}
	jlist = urdentry.joblist
	jobsinurdlist = tuple(Job(item[1]) for item in reversed(jlist))
	nodes, edges, atmaxdepth = recurse_joblist(jobsinurdlist, recursiondepth)
	assert min(nodes) == 0, ('minimum level must be zero!', nodes.keys())
	xoffset = 0
	for graphnumber in nodes:
		g.insert_nodes(nodes[graphnumber], None, xoffset, atmaxdepth, jobsinurdlist, job2urddep)
		xoffset += max(nodes[graphnumber]) - min(nodes[graphnumber]) + 1
	g.insert_edges(edges)
	return g.write()


def job(inputjob, recursiondepth=100):
	g = graph()
	import time
	t0 = time.time()
	nodes, edges, atmaxdepth = recurse_jobs(inputjob, recursiondepth)
	print('therecursiontime', time.time() - t0)
	t0 = time.time()
	g.insert_nodes(nodes[0], None, 0, atmaxdepth)
	print('theinsertnodestime', time.time() - t0)
	t0 = time.time()
	g.insert_edges(edges)
	print('theinsertedgestime', time.time() - t0)
	return g.write()


def ds(ds, recursiondepth=100):
	g = graph()
	nodes, edges, atmaxdepth = recurse_ds(ds, recursiondepth)
	g.insert_nodes(nodes[0], None, 0, atmaxdepth, jobnotds=False)
	g.insert_edges_ds(edges)
	return g.write()


class graph():
	def __init__(self):
		self.svg = SVG()
		self.bbox = [None, None, None, None]
	def insert_nodes(self, nodes, labelfun, xoffset, atmaxdepth, validjobset=None, job2urddep=None, jobnotds=True):
		"""
		nodes = {level: [nodes]}
		labelfun(x) generates a label string from object x
		xoffset is leftmost position of new graph
		atmaxdepth is set of nodes that have reached recursion depth
		validjobset is the main set of jobs to plot, those outside are plotted differently
		"""
		assert labelfun is None
		for level, jobsatlevel in sorted(nodes.items()):
			adjlev = level - min(nodes)
			for ix, j in enumerate(jobsatlevel):
				x = (xoffset + adjlev + 0.3 * sin(ix)) * 160
				y = (ix - len(jobsatlevel) / 2) * 140 + sin(adjlev / 3) * 70
				notinjoblist = False
				def presentstuff(v, tit, maxlen=5):
					if v:
						nonlocal title
						title += '<br><b>%s:</b><br>' % (tit,)
						for item in v[:maxlen]:
							if tit == 'Datasets':
								title += '&nbsp&nbsp<a href=../dataset/{fn} target="_parent">{fn}</a><br>'.format(fn=item)
							elif tit == 'Subjobs':
								title += '&nbsp&nbsp<a href=../job/{fn} target="_parent">{fn}</a> (<a href=../job/{fn}/method.tar.gz/ target="_parent">{job}</a>)<br>'.format(fn=item, job=Job(item).method)
							elif tit == 'Columns':
								title += '&nbsp&nbsp%s  (%s)<br>' % (item[0], item[1].type)
							else:  # assume Job
								title += '&nbsp&nbsp<a href=../job/{job}/{fn} target="_parent">{fn}</a><br>'.format(job=j, fn=item)
						if len(v) > maxlen:
							title += '&nbsp&nbsp... and %d more.' % (len(v) - maxlen,)
				if isinstance(j, Job):
					# This is a Job
					title = ''
					if validjobset and j not in validjobset:  # i.e. job is not in this urdlist
						if job2urddep and j in job2urddep:
							notinjoblist = job2urddep[j]
						else:
							notinjoblist = True
					if j.method == 'csvimport':
						title += '<br><b>options.filename:</b> <i> %s </i><br>' % (j.params.options.filename,)
					self.svg.jobnode2(
						j, x=x, y=y,
						atmaxdepth=j in atmaxdepth,
						notinurdlist=notinjoblist,
					)
					for ix, (fun, var) in enumerate(((min, x), (max, x), (min, y), (max, y))):
						self.bbox[ix] = fun(self.bbox[ix] if not self.bbox[ix] is None else var, var)
				else:
					# This is a Dataset
					title = '<b>Dataset </b><a href=../dataset/{job} target="_parent">{job}</a>'.format(job=j)
					title += '<br>' + datetime.fromtimestamp(j.job.params.starttime).strftime("%Y-%m-%d %H:%M:%S")
					if j in atmaxdepth:
						title += '<br><b><font color="#ff0099">Reached recursion limit - no dependencies drawn!</font></b>'
					title += '<br><br>'
					title += '<b>Job: </b><a href=../job/{job} target="_parent">{job}</a>'.format(job=j.job)
					title += '<br><br>'
					if isinstance(j.parent, list):
						pv = j.parent
					else:
						pv = [j.parent, ]
					for p in pv:
						title += '<b>Parent: </b> <a href=../dataset/{ds} target="_parent">{ds}</a><br>'.format(ds=p)
					if j.previous:
						title += '<b>Previous: </b> <a href=../dataset/{ds} target="_parent">{ds}</a><br>'.format(ds=j.previous)
					title += '<br><b>Rows: </b> %s' % ('{:,d}'.format(sum(j.lines)).replace(',', '.'),)
					title += '<br>'
					presentstuff(sorted(j.columns.items()), 'Columns')
					self.svg.jobnode_ds(
						j, x=x, y=y,
						atmaxdepth=j in atmaxdepth,
						notinurdlist=notinjoblist,
					)
					for ix, (fun, var) in enumerate(((min, x), (min, y), (max, x), (max, y))):
						self.bbox[ix] = fun(self.bbox[ix] if not self.bbox[ix] is None else var, var)

				# @@@@@@@@@@@ dataset.parent as a list is not tested at all!!!!!!!!!!!!!!!!!!!!!!!!

	def insert_edges_ds(self, edges):
		self.svg.edges = edges
		for s, d, relation in edges:
			self.svg.arrow_ds(s, d, relation)

	def insert_edges(self, edges):
		self.svg.edges = edges
		for s, d in edges:
			self.svg.arrow2(s, d)

	def write(self):
		x1, y1, x2, y2 = self.bbox
		dy = y2 - y1
		if dy < 400:
			y1 = y1 - (400 - dy) // 2
		return self.svg.nodes, self.svg.edges, (-100 + x1, y1, 200 + x2 - x1, 400), self.svg.neighbour_nodes, self.svg.neighbour_edges
