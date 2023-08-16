from math import sin, cos, atan2, pi
from json import dumps
from html import escape
from accelerator.compat import url_quote
from accelerator.graph import joblist_graph, job_graph, dataset_graph
from accelerator import Job, DotDict


arrowlen = 15
arrowangle = pi / 8


def escdump(x):
	print('använd url_quote?')
	return(escape(dumps(x), quote=True))


svgheader = """<svg id="svg" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="{bbox}" width="100%" height="400px">\n"""

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
		{text}
	</text>
"""

linktemplate = """	<text x="{x}", y="{y}" font-weight="{weight}" font-size="12" text-anchor="middle" fill="black">
		<a href={href}>{text}</a>
	</text>
"""

centertemplate = """	<text x="{x}" y="{y}" fill="blue4" text-anchor="middle" font-weight="bold">
		{text}
	</text>
"""


def svg_dataset(inputitem):
	graph = dataset_graph(inputitem)
	res = svgheader.format(bbox=' '.join(map(str, graph['bbox'])))
	for name, item in graph['nodes'].items():
		item.size = 30
		color = 'node-atmaxdepth' if item.atmaxdepth else 'node-ds-default'
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
					item.method,
					item.ds,
					item.columns,
					item.atmaxdepth,
					item.timestamp,
				])
			)
		)
		res += linktemplate.format(
			x=item.x,
			y=item.y + item.size + 15,
			weight='bold',
			href='/dataset/' + url_quote(item.ds),
			text=item.ds,
		)
		res += linktemplate.format(
			x=item.x,
			y=item.y + item.size + 30,
			weight='normal',
			href='/job/' + url_quote(item.jobid) + '/method.tar.gz/',
			text=item.method,
		)
		res += texttemplate.format(
			x=item.x,
			y=item.y + item.size + 45,
			weight='normal',
			text=item.lines,
		)
	res = draw_edges(res, graph, '#a040a0')
	res += "</svg>"
	return res


def svg_joborurdlist(inputitem):
	if isinstance(inputitem, Job):
		graph = job_graph(inputitem)
	else:
		assert isinstance(inputitem, DotDict)
		graph = joblist_graph(inputitem)
	res = svgheader.format(bbox=' '.join(map(str, graph['bbox'])))
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
					name,
					item.atmaxdepth,
					item.timestamp,
					item.notinurdlist,
				])
			)
		)
		res += linktemplate.format(
			x=item.x,
			y=item.y + item.size + 15,
			weight='bold',
			href='/job/' + url_quote(item.jobid),
			text=item.jobid,
		)
		res += linktemplate.format(
			x=item.x,
			y=item.y + item.size + 30,
			weight='normal',
			href='/job/' + url_quote(item.jobid) + '/method.tar.gz' + '/',
			text=name,
		)
	res = draw_edges(res, graph, '#4040a0')
	res += "</svg>"
	return res


def draw_edges(res, graph, color='#a040a0'):
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
			x1=fx, y1=fy,
			x2=tx, y2=ty,
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
		res += """		<text x={x} y={y} transform="rotate({angle},{x},{y})" text-anchor="start" font-size="9" fill="{color}">\n			{text}\n		</text1>\n""".format(
			x=mx, y=my,
			angle=a * 180 / pi,
			text=relation,
			color=color,
		)
		res += """	</g>\n"""
	return res
