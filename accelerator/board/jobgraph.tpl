%from json import dumps
%from math import atan2, sin, cos, pi
% arrowlen = 20
% arrowangle = pi/8

% for item in svgdata['nodes'].values():
	<text x="{{item.x}}" y="{{item.y + 5}}" fill="blue4" text-anchor="middle" font-weight="bold">
		{{ ''.join(('D' if item.datasets else '', 'F' if item.files else '', 'S' if item.subjobs else ''))}}
	</text>
	% if item.atmaxdepth:
	%     color='node-atmaxdepth'
	% elif item.notinurdlist is True:
	%     color='node-nourdlist'
	% elif isinstance(item.notinurdlist, str):
	%     color='node-inanotherurdlist'
	% else:
	%     color='node-job-default'
	% end
	% item.size = 20 if item.notinurdlist else 30
	% if item.name is None or item.name == item.method:
	%     name = item.method
	% else:
	%     name = '%s (%s)' % (item.method, item.name)
	% end
	<circle
		id="{{item.nodeid}}"
		class="hovernode"
		onclick="popupmenu(
			event,
			{{dumps(item.jobid)}},
			{{dumps(item.files)}},
			{{dumps(item.datasets)}},
			{{dumps(item.subjobs)}},
			{{dumps(item.method)}},
			{{dumps(item.atmaxdepth)}},
			{{dumps(item.timestamp)}},
			{{dumps(item.notinurdlist)}},
		)"
		onmouseover="highlight_nodes(this, true)"
		onmouseout="highlight_nodes(this, false)"
		fill-opacity="50%"
		data-neighbour_nodes="{{dumps(list(svgdata['neighbour_nodes'][item.nodeid]))}}"
		data-neighbour_edges="{{dumps(list(svgdata['neighbour_edges'][item.nodeid]))}}"
		cx="{{item.x}}" cy="{{item.y}}" r="{{item.size}}"
		fill="var(--{{color}})"
		data-origfill="var(--{{color}})"
		stroke="black" stroke-width="2"
	/>
	<text x="{{ item.x }}" y="{{ item.y + item.size + 15 }}" font-weight="bold"
		font-size="12" text-anchor="middle" fill="black">
		<a href="{{ '/job/' + url_quote(item.jobid) }}">{{ item.jobid }}</a>
	</text>
	<text x="{{ item.x }}" y="{{ item.y + item.size + 30 }}"
		font-size="12" text-anchor="middle" fill="black">
		<a href="{{ '/job/' + url_quote(item.jobid) + '/method.tar.gz' + '/'}}">{{ name}}</a>
	</text>
% end
% # Draw edges
% for fromid, toid, _ in svgdata['edges']:
	% key = ''.join((fromid, toid))
	<g id={{key}}>
		% fromnode = svgdata['nodes'][fromid]
		% tonode = svgdata['nodes'][toid]
		% x1, y1 = fromnode.x, fromnode.y
		% x2, y2 = tonode.x, tonode.y
		% a = atan2(y2 - y1, x2 - x1)
		% x1 = x1 + fromnode.size * cos(a)
		% y1 = y1 + fromnode.size * sin(a)
		% x2 = x2 - tonode.size * cos(a)
		% y2 = y2 - tonode.size * sin(a)
		<line x1="{{x1}}" x2="{{x2}}" y1="{{y1}}" y2="{{y2}}" stroke="black" stroke-width="2"/>
		% x1 = x2 - arrowlen * cos(a + arrowangle)
		% y1 = y2 - arrowlen * sin(a + arrowangle)
		<line x1="{{x1}}" x2="{{x2}}" y1="{{y1}}" y2="{{y2}}" stroke="black" stroke-width="2"/>
		% x1 = x2 - arrowlen * cos(a - arrowangle)
		% y1 = y2 - arrowlen * sin(a - arrowangle)
		<line x1="{{x1}}" x2="{{x2}}" y1="{{y1}}" y2="{{y2}}" stroke="black" stroke-width="2"/>
	</g>
% end
