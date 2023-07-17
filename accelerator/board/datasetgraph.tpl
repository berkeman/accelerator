%from json import dumps
%from math import atan2, sin, cos, pi, sqrt
% arrowlen = 10
% arrowangle = pi/6

% for ds, item in svgdata['nodes'].items():
%   color='node-ds-default'
%   if item.atmaxdepth:
%       color='node-atmaxdepth'
%   end
%   item.size = 30
	<circle id="{{item.nodeid}}" class="hovernode" onclick="jobpopup(
			event,
			{{dumps(item.jobid)}},
			{{dumps(item.method)}},
			{{dumps(ds)}},
			{{dumps(item.columns)}},
			{{dumps(item.atmaxdepth)}},
			{{dumps(item.timestamp)}},
		)"
		onmouseover="highlight_nodes(this, true)"
		onmouseout="highlight_nodes(this, false)"
		fill-opacity="50%"
		data-neighbour_nodes="{{dumps(list(svgdata['neighbour_nodes'][ds]))}}"
		data-neighbour_edges="{{dumps(list(svgdata['neighbour_edges'][ds]))}}"
		cx="{{item.x}}" cy="{{item.y}}" r="{{item.size}}"
		fill="var(--{{color}})"
		data-origfill="var(--{{color}})"
		stroke="black" stroke-width="2"
	/>
	<text x="{{ item.x }}" y="{{ item.y + item.size + 15 }}" font-weight="bold"
		font-size="12" text-anchor="middle" fill="black">
		<a href="{{ '/dataset/' + ds }}">{{ ds }}</a>
	</text>
	<text x="{{ item.x }}" y="{{ item.y + item.size + 30 }}"
		font-size="12" text-anchor="middle" fill="black">
		<a href="{{ '/job/' + item.jobid + '/method.tar.gz' + '/'}}">{{ item.method }}</a>
	</text>
	<text x="{{ item.x }}" y="{{ item.y + item.size + 45 }}"
		font-size="12" text-anchor="middle" fill="black">
		{{len(item.columns)}} x {{'{:,}'.format(sum(ds.lines)).replace(',', ' ')}}
	</text>
% end
% # Draw edges
% for fromid, toid, relation in svgdata['edges']:
	% key = ''.join((fromid, toid))
	<g id={{key}}>
		% fromnode = svgdata['nodes'][fromid]
		% tonode = svgdata['nodes'][toid]
		% x1, y1 = fromnode.x, fromnode.y
		% x2, y2 = tonode.x, tonode.y
		% a = atan2(y2 - y1, x2 - x1)
		% L = sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))
		% mx = x1 + (L-70)/L*(x2-x1)
		% my = y1 + (L-70)/L*(y2-y1)
		% vx =  my / sqrt(mx*mx+my*my) * 8
		% vy = -mx / sqrt(mx*mx+my*my) * 8
		<text x={{mx+vx}} y={{my+vy}}
			transform="rotate({{a*180/pi}},{{mx+vx}},{{my+vy}})"
			text-anchor="middle" font-size="12">
			{{relation}}
		</text>
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
