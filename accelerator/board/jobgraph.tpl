%from json import dumps
%from math import atan2, sin, cos, pi
% arrowlen = 10
% arrowangle = pi/6

<svg id="jobgraph" version="1.1" xmlns="http://www.w3.org/2000/svg"
	viewBox="{{' '.join(map(str, (svgdata['bbox'][0],svgdata['bbox'][1],svgdata['bbox'][2]-svgdata['bbox'][0],svgdata['bbox'][3]-svgdata['bbox'][1])))}}"
		width="100%" height="400px">
	% print(' '.join(map(str, (svgdata['bbox'][0],svgdata['bbox'][1],svgdata['bbox'][2]-svgdata['bbox'][0],svgdata['bbox'][3]-svgdata['bbox'][1]))))
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
		%     color='node-default'
		% end
		% item.size = 20 if item.notinurdlist else 30
		% name = item.method if item.method == item.name else '%s (%s)' % (item.method, item.name)
		<circle id="{{item.jobid}}" class="hovernode" onclick="jobpopup(
				event,
				{{dumps(item.jobid)}},
				{{dumps(item.files)}},
				{{dumps(item.datasets)}},
				{{dumps(tuple(item.subjobs.keys()))}},
				{{dumps(item.method)}},
				{{dumps(item.atmaxdepth)}},
				{{dumps(item.timestamp)}},
				{{dumps(item.notinurdlist)}},
			)"
			onmouseover="highlight_nodes(this, true)"
			onmouseout="highlight_nodes(this, false)"
			fill-opacity="50%"
			data-neighbour_nodes="{{dumps(list(svgdata['neighbour_nodes'][item.jobid]))}}"
			data-neighbour_edges="{{dumps(list(svgdata['neighbour_edges'][item.jobid]))}}"
			cx="{{item.x}}" cy="{{item.y}}" r="{{item.size}}"
			fill="var(--{{color}})"
			data-origfill="var(--{{color}})"
			stroke="black" stroke-width="2"
		/>
		<text x="{{ item.x }}" y="{{ item.y + item.size + 15 }}" font-weight="bold"
			font-size="12" text-anchor="middle" fill="black">
			<a href="{{ '/job/' + item.jobid }}">{{ item.jobid }}</a>
		</text>
		<text x="{{ item.x }}" y="{{ item.y + item.size + 30 }}"
			font-size="12" text-anchor="middle" fill="black">
			<a href="{{ '/job/' + item.jobid + '/method.tar.gz' + '/'}}">{{ name}}</a>
		</text>
	% end
	% # Draw edges
	% for fromid, toid in svgdata['edges']:
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
</svg>
