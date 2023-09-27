% from math import atan2, sin, cos, pi
% from json import dumps

% arrowlen = 15
% arrowangle = pi / 8
% smallnodesize = 20
% defaultnodesize = 30
% textrowspace = 15
% fontsize = 12
% edgetextcolor = '#224488'
% edgefontsize = 9

<svg id="svg" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="{{' '.join(map(str, bbox))}}" width="100%" height="400px">
%	# nodes
%	if type == 'job':
%		for name, item in nodes.items():
%			item.size = smallnodesize if item.notinurdlist else defaultnodesize
%			if item.atmaxdepth:
%				color = 'node-atmaxdepth'
%			elif item.notinurdlist is True:
%				color = 'node-nourdlist'
%			elif isinstance(item.notinurdlist, str):
%				color = 'node-inanotherurdlist'
%			else:
%				color = 'node-job-default'
%			end
%			if item.name is None or item.name == item.method:
%				name = item.method
%			else:
%				name = '%s (%s)' % (item.method, item.name)
%			end
		<text x="{{ item.x }}" y="{{ item.y + 5 }}" font-weight="bold" font-size="{{ fontsize }}" text-anchor="middle" fill="black">
			{{''.join(('D' if item.datasets else '', 'F' if item.files else '', 'S' if item.subjobs else ''))}}
		</text>
		<circle
			id="{{ item.nodeid }}"
			class="hovernode"
			cx="{{ item.x }}"
			cy="{{ item.y }}"
			r="{{ item.size }}"
			stroke="black"
			stroke_width="2"
			fill="var(--{{ color }})"
			fill-opacity="50%"
			data-origfill="var(--{{ color }})"
			data-neighbour_nodes="{{ dumps(list(item.neighbour_nodes)) }}"
			data-neighbour_edges="{{ dumps(list(item.neighbour_edges)) }}"
			onclick="popupmenu(
				event,
				{{ dumps(item.jobid) }},
				{{ dumps(item.files) }},
				{{ dumps(item.datasets) }},
				{{ dumps(item.subjobs) }},
				{{ dumps(item.method) }},
				{{ dumps(name) }},
				{{ dumps(item.atmaxdepth) }},
				{{ dumps(item.timestamp) }},
				{{ dumps(item.notinurdlist) }},
			)"
			onmouseover="highlight_nodes(this, true)"
			onmouseout="highlight_nodes(this, false)"
		/>
		<text x="{{ item.x }}" y="{{ item.y + item.size + 1 * textrowspace }}" font-weight="bold" font-size="{{ fontsize }}" text-anchor="middle" fill="black">
			<a href="{{'/job/' + url_quote(item.jobid)}}">{{item.jobid}}</a>
		</text>
		<text x="{{ item.x }}" y="{{ item.y + item.size + 2 * textrowspace }}" font-weight="normal" font-size="{{ fontsize }}" text-anchor="middle" fill="black">
			<a href="{{'/job/' + url_quote(item.jobid) +'/method.tar.gz/'}}">{{name}}</a>
		</text>
%		end
%	else:
%		assert type == 'ds'
%		for name, item in nodes.items():
%			item.size = defaultnodesize
%			color = 'node-atmaxdepth' if item.atmaxdepth else 'node-ds-default'
		<circle
			id="{{ item.nodeid }}"
			class="hovernode"
			cx="{{ item.x }}"
			cy="{{ item.y }}"
			r="{{ item.size }}"
			stroke="black"
			stroke_width="2"
			fill="var(--{{ color }})"
			fill-opacity="50%"
			data-origfill="var(--{{ color }})"
			data-neighbour_nodes="{{ dumps(list(item.neighbour_nodes)) }}"
			data-neighbour_edges="{{ dumps(list(item.neighbour_edges)) }}"
			onclick="popupmenu(
				event,
				{{ dumps(item.jobid) }},
				{{ dumps(item.method) }},
				{{ dumps(item.ds) }},
				{{ dumps(item.columns) }},
				{{ dumps(item.atmaxdepth) }},
				{{ dumps(item.timestamp) }},
			)"
			onmouseover="highlight_nodes(this, true)"
			onmouseout="highlight_nodes(this, false)"
		/>
		<text x="{{ item.x }}" y="{{ item.y + item.size + 1 * textrowspace }}" font-weight="bold" font-size="{{ fontsize }}" text-anchor="middle" fill="black">
			<a href="{{'/dataset/' + url_quote(item.ds)}}">{{item.ds}}</a>
		</text>
		<text x="{{ item.x }}" y="{{ item.y + item.size + 2 * textrowspace }}" font-weight="normal" font-size="{{ fontsize }}" text-anchor="middle" fill="black">
			<a href="{{'/job/' + url_quote(item.jobid) +'/method.tar.gz/'}}">{{name}}</a>
		</text>
		<text x="{{ item.x }}" y="{{ item.y + item.size + 3 * textrowspace }}" font-weight="normal" font-size="{{ fontsize }}" text-anchor="middle" fill="black">
			{{ item.lines }}
		</text>
%		end
%	end
%	# edges
%	for fromid, toid, relation in edges:
%		key = ''.join((fromid, toid))
	<g id="{{ key }}">
%		fromnode = nodes[fromid]
%		tonode = nodes[toid]
%		fx, fy = fromnode.x, fromnode.y
%		tx, ty = tonode.x, tonode.y
%		a = atan2(ty - fy, tx - fx)
%		fx = fx + fromnode.size * cos(a)
%		fy = fy + fromnode.size * sin(a)
%		tx = tx - tonode.size * cos(a)
%		ty = ty - tonode.size * sin(a)
		<line x1="{{ fx }}" x2="{{ tx }}" y1="{{ fy }}" y2="{{ ty }}" stroke="black" stroke_width="2"/>
%		x1 = tx - arrowlen * cos(a + arrowangle)
%		y1 = ty - arrowlen * sin(a + arrowangle)
%		x2 = tx - arrowlen * cos(a - arrowangle)
%		y2 = ty - arrowlen * sin(a - arrowangle)
		<polygon points="{{ tx }},{{ ty }} {{ x1 }},{{ y1 }} {{ x2 }},{{ y2 }}" stroke="black"/>
%		mx = fx + 4 * cos(a) - 6 * sin(a)
%		my = fy + 4 * sin(a) + 6 * cos(a)
		<text x={{ mx }} y={{ my }} transform="rotate({{ a * 180 / pi + 180 }}, {{ mx }}, {{ my }})" text-anchor="end" font-size="{{ edgefontsize }}" fill="{{ edgetextcolor }}">
		{{ relation }}
		</text1>
	</g>
%	end
</svg>
