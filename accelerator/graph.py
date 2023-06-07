from datetime import datetime
from math import sin
from collections import defaultdict
from accelerator import JobWithFile, Job
from accelerator.svg import SVG

MAXDEPTH = 1000



def alljobdeps(job):
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


def recurse_ds(inputitem, maxdepth=MAXDEPTH):
	edges = set()
	atmaxdepth = set()
	mergeoffsets = dict()
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
			if current.parent:
				if isinstance(current.parent, list):
					parent = current.parent
				else:
					parent = [current.parent,]
				for child in parent:
					stack.append((child, level + 1))
					edges.add((current, child))
			if current.previous:
				stack.append((current.previous, level + 1))
				edges.add((current, current.previous))
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


def jlist(urdentry, recursiondepth=1000):
	g = graph()
	job2urddep = {Job(x[1]): str(k) + '/' + str(item.timestamp) for k, item in urdentry.deps.items() for x in item.joblist}
	jlist = urdentry.joblist
	jobsinurdlist = tuple(Job(item[1]) for item in reversed(jlist))
	job2name = {job: name for name, job in jlist}
	nodes, edges, atmaxdepth = recurse_joblist(jobsinurdlist, recursiondepth)
	assert min(nodes) == 0, ('minimum level must be zero!', nodes.keys())
	def labelfun(j):
		label = '\n'.join((j, j.method))
		if job2name.get(j) and j.method != job2name[j]:
			label = "[%s]" % (job2name[j],) + '\n' + label
		label += '\n' + ('D' if j.datasets else '') + ('F' if j.files() else '') + ('S' if j.post.subjobs else '')
		return label
	xoffset = 0
	for graphnumber in nodes:
		g.insert_nodes(nodes[graphnumber], labelfun, xoffset, atmaxdepth, jobsinurdlist, job2urddep)
		xoffset += max(nodes[graphnumber]) - min(nodes[graphnumber]) + 1
	g.insert_edges(edges)
	return g.write()


def job(inputjob, recursiondepth=10):
	g = graph()
	nodes, edges, atmaxdepth = recurse_jobs(inputjob, recursiondepth)
	def labelfun(j):
		label = '\n'.join((j, j.method))
		label += '\n' + ('D' if j.datasets else '') + ('F' if j.files() else '') + ('S' if j.post.subjobs else '')
		return label
	g.insert_nodes(nodes[0], labelfun, 0, atmaxdepth)
	g.insert_edges(edges)
	return g.write()


def ds(ds, recursiondepth=10):
	g = graph()
	nodes, edges, atmaxdepth = recurse_ds(ds, recursiondepth)
	g.insert_nodes(nodes[0], lambda ds: ("%s\n%s\n%dx{:,d}" % (ds, ds.job.method, len(ds.columns))).format(sum(ds.lines)).replace(',', '.'), 0, atmaxdepth, jobnotds=False)
	g.insert_edges(edges)
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
		shape = 'dot' if jobnotds else 'square'
		for level, jobsatlevel in sorted(nodes.items()):
			adjlev = level - min(nodes)
			for ix, j in enumerate(jobsatlevel):
				label = labelfun(j)
				color = "#4466aa"
				size = 30
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
					if j in atmaxdepth:
						color = '#cc5522'
					if validjobset and j not in validjobset:  # i.e. job is not in this urdlist
						size = 20
						if job2urddep and j in job2urddep:
							color = "#cccccc"
							title += '<br><font color="#9900FF"><b>Job in dependency urdlist:</b><br>&nbsp&nbsp<a href=../urd/{item} target = "_parent">{item}</a></font>'.format(item=job2urddep[j])
						else:
							color = "#cc0000"
							title += '<br><font color="#ff5555"><b>Job not in this urdlist or any of its dependencies.</b></font>'
					if j.method == 'csvimport':
						title += '<br><b>options.filename:</b> <i> %s </i><br>' % (j.params.options.filename,)
					presentstuff(sorted(j.files()), 'Files')
					presentstuff(sorted(j.datasets), 'Datasets')
					presentstuff(sorted(j.post.subjobs), 'Subjobs')
				else:
					# This is a Dataset
					title = '<b>Dataset </b><a href=../dataset/{job} target="_parent">{job}</a>'.format(job=j)
					title += '<br>' + datetime.fromtimestamp(j.job.params.starttime).strftime("%Y-%m-%d %H:%M:%S")
					if j in atmaxdepth:
						color = "#cc5522"
						title += '<br><b><font color="#ff0099">Reached recursion limit - no dependencies drawn!</font></b>'
					title += '<br><br>'
					title += '<b>Job: </b><a href=../job/{job} target="_parent">{job}</a>'.format(job=j.job)
					title += '<br><br>'
					if isinstance(j.parent, list):
						pv = j.parent
					else:
						pv = [j.parent,]
					for p in pv:
						title += '<b>Parent: </b> <a href=../dataset/{ds} target="_parent">{ds}</a><br>'.format(ds=p)
					if j.previous:
						title += '<b>Previous: </b> <a href=../dataset/{ds} target="_parent">{ds}</a><br>'.format(ds=j.previous)
					title += '<br><b>Rows: </b> %s' % ('{:,d}'.format(sum(j.lines)).replace(',', '.'),)
					title += '<br>'
					presentstuff(sorted(j.columns.items()), 'Columns')
				x = (xoffset + adjlev + 0.3 * sin(ix)) * 160
				y = (ix - len(jobsatlevel) / 2) * 140 + sin(adjlev / 3) * 70
				# @@@@@@@@@@@ dataset.parent as a list is not tested at all!!!!!!!!!!!!!!!!!!!!!!!!
#				self.svg.jobnode(j, text=label, color=color, x=x, y=y, size=size)
				self.svg.jobnode2(j, x=x, y=y, size=size, color=color, atmaxdepth=j in atmaxdepth)
				for ix, (fun, var) in enumerate(((min, x), (max, x), (min, y), (max, y))):
					self.bbox[ix] = fun(self.bbox[ix] if not self.bbox[ix] is None else var, var)

	def insert_edges(self, edges):
		for s, d in edges:
#			self.svg.arrow(s, d)
			self.svg.arrow2(s, d)
	def write(self):
		x1, x2, y1, y2 = self.bbox
		dy = y2 - y1
		if dy < 300:
			y1 = y1 - (300 - dy) // 2
#		s = self.svg.getsvg((-100 + x1, y1, 200 + x2 - x1, 300))
		return self.svg.nodes, self.svg.edges, (-100 + x1, y1, 200 + x2 - x1, 300), self.svg.neighbour_nodes, self.svg.neighbour_edges
