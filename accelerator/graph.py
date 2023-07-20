from math import sin
from collections import defaultdict
from datetime import datetime
from accelerator import JobWithFile, Job
from accelerator import DotDict

MAXDEPTH = 1000


def jobdeps(job):
	""" Return all the job's dependencies """
	res = defaultdict(set)
	# jobs
	for key, value in job.params.jobs.items():
		if not isinstance(value, (list, tuple)):
			value = [value, ]
		for val in value:
			if val:
				res['jobs.' + key].add(val)
	# options Jobwithfile
	for key, value in job.params.options.items():
		if isinstance(value, JobWithFile):
			res['jwf.' + key] = value.job
		# @@ handle or sorts of nested options here
	# datasets
	for key, value in job.params.datasets.items():
		if not isinstance(value, (list, tuple)):
			value = [value, ]
		for val in value:
			if val:
				res['datasets.' + key].add(val.job)
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
		deps = set.union(*jobdeps(item).values())
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
	node2children = defaultdict(dict)  # a "cache" for nodes' children
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
				node2children[current] = jobdeps(current)
			for key, children in node2children[current].items():
				for child in children:
					stack.append((child, level + 1))
					edges.add((current, child, key))
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
		for children in node2children[current].values():
			for child in children:
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
	job2urddep = {Job(x[1]): str(k) + '/' + str(item.timestamp) for k, item in urdentry.deps.items() for x in item.joblist}
	jlist = urdentry.joblist
	jobsinurdlist = tuple(Job(item[1]) for item in reversed(jlist))
	nodes, edges, atmaxdepth = recurse_joblist(jobsinurdlist)
	names = {}
	for name, jobid in jlist:
		names[jobid] = name
	return creategraph(nodes, edges, atmaxdepth, names, jobsinurdlist, job2urddep)


def job(inputjob, recursiondepth=100):
	nodes, edges, atmaxdepth = recurse_jobs(inputjob, recursiondepth)
	return creategraph(nodes, edges, atmaxdepth)


def ds(ds, recursiondepth=100):
	nodes, edges, atmaxdepth = recurse_ds(ds, recursiondepth)
	return creategraph(nodes, edges, atmaxdepth)


def creategraph(nodes, edges, atmaxdepth, jobnames={}, jobsinurdlist=set(), job2urddep={}):
	def nodes_with_attributes(nodes, edges, atmaxdepth, jobnames, validjobset, job2urddep):
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
		outnodes = {}
		bbox = [None, None, None, None]
		order = Ordering(nodes[0])
		children = defaultdict(set)
		for s, d, _ in edges:
			children[s].add(d)
		for level, jobsatlevel in sorted(nodes.items()):
			jobsatlevel, offset = order.update(jobsatlevel)
			for ix, (j, ofs) in enumerate(zip(jobsatlevel, offset)):
				x = 160 * (level + 0.3 * sin(ix))
				y = 140 * ofs + 70 * sin(level / 3)
				# update bounding box
				for i, (fun, var) in enumerate(((min, x), (min, y), (max, x), (max, y))):
					bbox[i] = fun(bbox[i] if not bbox[i] is None else var, var)
				# remains to create a node with attributes
				jj = j if isinstance(j, Job) else j.job
				nodeix = nodeids[j]
				outnodes[nodeix] = DotDict(
					nodeid=nodeids[j],
					jobid=str(j), x=x, y=y,
					atmaxdepth=j in atmaxdepth,
					timestamp=datetime.fromtimestamp(jj.params.starttime).strftime("%Y-%m-%d %H:%M:%S"),
					method=jj.method,
				)
				if isinstance(j, Job):
					notinjoblist = False
					if validjobset and j not in validjobset:  # i.e. job is not in this urdlist
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
		return outnodes, bbox
	def create_edges(edges):
		neighbour_nodes = defaultdict(set)
		neighbour_edges = defaultdict(set)
		outedges = set()
		for s, d, rel in edges:
			s = nodeids[s]
			d = nodeids[d]
			edgekey = ''.join((s, d))
			neighbour_nodes[s].add(d)
			neighbour_nodes[d].add(s)
			neighbour_edges[s].add(edgekey)
			neighbour_edges[d].add(edgekey)
			outedges.add((s, d, rel))
		return outedges, neighbour_nodes, neighbour_edges

	# create unique string node ids
	nodeids = {n: 'node' + str(ix) for ix, n in enumerate(sorted(set.union(*(set(nn) for nn in nodes.values()))))}
	# create nodes (with geometrical locations) and a bounding box
	outnodes, bbox = nodes_with_attributes(nodes, edges, atmaxdepth, jobnames, jobsinurdlist, job2urddep)
	outedges, neighbour_nodes, neighbour_edges = create_edges(edges)
	# do some adjustments to the bounding box
	x1, y1, x2, y2 = bbox
	dy = max(100, y2 - y1)
	dx = max(100, x2 - x1)
	bbox = [x1 - 50, y1 - 50, dx + 100, dy + 100]
	return dict(
		nodes=outnodes,
		edges=outedges,
		bbox=bbox,
		neighbour_nodes=neighbour_nodes,
		neighbour_edges=neighbour_edges
	)
