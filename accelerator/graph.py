from math import sin, pi, tan, atan
from collections import defaultdict
from datetime import datetime
from accelerator import JobWithFile, Job
from accelerator.dataset import Dataset

MAXDEPTH = 20


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


class Graffe:
	class WrapperNode:
		def __init__(self, payload):
			self.nodeid = str(payload)
			self.payload = payload
			self.level = 0
			self.atmaxdepth = False
			self.notinurdlist = False
			self.children = []
			self.depdict = {}
			self.done = False
			self.num_entries = 0

	def __init__(self):
		self.count = 0
		self.nodes = {}
		self.edges = set()

	def getorcreatenode(self, name, num_entries=0):
		""" get existing from name or create a new WrapperNode """
		assert isinstance(name, str)
		if name in self.nodes:
			return self.nodes[name]
		else:
			n = self.WrapperNode(name)
			n.num_entries = num_entries
			self.nodes[name] = n
			self.safename = 'node' + str(self.count)
			self.count += 1
			return n

	def createedge(self, current, child, relation):
		""" create a new edge (from WrapperNode to WrapperNode """
		assert isinstance(current, self.WrapperNode)
		assert isinstance(child, self.WrapperNode)
		self.edges.add((current, child, relation))

	def level2nodes(self):
		""" return {level: set_of_WrapperNodes_at_level} """
		ret = defaultdict(set)
		for n in self.nodes.values():
			ret[n.level].add(n)
		return ret

	def clear_done(self):
		""" set done to False in all WrapperNodes """
		for n in self.nodes.values():
			n.done = False

	def populatenodefrompayload(self):
		for n in self.nodes.values():
			njob = n.payload if isinstance(n.payload, Job) else n.payload.job
			n.jobid = str(njob)
			n.method = njob.method
			n.name = n.method  # @@@
			n.timestamp = datetime.fromtimestamp(njob.params.starttime).strftime("%Y-%m-%d %H:%M:%S")
			if isinstance(n.payload, Job):
				n.files = sorted(n.payload.files())
				n.datasets = sorted(n.payload.datasets)
				n.subjobs= tuple((x, Job(x).method) for x in n.payload.post.subjobs)
			else:
				n.columns=tuple((key, val.type) for key, val in n.payload.columns.items()),
				n.lines="%d x % s" % (len(n.payload.columns), '{:,}'.format(sum(n.payload.lines)).replace(',', ' ')),
			n.neighbour_nodes = set()
			n.neighbour_edges = set()

	def populatewithneighbours(self):
		for s, d, rel in self.edges:
			edgekey = ''.join([s.nodeid, d.nodeid])
			s.neighbour_nodes.add(d)
			d.neighbour_nodes.add(s)
			s.neighbour_edges.add(edgekey)
			d.neighbour_edges.add(edgekey)
		for n in self.nodes.values():
			n.neighbour_nodes = tuple(n.neighbour_nodes)
			n.neighbour_edges = tuple(n.neighbour_edges)

	def cleankeepers(self, keepers):
		""" keep only those nodes (and edges relating to) nodes in keepers set """
		self.nodes = {key: val for key, val in self.nodes.items() if val in keepers}
		self.edges = set(x for x in self.edges if x[0] in keepers and x[1] in keepers)

	def serialise(self):
		for n in self.nodes.values():
			n.neighbour_nodes = tuple(x.nodeid for x in n.neighbour_nodes)
		self.edges = tuple((x[0].nodeid, x[1].nodeid, x[2]) for x in self.edges)



	
def recurse_jobsords(inputitem, depsfun, maxdepth=MAXDEPTH):
	# Phase 1: depth first to find all nodes with multiple entries.
	# Flagging of atmaxdepth is pessimistic in depth first.
	graffe = Graffe()

	inputitem = graffe.getorcreatenode(inputitem, num_entries=1)
	stack = [inputitem, ]
	while stack:
		current = stack.pop()
		if current.done:
			continue
		if current.level >= maxdepth:
			current.atmaxdepth = True
			continue
		current.depdict = depsfun(current.payload)
		childset = set()
		for relation, children in current.depdict.items():
			for child in children:
				child = graffe.getorcreatenode(child)
				graffe.createedge(current, child, relation)
				childset.add(child)
		current.children = tuple(sorted(childset, key=lambda x: x.nodeid))
		for child in current.children:
			child.level = max(child.level, current.level + 1)
			child.num_entries += 1
			stack.append(child)
		current.done = True


	# Phase 2: breadth first, find levels and atmaxdepth

	graffe.clear_done()

	keepers = set()
	stack = [inputitem, ]
	while stack:
		current = stack.pop()
		current.num_entries -= 1
		keepers.add(current)
		if current.done or current.atmaxdepth:
			continue
		if current.level >= maxdepth:
			current.atmaxdepth = True
			current.done = True
			continue
		if current.num_entries == 0:
			for child in current.children:
				child.level = current.level + 1
				stack.append(child)
		current.done = True

	graffe.cleankeepers(keepers)
	graffe.populatenodefrompayload()
	graffe.populatewithneighbours()
	return graffe


def joblist_graph(urdentry):
	job2urddep = {Job(x[1]): str(dep) + '/' + str(item.timestamp) for dep, item in urdentry.deps.items() for x in item.joblist}
	jlist = urdentry.joblist
	jobsinurdlist = tuple(Job(item[1]) for item in jlist)
	nodes, edges, atmaxdepth = recurse_joblist(jobsinurdlist)
	names = {jobid: name for name, jobid in jlist}
	return placement(graffe, atmaxdepth, names, jobsinurdlist, job2urddep)


def job_graph(inputjob, recursiondepth=MAXDEPTH):
	graffe = recurse_jobsords(inputjob, jobdeps, recursiondepth)
	return placement(graffe)


def dataset_graph(ds, recursiondepth=MAXDEPTH):
	nodes, edges = recurse_jobsords(ds, dsdeps, recursiondepth)
	return placement(nodes, edges)


def placement(graffe, jobnames={}, jobsinurdlist=set(), job2urddep={}):

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
			for n in nodes:
				for ix, c in enumerate(sorted(n.children, key=lambda x: x.nodeid)):
					if c not in self.order:
						self.order[c] = self.order[n] + str(ix)
				self.order.pop(n)
			for ix, (key, val) in enumerate(sorted(self.order.items(), key=lambda x: x[1])):
				self.order[key] = str(ix)
			return nodes

	# determine x and y coordinates
	level2nodes = graffe.level2nodes()
	order = Ordering(level2nodes[0])
	for level, nodesatlevel in sorted(level2nodes.items()):
		nodesatlevel = order.update(nodesatlevel)
		for ix, n in enumerate(nodesatlevel):
			n.x = - 160 * (level + 0.2 * sin(ix))
			n.y = 140 * ix + 50 * sin(level / 3)

	# limit angles by adjusting x positions
	MAXANGLE = 45 * pi / 180
	offset = {}
	for level, nodesatlevel in sorted(level2nodes.items()):
		maxangle = MAXANGLE
		xoffs = 0
		for n in nodesatlevel:
			for m in n.children:
				dx = abs(n.x - m.x)
				dy = abs(n.y - m.y)
				angle = abs(atan(dy / dx))
				if angle > maxangle:
					maxangle = angle
					xoffs = max(dy / tan(MAXANGLE), xoffs - dx)
		offset[level + 1] = xoffs
	totoffs = 0
	for level, offs in sorted(offset.items()):
		totoffs += offs
		for n in level2nodes[level]:
			n.x -= totoffs

	graffe.serialise()

	return dict(
		nodes=graffe.nodes,
		edges=graffe.edges,
	)



			# # remains to create a node with attributes
			# # outnodes[nodeix] = DotDict(
			# # 	nodeid=nodeids[n],
			# # 	jobid=str(nn), x=x, y=y,
			# # 	atmaxdepth=n in atmaxdepth,
			# # 	timestamp=datetime.fromtimestamp(nn.params.starttime).strftime("%Y-%m-%d %H:%M:%S"),
			# # 	method=nn.method,
			# # 	neighbour_nodes=set(),
			# # 	neighbour_edges=set(),
			# # )
			# if isinstance(n, Job):
		# 	notinjoblist = False
			# 	if jobsinurdlist and n not in jobsinurdlist:  # i.e. job is not in this urdlist
			# 		if job2urddep and n in job2urddep:
			# 			notinjoblist = job2urddep[n]  # but in a dependency urdlist
			# 		else:
			# 			notinjoblist = True
			# 	outnodes[nodeix].update(dict(
			# 		files=sorted(n.files()),
			# 		datasets=n.datasets,
			# 		subjobs=tuple((x, Job(x).method) for x in n.post.subjobs),
			# 		name=jobnames.get(n) if jobnames else None,
			# 		notinurdlist=notinjoblist,
			# 	))
			# else:
			# 	# n is Dataset
			# 	outnodes[nodeix].update(dict(
			# 		ds=str(n),
			# 		columns=tuple((key, val.type) for key, val in n.columns.items()),
			# 		lines="%d x % s" % (len(n.columns), '{:,}'.format(sum(n.lines)).replace(',', ' ')),
			# 	))

	# # create set of edges and find all node's neighbours
	# outedges = set()
	# for s, d, rel in graffe.edges:
	# 	edgekey = ''.join((s.simple, d.simple))
	# 	s.neighbour_nodes.add(d.simple)
	# 	d.neighbour_nodes.add(s.simple)
	# 	s.neighbour_edges.add(edgekey)
	# 	d.neighbour_edges.add(edgekey)
	# 	outedges.add((s, d, rel))
