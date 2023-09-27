from math import sin, cos, atan, pi, tan
from collections import defaultdict
from datetime import datetime
from html import escape
from json import dumps
from accelerator import JobWithFile, Job
from accelerator import DotDict
from accelerator.compat import url_quote

MAXDEPTH = 10
arrowlen = 15
arrowangle = pi / 8


def expandtoset(what, fun=lambda x: x):
	if what:
		if not isinstance(what, (list, tuple)):
			what = [what, ]
		return set(fun(item) for item in what)
	return set()


def jobdeps(job):
	""" Return all the job's dependencies """
	res = defaultdict(set)
	for key, value in job.params.jobs.items():
		if value:
			res['jobs.' + key].update(expandtoset(value))
	for key, value in job.params.datasets.items():
		if value:
			res['datasets.' + key].update(expandtoset(value, lambda x: x.job))
	# options Jobwithfile
	namespace = set()
	def recurse(options, name=''):
		if isinstance(options, JobWithFile):  # must happen before tuple
			res['jwf' + name].add(options.job)
			namespace.add(name)
		elif isinstance(options, dict):
			for key, val in options.items():
				recurse(val, '.'.join((name, key)))
		elif isinstance(options, (list, tuple, set)):
			for item in options:
				recurse(item, name)
	recurse(job.params.options)
	return res


def dsdeps(ds):
	""" return all the dataset's parents and previous """
	res = defaultdict(set)
	if ds:
		if ds.parent:
			res['parent'].update(expandtoset(ds.parent))
		if ds.previous:
			res['previous'].add(ds.previous)
	return res


def recurse_joblist(inputjoblist):
	# This is a breadth-first algo, that computes the level of each
	# join node to be max of all its parent's levels.
	edges = set()
	atmaxdepth = set()  # @@@ currently not implemented, this algo recurses everything!
	children = defaultdict(dict)
	parents = defaultdict(set)
	for item in inputjoblist:
		deps = jobdeps(item)
		children[item] = deps
		for d in deps.values():
			for dd in d:
				parents[dd].add(item)
	joinnodes = {key: sorted(val) for key, val in parents.items() if len(val) > 1}
	starts = set(inputjoblist) - set(parents)
	dones = set()
	stack = [(None, x, 0) for x in starts]  # (parent, current, level)
	levels = {}
	joinedparents = defaultdict(set)
	while stack:
		parent, current, level = stack.pop()
		if current in joinnodes:
			level = max(level, levels.get(current, level))
			levels[current] = level
			joinedparents[current].add(parent)
			if joinedparents[current] != parents[current]:
				continue
		levels[current] = level
		for key, childs in children[current].items():
			for child in childs:
				edges.add((current, child, key))
				if child not in dones:
					stack.append((current, child, level + 1))
		dones.add(current)
	nodes = defaultdict(list)
	for n, lev in levels.items():
		nodes[lev].append(n)
	return nodes, edges, atmaxdepth


def recurse_jobsords(inputitem, depsfun, maxdepth=MAXDEPTH):
	# Depth first algo.  When multiple paths join in a node, the max
	# difference in level between the paths is stored.  In a second
	# recursion, this delta difference is added to the subgraph having
	# the node as root.
	edges = set()       # set of graph edges, each is tuple(source, dest, key)
	atmaxdepth = set()  # set of nodes that touch max recursion depth
	node2children = defaultdict(dict)  # a "cache" for nodes' children
	joindeltas = {}     # max difference in depth when arriving at node from different paths
	dones = set()       # nodes we are done with
	levels = {}         # {node: recursionlevel}.  Level will be updated in second recursion.
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
				joindeltas[current] = max(joindeltas.get(current, 0), level - levels[current])
			continue
		levels[current] = level
		if level >= maxdepth:
			# add to set of maxdepth nodes, and don't recurse further
			atmaxdepth.add(current)
		else:
			if current not in node2children:
				# populate "cache".  Used by second recursion too!
				node2children[current] = depsfun(current)
			for key, children in node2children[current].items():
				for child in children:
					stack.append((child, level + 1))
					edges.add((current, child, key))
		dones.add(current)
	# Phase 2, recurse again and fix level differences
	levels = {}
	stack = [(inputitem, 0), ]
	while stack:
		current, level = stack.pop()
		level = max(level, levels.get(current, 0))  # always use the max depth to get here
		level += joindeltas.pop(current, 0)
		levels[current] = level
		if current in atmaxdepth:
			continue
		for children in node2children[current].values():
			for child in children:
				stack.append((child, level + 1))
	nodes = defaultdict(list)
	for n, lev in levels.items():
		nodes[lev].append(n)
	return nodes, edges, atmaxdepth


def joblist_graph(urdentry):
	job2urddep = {Job(x[1]): str(dep) + '/' + str(item.timestamp) for dep, item in urdentry.deps.items() for x in item.joblist}
	jlist = urdentry.joblist
	jobsinurdlist = tuple(Job(item[1]) for item in jlist)
	nodes, edges, atmaxdepth = recurse_joblist(jobsinurdlist)
	names = {jobid: name for name, jobid in jlist}
	return creategraph(nodes, edges, atmaxdepth, names, jobsinurdlist, job2urddep)


def job_graph(inputjob, recursiondepth=MAXDEPTH):
	nodes, edges, atmaxdepth = recurse_jobsords(inputjob, jobdeps, recursiondepth)
	return creategraph(nodes, edges, atmaxdepth)


def dataset_graph(ds, recursiondepth=MAXDEPTH):
	nodes, edges, atmaxdepth = recurse_jobsords(ds, dsdeps, recursiondepth)
	return creategraph(nodes, edges, atmaxdepth)


def creategraph(nodes, edges, atmaxdepth, jobnames={}, jobsinurdlist=set(), job2urddep={}):
	# create unique string node ids
	nodeids = {n: 'node' + str(ix) for ix, n in enumerate(sorted(set.union(*(set(nn) for nn in nodes.values()))))}
	class Ordering:
		"""The init function takes the first level of nodes as input.
		The update function takes each consecutive level of nodes as
		input.  It returns two lists, the first contains the nodes in
		sorted order, and the second is a positive integer offset
		(starting at zero) indicating in which order the nodes should
		be drawn.
		"""
		def __init__(self, nodes):
			self.order = {x: str(ix) for ix, x in enumerate(sorted(nodes))}
		def update(self, nodes):
			nodes = sorted(nodes, key=lambda x: self.order[x])
			orders = tuple(int(self.order[n]) for n in nodes)
			for n in nodes:
				if 1:
					for ix, c in enumerate(sorted(children[n])):
						if c not in self.order:
							self.order[c] = self.order[n] + str(ix)
				if 0:
					ix = 0
					for (key, childs) in (sorted(jobdeps(n).items())):  # sort in depname order
						for child in childs:
							if child not in self.order:
								self.order[child] = self.order[n] + str(ix)
								ix += 1
				self.order.pop(n)
			for ix, (key, val) in enumerate(sorted(self.order.items(), key=lambda x: x[1])):
				self.order[key] = str(ix)
			return nodes, orders
	outnodes = {}
	order = Ordering(nodes[0])
	children = defaultdict(set)
	for s, d, _ in edges:
		children[s].add(d)
	for level, jobsatlevel in sorted(nodes.items()):
		jobsatlevel, offset = order.update(jobsatlevel)
		for ix, (j, ofs) in enumerate(zip(jobsatlevel, offset)):
			x = - 160 * (level + 0.2 * sin(ix + ofs))
			y = 140 * ofs + 50 * sin(level / 3)
			# remains to create a node with attributes
			jj = j if isinstance(j, Job) else j.job
			nodeix = nodeids[j]
			outnodes[nodeix] = DotDict(
				nodeid=nodeids[j],
				jobid=str(jj), x=x, y=y,
				atmaxdepth=j in atmaxdepth,
				timestamp=datetime.fromtimestamp(jj.params.starttime).strftime("%Y-%m-%d %H:%M:%S"),
				method=jj.method,
				neighbour_nodes=set(),
				neighbour_edges=set(),
			)
			if isinstance(j, Job):
				notinjoblist = False
				if jobsinurdlist and j not in jobsinurdlist:  # i.e. job is not in this urdlist
					if job2urddep and j in job2urddep:
						notinjoblist = job2urddep[j]  # but in a dependency urdlist
					else:
						notinjoblist = True
				outnodes[nodeix].update(dict(
					files=sorted(j.files()),
					datasets=j.datasets,
					subjobs=tuple((x, Job(x).method) for x in j.post.subjobs),
					name=jobnames.get(j) if jobnames else None,
					notinurdlist=notinjoblist,
				))
			else:
				# j is Dataset
				outnodes[nodeix].update(dict(
					ds=str(j),
					columns=tuple((key, val.type) for key, val in j.columns.items()),
					lines="%d x % s" % (len(j.columns), '{:,}'.format(sum(j.lines)).replace(',', ' ')),
				))

	# create set of edges and find all node's neighbours
	outedges = set()
	for s, d, rel in edges:
		s, d = nodeids[s], nodeids[d]
		edgekey = ''.join((s, d))
		outnodes[s].neighbour_nodes.add(d)
		outnodes[d].neighbour_nodes.add(s)
		outnodes[s].neighbour_edges.add(edgekey)
		outnodes[d].neighbour_edges.add(edgekey)
		outedges.add((s, d, rel))

	# limit angles
	seen = set()
	MAXANGLE = 60 * pi / 180
	offset = {}
	for level, jobsatlevel in sorted(nodes.items(), reverse=True):
		for n in jobsatlevel:
			n = outnodes[nodeids[n]]
		xoffset = 0
		maxangle = MAXANGLE
		for n in (outnodes[nodeids[x]] for x in jobsatlevel):
			for m in sorted((outnodes[x] for x in n.neighbour_nodes), key=lambda x: x.jobid):
				if m.jobid in seen:
					continue
				dx = abs(n.x - m.x)
				dy = abs(n.y - m.y)
				angle = abs(atan(dy / dx))
				if angle > maxangle:
					maxangle = angle
					xoffs = dy / tan(MAXANGLE)
					xoffset = max(xoffset, xoffs - dx)
			seen.add(n.jobid)
		offset[level] = xoffset
	totoffs = 0
	for level, offs in sorted(offset.items(), reverse=True):
		if level > 0:
			totoffs += offs
			for n in nodes[level-1]:
				n = outnodes[nodeids[n]]
				n.x += totoffs

	return dict(
		nodes=outnodes,
		edges=list(outedges),
	)
