from math import sin, pi, tan, atan
from collections import defaultdict
from datetime import datetime
from accelerator import JobWithFile, Job, DotDict
MAXDEPTH = 200


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
			self.num_incoming = 0

	def __init__(self):
		self.count = 0
		self.nodes = {}
		self.edges = set()

	def getorcreatenode(self, item):
		""" get existing from item or create a new WrapperNode """
		if str(item) in self.nodes:
			return self.nodes[item]
		else:
			n = self.WrapperNode(item)
			n.safename = 'node' + str(self.count)
			self.nodes[str(item)] = n
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

	def reset_done(self):
		""" set done to False in all WrapperNodes """
		for n in self.nodes.values():
			n.done = False

	def populate_with_neighbours(self):
		""" add neighbour information to all WrapperNodes """
		for n in self.nodes.values():
			n.neighbour_nodes = set()
			n.neighbour_edges = set()
		for s, d, rel in self.edges:
			edgekey = ''.join([s.safename, d.safename])
			s.neighbour_nodes.add(d)
			d.neighbour_nodes.add(s)
			s.neighbour_edges.add(edgekey)
			d.neighbour_edges.add(edgekey)

	def prune(self, keepers):
		""" keep only those nodes (and edges relating to) nodes in keepers set """
		self.nodes = {key: val for key, val in self.nodes.items() if val in keepers}
		self.edges = set(x for x in self.edges if x[0] in keepers and x[1] in keepers)

	def serialise(self):
		""" collapse neighbour_nodes and edges to strings, for later JSON output """
		for n in self.nodes.values():
			n.neighbour_nodes = tuple(x.safename for x in n.neighbour_nodes)
		self.edges = tuple((x[0].safename, x[1].safename, x[2]) for x in self.edges)
		self.nodes = {item.safename: item for item in self.nodes.values()}

	def depth_first(self, stack, depsfun, maxdepth):
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
					child = self.getorcreatenode(child)
					self.createedge(current, child, relation)
					childset.add(child)
			current.children = tuple(sorted(childset, key=lambda x: x.nodeid))
			for child in current.children:
				child.level = max(child.level, current.level + 1)
				child.num_incoming += 1
				stack.append(child)
			current.done = True

	def breadth_first(self, stack, maxdepth):
		""" also prune all nodes that are not visited because they are outside of MAXDEPTH """
		keepers = set()
		while stack:
			current = stack.pop()
			current.num_incoming -= 1
			keepers.add(current)
			if current.done or current.atmaxdepth:
				continue
			if current.level >= maxdepth:
				assert current.level == maxdepth
				current.atmaxdepth = True
				current.children = set()  # remove children from edge-node
				current.done = True
				continue
			if current.num_incoming == 0:
				for child in current.children:
					child.level = max(child.level, current.level + 1)
					stack.append(child)
				current.done = True
		self.prune(keepers)


def create_graph(inputitem, urdinfo=(), maxdepth=MAXDEPTH):
	graffe = Graffe()
	if isinstance(inputitem, tuple):
		# is joblist, create and populate WrapperNodes from input
		inputitem = tuple(graffe.getorcreatenode(x) for x in inputitem)
		for n in inputitem:
			childset = set()
			depdict = jobdeps(n.payload)
			for relation, children in depdict.items():
				for c in children:
					c = graffe.getorcreatenode(c)
					graffe.createedge(n, c, relation)
					c.num_incoming += 1
					childset.add(c)
			n.children = tuple(sorted(childset, key=lambda x: x.nodeid))
		stack = [n for n in inputitem if n.num_incoming == 0]
		for n in stack:
			n.num_incoming = 1
	else:
		# is job or dataset, need to do depth-first to find num_incoming for all WrapperNodes
		depsfun = jobdeps if isinstance(inputitem, Job) else dsdeps
		inputitem = graffe.getorcreatenode(inputitem)
		inputitem.num_incoming = 1
		stack = [inputitem, ]
		graffe.depth_first(stack, depsfun, maxdepth)
		graffe.reset_done()
		stack = [inputitem, ]
	graffe.breadth_first(stack, maxdepth)
	# add parameters from payload (job/ds) to all WrapperNodes
	for n in graffe.nodes.values():
		njob = n.payload if isinstance(n.payload, Job) else n.payload.job
		n.jobid = str(njob)
		n.method = njob.method
		n.timestamp = datetime.fromtimestamp(njob.params.starttime).strftime("%Y-%m-%d %H:%M:%S")
		n.name = n.method
		if isinstance(n.payload, Job):
			n.files = sorted(n.payload.files())
			n.datasets = sorted(n.payload.datasets)
			n.subjobs = tuple((x, Job(x).method) for x in n.payload.post.subjobs)
			if urdinfo:
				jobsinurdlist, job2urddep, names = urdinfo
				if jobsinurdlist and n.nodeid not in jobsinurdlist:
					if job2urddep and n.nodeid in job2urddep:
						n.notinurdlist = job2urddep[n.nodeid]
					else:
						n.notinurdlist = True
				n.name = names.get(n.nodeid, None)
		else:
			# dataset
			n.columns = tuple((key, val.type) for key, val in n.payload.columns.items()),
			n.lines = "%d x % s" % (len(n.payload.columns), '{:,}'.format(sum(n.payload.lines)).replace(',', ' ')),
			n.ds = str(n.payload)
	graffe.populate_with_neighbours()
	return graffe


def placement(graffe):
	class Ordering:
		"""The init function takes the first level of nodes as input.
		The update function takes each consecutive level of nodes as
		input.  It returns a list of the nodes in order.
		"""
		def __init__(self, nodes):
			self.order = {x: str(ix) for ix, x in enumerate(sorted(nodes, key=lambda x: x.nodeid))}
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


def do_graph(inp, gtype, recursiondepth=MAXDEPTH):
	if gtype == 'urdlist':
		# is joblist
		job2urddep = {x[1]: "%s/%s" % (dep, item.timestamp) for dep, item in inp.deps.items() for x in item.joblist}
		jlist = inp.joblist
		inp = tuple(Job(item[1]) for item in jlist)
		jobsinurdlist = tuple(str(x) for x in inp)
		names = {jobid: name for name, jobid in jlist}
		graffe = create_graph(inp, urdinfo=(jobsinurdlist, job2urddep, names), maxdepth=recursiondepth)
	else:
		graffe = create_graph(inp, maxdepth=recursiondepth)
	ret = placement(graffe)
	ret['type'] = 'job' if gtype in ('urdlist', 'job') else 'ds'
	return ret
