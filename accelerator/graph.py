from math import sin, cos, atan2, pi
from collections import defaultdict
from datetime import datetime
from html import escape
from json import dumps
from accelerator import JobWithFile, Job
from accelerator import DotDict
MAXDEPTH = 100
from accelerator.compat import url_quote
MAXDEPTH = 10


def escdump(x):
	return(escape(dumps(x), quote=True))


def expandtolist(what, fun=lambda x: x):
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
			res['jobs.' + key].update(expandtolist(value))
	for key, value in job.params.datasets.items():
		if value:
			res['datasets.' + key].update(expandtolist(value, lambda x: x.job))
	# options Jobwithfile
	for key, value in job.params.options.items():
		if isinstance(value, JobWithFile):
			res['jwf.' + key].add(value.job)
		# @@ handle or sorts of nested options here
	return res


def dsdeps(ds):
	""" return all the dataset's parents and previous """
	res = defaultdict(set)
	if ds:
		if ds.parent:
			res['parent'].update(expandtolist(ds.parent))
		if ds.previous:
			res['previous'].add(ds.previous)
	return res


def recurse_joblist(inputjoblist):
	print("Test that out-of-urdlist items render properly (both in-other-urdlist and in-no-urdlist).")
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


def job(inputjob, recursiondepth=100):
	nodes, edges, atmaxdepth = recurse_jobsords(inputjob, jobdeps, recursiondepth)
	return creategraph(nodes, edges, atmaxdepth)


def dataset(ds, recursiondepth=100):
	nodes, edges, atmaxdepth = recurse_jobsords(ds, dsdeps, recursiondepth)
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
		bbox = [None, None, None, None]
		order = Ordering(nodes[0])
		children = defaultdict(set)
		for s, d, _ in edges:
			children[s].add(d)
		for level, jobsatlevel in sorted(nodes.items()):
			jobsatlevel, offset = order.update(jobsatlevel)
			for ix, (j, ofs) in enumerate(zip(jobsatlevel, offset)):
				x = 160 * (level + 0.2 * sin(ix + ofs))
				y = 140 * ofs + 50 * sin(level / 3)
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


circletemplate = """	<circle
		id="{id}"
		class="hovernode"
		cx="{cx}"
		cy="{cy}"
		r="{r}"
		stroke="black"
		stroke_width="2"
		fill="var(--{color})"
		fill-opacity="50%"
		data-origfill="var(--{color})"
		data-neighbour_nodes="{neighbour_nodes}"
		data-neighbour_edges="{neighbour_edges}"
		onclick="popupmenu({popuparglist})"
		onmouseover="highlight_nodes(this, true)"
		onmouseout="highlight_nodes(this, false)"
	/>
"""


texttemplate = """	<text x="{x}", y="{y}" font-weight="{weight}" font-size="12" text-anchor="middle" fill="black">
		<a href={href}>{text}</a>
	</text>
"""


centertemplate = """	<text x="{x}" y="{y}" fill="blue4" text-anchor="middle" font-weight="bold">
		{text}
	</text>
"""


def svg_joblist(urdentry, arrowlen=15, arrowangle=pi / 8):
	graph = joblist_graph(urdentry)
	res = """<svg id="svg" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="{bbox}" width="100%" height="400px">\n""".format(bbox=' '.join(map(str, graph['bbox'])))
	for name, item in graph['nodes'].items():
		item.size = 20 if item.notinurdlist else 30
		if item.atmaxdepth:
			color = 'node-atmaxdepth'
		elif item.notinurdlist is True:
			color = 'node-nourdlist'
		elif isinstance(item.notinurdlist, str):
			color = 'node-inanotherurdlist'
		else:
			color = 'node-job-default'
		if item.name is None or item.name == item.method:
			name = item.method
		else:
			name = '%s (%s)' % (item.method, item.name)
		res += centertemplate.format(
			x=item.x,
			y=item.y + 5,
			text=''.join(('D' if item.datasets else '', 'F' if item.files else '', 'S' if item.subjobs else '')),
		)
		res += circletemplate.format(
			id=item.nodeid,
			cx=item.x,
			cy=item.y,
			r=item.size,
			color=color,
			neighbour_edges=escdump(list(graph['neighbour_edges'][item.nodeid])),
			neighbour_nodes=escdump(list(graph['neighbour_nodes'][item.nodeid])),
			popuparglist="event, " + ', '.join(
				map(lambda x: escdump(x), [
					item.jobid,
					item.files,
					item.datasets,
					item.subjobs,
					item.method,
					item.atmaxdepth,
					item.timestamp,
					item.notinurdlist,
				])
			)
		)
		res += texttemplate.format(
			x=item.x,
			y=item.y + item.size + 15,
			weight='bold',
			href='/job/' + url_quote(item.jobid),
			text=item.jobid,
		)
		res += texttemplate.format(
			x=item.x,
			y=item.y + item.size + 30,
			weight='normal',
			href='/job/' + url_quote(item.jobid) + '/method.tar.gz' + '/',
			text=name,
		)
	for fromid, toid, relation in graph['edges']:
		key = ''.join((fromid, toid))
		res += """	<g id={key}>\n""".format(key=url_quote(key))
		fromnode = graph['nodes'][fromid]
		tonode = graph['nodes'][toid]
		fx, fy = fromnode.x, fromnode.y
		tx, ty = tonode.x, tonode.y
		a = atan2(ty - fy, tx - fx)
		fx = fx + fromnode.size * cos(a)
		fy = fy + fromnode.size * sin(a)
		tx = tx - tonode.size * cos(a)
		ty = ty - tonode.size * sin(a)
		res += """		<line x1="{x1}" x2="{x2}" y1="{y1}" y2="{y2}" stroke="black" stroke_width="2"/>\n""".format(
			x1=fx,
			x2=tx,
			y1=fy,
			y2=ty,
		)
		x1 = tx - arrowlen * cos(a + arrowangle)
		y1 = ty - arrowlen * sin(a + arrowangle)
		x2 = tx - arrowlen * cos(a - arrowangle)
		y2 = ty - arrowlen * sin(a - arrowangle)
		res += """		<polygon points="{x0},{y0} {x1},{y1} {x2},{y2}"/> stroke="black"/>\n""".format(
			x0=tx, y0=ty,
			x1=x1, y1=y1,
			x2=x2, y2=y2,
		)
		mx = fx + 8 * cos(a) + 6 * sin(a)
		my = fy + 8 * sin(a) - 6 * cos(a)
		res += """		<text x={x} y={y} transform="rotate({angle},{x},{y})" text-anchor="start" font-size="9" fill="#4040a0">\n			{text}\n		</text1>\n""".format(
			x=mx, y=my,
			angle=a * 180 / pi,
			text=relation,
		)
		res += """	</g>\n"""
	res += "</svg>"
	print(res)
	return res
