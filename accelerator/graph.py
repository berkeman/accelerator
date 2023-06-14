from time import time
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
	return nodes, edges, atmaxdepth


def recurse_joblist(inputv, maxdepth=MAXDEPTH):
	# Same as recurse_jobs (see comments there), but with arbitrary
	# number of graphs, since jobs in a joblist may not be connected.
	nodes = defaultdict(list)
	edges = set()
	atmaxdepth = set()
	children = defaultdict(set)
	parents = defaultdict(set)
	for item in inputv:
		deps = sorted(alljobdeps(item))
		children[item] = deps
		for d in deps:
			parents[d].add(item)
	joins = {key: sorted(val) for key, val in parents.items() if len(val) > 1}
	starts = set(inputv) - set(parents)
	dones = set()
	stack = list( (x, 0) for x in starts)
	levels = dict()
	while stack:
		current, level = stack.pop()
		if current in joins:
			level = max(level, levels[current]) if current in levels else level
			if set(parents[current]) - set(dones):
				levels[current] = level
				continue
		for child in children[current]:
			edges.add((current, child))
			if child not in dones:
				stack.insert(0, (child, level + 1))
		levels[current] = level
		dones.add(current)
	for k, v in levels.items():
		nodes[v].append(k)
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
	return nodes, edges, atmaxdepth


def jlist(urdentry, recursiondepth=100):
	g = graph()
	job2urddep = {Job(x[1]): str(k) + '/' + str(item.timestamp) for k, item in urdentry.deps.items() for x in item.joblist}
	jlist = urdentry.joblist
	jobsinurdlist = tuple(Job(item[1]) for item in reversed(jlist))
	nodes, edges, atmaxdepth = recurse_joblist(jobsinurdlist, recursiondepth)
	names = {}
	for name, jobid in jlist:
		names[jobid] = name
		g.insert_nodes(nodes, names, 0, atmaxdepth, jobsinurdlist, job2urddep)
	g.insert_edges(edges)
	return g.write()


def job(inputjob, recursiondepth=100):
	g = graph()
	import time
	t0 = time.time()
	nodes, edges, atmaxdepth = recurse_jobs(inputjob, recursiondepth)
	print('therecursiontime', time.time() - t0)
	t0 = time.time()
	g.insert_nodes(nodes, None, 0, atmaxdepth)
	print('theinsertnodestime', time.time() - t0)
	t0 = time.time()
	g.insert_edges(edges)
	print('theinsertedgestime', time.time() - t0)
	return g.write()


def ds(ds, recursiondepth=100):
	g = graph()
	nodes, edges, atmaxdepth = recurse_ds(ds, recursiondepth)
	g.insert_nodes(nodes, None, 0, atmaxdepth, jobnotds=False)
	g.insert_edges_ds(edges)
	return g.write()


class graph():
	def __init__(self):
		self.svg = SVG()
		self.bbox = [None, None, None, None]
	def insert_nodes(self, nodes, jobnames, xoffset, atmaxdepth, validjobset=None, job2urddep=None, jobnotds=True):
		"""
		nodes = {level: [nodes]}
		labelfun(x) generates a label string from object x
		xoffset is leftmost position of new graph
		atmaxdepth is set of nodes that have reached recursion depth
		validjobset is the main set of jobs to plot, those outside are plotted differently
		"""
		for level, jobsatlevel in sorted(nodes.items()):
			adjlev = level - min(nodes)
			for ix, j in enumerate(jobsatlevel):
				x = (xoffset + adjlev + 0.3 * sin(ix)) * 160
				y = (ix - len(jobsatlevel) / 2) * 140 + sin(adjlev / 3) * 70
				notinjoblist = False
				if isinstance(j, Job):
					# This is a Job
					if validjobset and j not in validjobset:  # i.e. job is not in this urdlist
						if job2urddep and j in job2urddep:
							notinjoblist = job2urddep[j]
						else:
							notinjoblist = True
					self.svg.jobnode2(
						j, x=x, y=y,
						name=jobnames.get(j) if jobnames else None,
						atmaxdepth=j in atmaxdepth,
						notinurdlist=notinjoblist,
					)
				else:
					# This is a Dataset
					self.svg.jobnode_ds(
						j, x=x, y=y,
						atmaxdepth=j in atmaxdepth,
						notinurdlist=None,
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
		dy = min(400, max(100, dy))
		return self.svg.nodes, self.svg.edges, (-50 + x1, y1 - 50, 100 + x2 - x1, dy + 150), self.svg.neighbour_nodes, self.svg.neighbour_edges
