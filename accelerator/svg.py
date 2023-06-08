from datetime import datetime
from collections import defaultdict
from math import atan2, pi, cos, sin
from accelerator import DotDict

class SVG:
	def __init__(self):
		self.s = ''
		self.nodedata = dict()
		self.nodes = dict()
		self.edges = dict()
		self.neighbour_nodes = defaultdict(set)
		self.neighbour_edges = defaultdict(set)

	def jobnode2(self, id, x, y, atmaxdepth=False, notinurdlist=True):
		self.nodedata[id] = (x, y)
		self.nodes[id] = DotDict(
			jobid=str(id),
			method=id.method,
			files=sorted(id.files()),
			datasets=id.datasets,
			subjobs=id.post.subjobs,
			x=x,
			y=y,
			atmaxdepth=atmaxdepth,
			notinurdlist=notinurdlist,
			timestamp=datetime.fromtimestamp(id.params.starttime).strftime("%Y-%m-%d %H:%M:%S"),
		)

	def arrow2(self, fromid, toid):
		edgekey = ''.join((fromid, toid))
		self.neighbour_nodes[fromid].add(toid)
		self.neighbour_nodes[toid].add(fromid)
		self.neighbour_edges[fromid].add(edgekey)
		self.neighbour_edges[toid].add(edgekey)
