from collections import defaultdict
from math import atan2, pi, cos, sin
from accelerator import DotDict


class SVG:
	def __init__(self):
		self.s = ''
		self.nodecoords = dict()
		self.nodes = dict()
		self.edges = set()
		self.neighbours = defaultdict(set)

	def jobnode2(self, id, x, y, size=30, color='magenta'):
		self.nodecoords[id] = (x, y, size)
		self.nodes[id] = DotDict(
			jobid=str(id),
			method=id.method,
			files=sorted(id.files()),
			datasets=id.datasets,
			subjobs=id.post.subjobs,
			x=x,
			y=y,
			size=size,
			color='#aabbee',
		)

	def arrow2(self, fromid, toid):
		s = list()
		arrowangle = pi / 6
		arrowlen = 10
		x1, y1, fromradius = self.nodecoords[fromid]
		x2, y2, toradius = self.nodecoords[toid]
		a = atan2(y2 - y1, x2 - x1)
		x1 = x1 + fromradius * cos(a)
		y1 = y1 + fromradius * sin(a)
		x2 = x2 - toradius * cos(a)
		y2 = y2 - toradius * sin(a)
		s.append((x1, y1, x2, y2))
		x1 = x2 - arrowlen * cos(a + arrowangle)
		y1 = y2 - arrowlen * sin(a + arrowangle)
		s.append((x1, y1, x2, y2))
		x1 = x2 - arrowlen * cos(a - arrowangle)
		y1 = y2 - arrowlen * sin(a - arrowangle)
		s.append((x1, y1, x2, y2))
		self.edges.add(tuple(s))
		self.neighbours[fromid].add(toid)
		self.neighbours[toid].add(fromid)
