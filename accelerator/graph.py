from math import sin
from collections import defaultdict
from datetime import datetime
from accelerator import JobWithFile, Job
from accelerator import DotDict

MAXDEPTH = 1000


def jobdeps(job):
	""" Return all the job's dependencies """
	res = set()
	# jobs
	for key, value in job.params.jobs.items():
		if not isinstance(value, (list, tuple)):
			value = [value, ]
		for val in value:
			if val:
				res.add(val)
	# options Jobwithfile
	for key, value in job.params.options.items():
		if isinstance(value, JobWithFile):
			res.add(value.job)
		# @@ handle or sorts of nested options here
	# datasets
	for key, value in job.params.datasets.items():
		if not isinstance(value, (list, tuple)):
			value = [value, ]
		for val in value:
			if val:
				res.add(val.job)
	return res


def dsdeps(ds):
	""" return all the dataset's parents and previous """
	ret = dict()
	if ds.parent:
		ret[ds.parent] = 'parent'
	if ds.previous:
		ret[ds.previous] = 'previous'
	return ret


def recurse_joblist(inputv):
	# This is a breadth-first algo, that computes the level of each
	# join node to be max of all its parent's levels.
	edges = set()
	atmaxdepth = set()  # @@@ currently not implemented, this algo recurses everything!
	children = defaultdict(set)
	parents = defaultdict(set)
	for item in inputv:
		deps = sorted(jobdeps(item))
		children[item] = deps
		for d in deps:
			parents[d].add(item)
	joins = {key: sorted(val) for key, val in parents.items() if len(val) > 1}
	starts = set(inputv) - set(parents)
	dones = set()
	stack = list((None, x, 0) for x in starts)
	levels = dict()
	joinedparents = defaultdict(set)
	while stack:
		parent, current, level = stack.pop()
		if current in joins:
			level = max(level, levels[current]) if current in levels else level
			levels[current] = level
			joinedparents[current].add(parent)
			if joinedparents[current] == set(parents[current]):
				pass
			else:
				continue
		levels[current] = level
		for child in children[current]:
			edges.add((current, child, None))
			if child not in dones:
				stack.insert(0, (current, child, level + 1))
		dones.add(current)
	nodes = defaultdict(list)
	for k, v in levels.items():
		nodes[v].append(k)
	return nodes, edges, atmaxdepth


def recurse_jobs(inputitem, maxdepth=MAXDEPTH):
	# Depth first algo, that stores max differences in level when two
	# or more parents enter a node.  On a second recursion, this delta
	# difference is added to the subgraph having the node as root.
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
				node2children[current] = sorted(jobdeps(current))
			for child in node2children[current]:
				stack.append((child, level + 1))
				edges.add((current, child, None))
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
	nodes = defaultdict(list)
	for k, v in levels.items():
		nodes[v].append(k)
	return nodes, edges, atmaxdepth


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


def jlist(urdentry):
	g = graph()
	job2urddep = {Job(x[1]): str(k) + '/' + str(item.timestamp) for k, item in urdentry.deps.items() for x in item.joblist}
	jlist = urdentry.joblist
	jobsinurdlist = tuple(Job(item[1]) for item in reversed(jlist))
	nodes, edges, atmaxdepth = recurse_joblist(jobsinurdlist)
	names = {}
	for name, jobid in jlist:
		names[jobid] = name
	return g.creategraph(nodes, edges, atmaxdepth, names, jobsinurdlist, job2urddep)


def job(inputjob, recursiondepth=100):
	g = graph()
	nodes, edges, atmaxdepth = recurse_jobs(inputjob, recursiondepth)
	return g.creategraph(nodes, edges, atmaxdepth)


def ds(ds, recursiondepth=100):
	g = graph()
	nodes, edges, atmaxdepth = recurse_ds(ds, recursiondepth)
	return g.creategraph(nodes, edges, atmaxdepth)


class graph:
	def __init__(self):
		self.nodes = dict()
		self.edges = dict()
		self.neighbour_nodes = defaultdict(set)
		self.neighbour_edges = defaultdict(set)
		self.bbox = [None, None, None, None]

	def creategraph(self, nodes, edges, atmaxdeph, jobnames={}, jobsinurdlist=set(), job2urddep={}):
		nodeids = {n: 'node' + str(ix) for ix, n in enumerate(sorted(set.union(*(set(nn) for nn in nodes.values()))))}
		self.insert_nodes(nodes, edges, atmaxdeph, jobnames, jobsinurdlist, job2urddep)
		for key, n in self.nodes.items():
			n.nodeid = nodeids[key]
		self.nodes = {n.nodeid: n for n in self.nodes.values()}
		e2 = set()
		for s, d, x in edges:
			e2.add((nodeids[s], nodeids[d], x))
		edges = e2
		self.insert_edges(edges)

		# do some adjustments to the bounding box
		x1, y1, x2, y2 = self.bbox
		dy = max(100, y2 - y1)
		dx = max(100, x2 - x1)
		self.bbox = [x1 - 50, y1 - 50, dx + 100, dy + 100]
		return dict(
			nodes=self.nodes,
			edges=self.edges,
			bbox=self.bbox,
			neighbour_nodes=self.neighbour_nodes,
			neighbour_edges=self.neighbour_edges
		)

	def insert_nodes(self, nodes, edges, atmaxdepth, jobnames, validjobset, job2urddep):
		class Ordering:
			"""
			The init function takes the first level of nodes as
			input.  The update function takes each consecutive level
			of nodes as input.  It returns two lists, the first
			contains the nodes in sorted order, and the second is a
			positive integer offset (starting at zero) indicating in
			which order the nodes should be drawn.
			"""
			def __init__(self, nodes):
				self.order = {x: str(ix) for ix, x in enumerate(sorted(nodes))}
			def update(self, nodes):
				nodes = sorted(nodes, key=lambda x: self.order[x])
				orders = tuple(int(self.order[n]) for n in nodes)
				for n in nodes:
					for ix, c in enumerate(sorted(children[n])):
						if c not in self.order:
							self.order[c] = self.order[n] + str(ix)
					self.order.pop(n)
				for ix, (key, val) in enumerate(sorted(self.order.items(), key=lambda x: x[1])):
					self.order[key] = str(ix)
				return nodes, orders
		order = Ordering(nodes[0])
		children = defaultdict(set)
		for s, d, _ in edges:
			children[s].add(d)
		for level, jobsatlevel in sorted(nodes.items()):
			jobsatlevel, offset = order.update(jobsatlevel)
			for ix, (j, ofs) in enumerate(zip(jobsatlevel, offset)):
				x = 160 * (level + 0.3 * sin(ix))
				y = 140 * ofs + 70 * sin(level / 3)
				for i, (fun, var) in enumerate(((min, x), (min, y), (max, x), (max, y))):
					self.bbox[i] = fun(self.bbox[i] if not self.bbox[i] is None else var, var)
				if isinstance(j, Job):
					notinjoblist = False
					if validjobset and j not in validjobset:  # i.e. job is not in this urdlist
						if job2urddep and j in job2urddep:
							notinjoblist = job2urddep[j]  # but in a dependency urdlist
						else:
							notinjoblist = True
					self.nodes[j] = DotDict(
						jobid=str(j), x=x, y=y,
						atmaxdepth=j in atmaxdepth,
						timestamp=datetime.fromtimestamp(j.params.starttime).strftime("%Y-%m-%d %H:%M:%S"),
						# specific to job
						method=j.method,
						files=sorted(j.files()),
						datasets=j.datasets,
						subjobs=tuple((x, Job(x).method) for x in j.post.subjobs),
						name=jobnames.get(j) if jobnames else None,
						notinurdlist=notinjoblist,
					)
				else:
					self.nodes[j] = DotDict(
						jobid=str(j.job), x=x, y=y,
						atmaxdepth=j in atmaxdepth,
						timestamp=datetime.fromtimestamp(j.job.params.starttime).strftime("%Y-%m-%d %H:%M:%S"),
						ds=str(j),
						method=j.job.method,
						# specific to ds
						columns=tuple((key, val.type) for key, val in j.columns.items()),
						lines="%d x % s" % (len(j.columns), '{:,}'.format(sum(j.lines)).replace(',', ' ')),
					)

	def insert_edges(self, edges):
		self.edges = edges
		for s, d, _ in edges:
			edgekey = ''.join((s, d))
			self.neighbour_nodes[s].add(d)
			self.neighbour_nodes[d].add(s)
			self.neighbour_edges[s].add(edgekey)
			self.neighbour_edges[d].add(edgekey)
