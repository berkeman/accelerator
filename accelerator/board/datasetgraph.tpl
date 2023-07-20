%from math import atan2, sin, cos, pi, sqrt
% arrowlen = 10
% arrowangle = pi/6

% for item in svgdata['nodes'].values():
%   color='node-ds-default'
%   if item.atmaxdepth:
%       color='node-atmaxdepth'
%   end
%   item.size = 30
	<circle
		id="{{item.nodeid}}"
		class="hovernode"
		onclick="popupmenu(
			event,
			{{js_quote(item.jobid)}},
			{{js_quote(item.method)}},
			{{js_quote(item.ds)}},
			{{js_quote(item.columns)}},
			{{js_quote(item.atmaxdepth)}},
			{{js_quote(item.timestamp)}},
		)"
		onmouseover="highlight_nodes(this, true)"
		onmouseout="highlight_nodes(this, false)"
		fill-opacity="50%"
		data-neighbour_nodes="{{js_quote(list(svgdata['neighbour_nodes'][item.nodeid]))}}"
		data-neighbour_edges="{{js_quote(list(svgdata['neighbour_edges'][item.nodeid]))}}"
		cx="{{item.x}}" cy="{{item.y}}" r="{{item.size}}"
		fill="var(--{{color}})"
		data-origfill="var(--{{color}})"
		stroke="black" stroke-width="2"
	/>
	<text x="{{ item.x }}" y="{{ item.y + item.size + 15 }}" font-weight="bold"
		font-size="12" text-anchor="middle" fill="black">
		<a href="{{ '/dataset/' + url_quote(item.ds) }}">{{ item.ds }}</a>
	</text>
	<text x="{{ item.x }}" y="{{ item.y + item.size + 30 }}"
		font-size="12" text-anchor="middle" fill="black">
		<a href="{{ '/job/' + url_quote(item.jobid) + '/method.tar.gz' + '/'}}">{{ item.method }}</a>
	</text>
	<text x="{{ item.x }}" y="{{ item.y + item.size + 45 }}"
		font-size="12" text-anchor="middle" fill="black">
		{{ item.lines }}
	</text>
% end
% # Draw edges
% for fromid, toid, relation in svgdata['edges']:
	% key = ''.join((fromid, toid))
	<g id={{key}}>
		% fromnode = svgdata['nodes'][fromid]
		% tonode = svgdata['nodes'][toid]
		% fx, fy = fromnode.x, fromnode.y
		% tx, ty = tonode.x, tonode.y
		% a = atan2(ty - fy, tx - fx)
		% fx = fx + fromnode.size * cos(a)
		% fy = fy + fromnode.size * sin(a)
		% tx = tx - tonode.size * cos(a)
		% ty = ty - tonode.size * sin(a)
		<line x1="{{fx}}" x2="{{tx}}" y1="{{fy}}" y2="{{ty}}" stroke="black" stroke-width="2"/>
		% x1 = tx - arrowlen * cos(a + arrowangle)
		% y1 = ty - arrowlen * sin(a + arrowangle)
		% x2 = tx - arrowlen * cos(a - arrowangle)
		% y2 = ty - arrowlen * sin(a - arrowangle)
		<polygon points="{{tx}},{{ty}} {{x1}},{{y1}} {{x2}},{{y2}}"/> stroke="black"/>
		% mx = fx + 8*cos(a) + 8*sin(a)
		% my = fy + 8*sin(a) - 8*cos(a)
		<text x={{mx}} y={{my}}
			transform="rotate({{a*180/pi}},{{mx}},{{my}})"
			text-anchor="start" font-size="9" fill="#a040a0">
			{{relation}}
	</g>
% end
