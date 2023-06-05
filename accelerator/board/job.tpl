{{ ! template('head', title=job) }}

% from datetime import datetime
% from math import sin, cos, pi, atan2
% from html import escape
% from json import dumps
% def paramspart(name):
	% thing = params.get(name)
	% if thing:
		<h3>{{ name }}</h3>
		<div class="box">
			{
			<table>
			% for k, v in sorted(thing.items()):
				<tr><td>{{ k }}</td><td>=</td><td>
					{{ ! ax_link(v) }}
				</td></tr>
			% end
			</table>
			}
		</div>
	% end
% end

	<h1>{{ job }}</h1>
	% if aborted:
		<div class="warning">WARNING: Job didn't finish, information may be incomplete.</div>
	% elif not current:
		<div class="warning">Job is not current.</div>
	% end




	<h2>job graph</h2>
	<div id="svgcontainer">
		<style>
		 nav ul{
			 height:100px;
			 min-height:50px;
			 max-height:100%;
			 width:100%;}
		 nav ul{overflow:hidden; overflow-y:scroll;}
		 #jobpopup {
			 background: #ffffff;
		 }
		 #filestable {
			 list-style-type:none;
			 padding: 0px 0px 0px 10px;
		 }
		 #datasetstable {
			 list-style-type:none;
			 margin: 0;
			 padding: 10px;
		 }
		 #subjobstable {
			 list-style-type:none;
			 margin: 0;
			 padding: 10px;
		 }
		 #files > h1 {
			 font-size: 1.05em;
			 margin-bottom:  0em;
		 }
		 #datasets > h1 {
			 font-size: 1.05em;
			 margin-bottom:  0em;
		 }
		 #subjobs > h1 {
			 font-size: 1.05em;
			 margin-bottom:  0em;
		 }
		</style>
		<div id="jobpopup">
			<a id="jobid" href="pelle">kalle</a>  (<a id="source" href="to_source">method</a>)<br>
			<div id="files" style="display:none">
				<br><h1>Files:</h1>
				<nav>
					<ul id="filestable"></ul>
				</nav>
			</div>
			<div id="datasets" style="display:none">
				<br><h1>Datasets:</h1>
				<nav>
					<ul id="datasetstable"></ul>
				</nav>
			</div>
			<div id="subjobs" style="display:none">
				<br><h1>Subjobs:</h1>
				<ul id="subjobstable"></ul>
			</div>
			<script>
			 function populatelist(jobid, items, location, tablelocation, maxitems=5) {
				 var thelist = document.querySelector(location);
				 thelist.style = 'display:none';
				 if (items.length) {
					 thelist.style = 'display:block';
					 var thetable = document.querySelector(tablelocation);
					 thetable.innerHTML = '';
					 ix = 0;
					 for (const item of items) {
						 var x = document.createElement("a");
						 if (location === '#files') {
							 x.setAttribute("href", jobid + '/' + item);
						 } else if (location === '#datasets') {
							 x.setAttribute("href", '../dataset/' + item);
						 } else {
							 x.setAttribute("href", item);
						 }
						 x.textContent = item;
						 var li = document.createElement("li");
						 li.appendChild(x);
						 thetable.appendChild(li);
						 ix += 1;
						 if (items.length > maxitems && ix === maxitems) {
							 var sublen = items.length - maxitems;
							 var x = document.createTextNode("... and ${sublen} more.");
							 var li = document.createElement("li");
							 li.appendChild(x);
							 thetable.appendChild(li);
							 break;
						 }
					 }
				 }
			 }
			 //		@@@ this is only for job graphs, urdlists and datasets remain
			 //		@@@ string and variable concatenation to simplify "..and x more" and input args to populatelist.
			 //		@@@ mark node while menu active  (kanske använda "this" som Carl pratade om)
			 function jobpopup(e, jobid, files, datasets, subjobs, method) {
				 console.debug(method, jobid);
				 const popup = document.querySelector("#jobpopup");
				 popup.style.display = 'block';
				 //popup.style.top = e.clientY + 'px';
				 popup.style.top = '100px';
				 popup.style.left = e.clientX + 'px';
				 popup.children["jobid"].textContent = jobid;
				 popup.children["jobid"].setAttribute("href", "../job/" + jobid);
				 popup.children["source"].textContent = method;
				 popup.children["source"].setAttribute("href", jobid + "/method.tar.gz" + '/');
				 files = JSON.parse(files);
				 populatelist(jobid, files, '#files', '#filestable');
				 datasets = JSON.parse(datasets);
				 populatelist(jobid, datasets, '#datasets', '#datasetstable');
				 subjobs = JSON.parse(subjobs);
				 populatelist(jobid, subjobs, '#subjobs', '#subjobstable');
			 }
			 function jobpopup_off(e, jobid, files, datasets, subjobs, method) {
				 const popup = document.querySelector("#jobpopup");
				 popup.style.display = 'none';
			 }

			 function highlight(thisnode, onoff) {
				 if (onoff) {
					 thisnode.setAttribute('fill', '#eeff88');
				 } else {
					 thisnode.setAttribute('fill', thisnode.getAttribute('origfill'));
				 }
				 const neighbours = JSON.parse(thisnode.getAttribute('neighbours'));
				 for (const jobid of neighbours) {
					 const n = document.querySelector('#' + jobid);
					 console.log(n);
					 if (onoff) {
						 n.setAttribute('fill', '#ccff88');
					 } else {
						 n.setAttribute('fill', n.getAttribute('origfill'));
					 }
				 }
			 }

			</script>
        </div>


		<svg id="jobgraph" version="1.1" xmlns="http://www.w3.org/2000/svg"
				 viewBox="{{ ' '.join(str(x) for x in svgdata['bbox']) }}"
				 width="100%" height="300px">
			% for item in svgdata['nodes'].values():
				<circle id="{{item.jobid}}" class="hovernode" onclick="jobpopup(
				event,
				'{{item.jobid}}',
				'{{dumps(item.files)}}',
				'{{dumps(item.datasets)}}',
				'{{dumps(tuple(item.subjobs.keys()))}}',
				'{{item.method}}'
				)"
				onmouseover="highlight(this, true)"
				onmouseout="highlight(this, false)"
				neighbours="{{dumps(list(svgdata['neighbours'][item.jobid]))}}"
				cx="{{item.x}}" cy="{{item.y}}" r="{{item.size}}"
				fill="{{item.color}}" origfill="{{item.color}}"
				stroke="black" stroke-width="2"/>
				<text x="{{ item.x }}" y="{{ item.y + item.size + 15 }}" font-weight="bold" font-size="12" text-anchor="middle" fill="black"><a href="{{ item.jobid }}">{{ item.jobid }}</a></text>
				<text x="{{ item.x }}" y="{{ item.y + item.size + 30 }}" font-size="12" text-anchor="middle" fill="black"><a href="{{ item.jobid + '/method.tar.gz' + '/'}}">{{ item.method }}</a></text>
				<text x="{{item.x}}" y="{{item.y + 5}}" fill="blue4" text-anchor="middle">{{ ''.join(('D' if item.datasets else '', 'F' if item.files else '', 'S' if item.subjobs else ''))}}</text>
			% end
			% for line in svgdata['edges']:
				% for (x1, y1, x2, y2) in line:
					<line x1="{{x1}}" x2="{{x2}}" y1="{{y1}}" y2="{{y2}}" stroke="black" stroke-width="2"/>
				% end
			% end
		</svg>
		<script>
		 shape = document.querySelector('#jobgraph');
		 var mouseStartPosition = {x: 0, y: 0};
		 var mousePosition = {x: 0, y: 0};
		 var viewboxStartPosition = {x: 0, y: 0};
		 var viewboxPosition = {x: {{ svgdata['bbox'][0] }}, y: {{svgdata['bbox'][1] }}};
		 var viewboxSize = {x: {{svgdata['bbox'][2]}}, y: 300};
		 var viewboxScale = 1.0;
		 var mouseDown = false;
		 shape.addEventListener("mousemove", mousemove);
		 shape.addEventListener("mousedown", mousedown);
		 shape.addEventListener("wheel", wheel);
		 function mousedown(e) {
			 mouseStartPosition.x = e.pageX;
			 mouseStartPosition.y = e.pageY;
			 viewboxStartPosition.x = viewboxPosition.x;
			 viewboxStartPosition.y = viewboxPosition.y;
			 window.addEventListener("mouseup", mouseup);
			 mouseDown = true;
			 e.preventDefault();
			 jobpopup_off();
		 }
		 function setviewbox() {
			 var vp = {x: 0, y: 0};
			 var vs = {x: 0, y: 0};
			 vp.x = viewboxPosition.x;
			 vp.y = viewboxPosition.y;
			 vs.x = viewboxSize.x * viewboxScale;
			 vs.y = viewboxSize.y * viewboxScale;
			 shape = document.querySelector('#jobgraph');
			 shape.setAttribute("viewBox", vp.x + " " + vp.y + " " + vs.x + " " + vs.y);
		 }
		 function mousemove(e) {
			 mousePosition.x = e.offsetX;
			 mousePosition.y = e.offsetY;
			 if (mouseDown) {
				 viewboxPosition.x = viewboxStartPosition.x + (mouseStartPosition.x - e.pageX) * viewboxScale;
				 viewboxPosition.y = viewboxStartPosition.y + (mouseStartPosition.y - e.pageY) * viewboxScale;
				 setviewbox();
			 }
			 e.preventDefault();
		 }
		 function mouseup(e) {
			 window.removeEventListener("mouseup", mouseup);
			 mouseDown = false;
			 e.preventDefault();
		 }
		 function wheel(e) {
			 var scale = (e.deltaY < 0) ? 0.8 : 1.2;
			 if ((viewboxScale * scale < 8.) && (viewboxScale * scale > 1./256.))
			 {
				 var mpos = {x: mousePosition.x * viewboxScale, y: mousePosition.y * viewboxScale};
				 var vpos = {x: viewboxPosition.x, y: viewboxPosition.y};
				 var cpos = {x: mpos.x + vpos.x, y: mpos.y + vpos.y}
				 viewboxPosition.x = (viewboxPosition.x - cpos.x) * scale + cpos.x;
				 viewboxPosition.y = (viewboxPosition.y - cpos.y) * scale + cpos.y;
				 viewboxScale *= scale;
				 setviewbox();
			 }
			 e.preventDefault();
		 }
		</script>
	</div>





	<h2>setup</h2>
	<div class="box">
		<a href="/method/{{ params.method }}">{{ params.package }}.{{ params.method }}</a><br>
		<a href="/job/{{ job }}/method.tar.gz/">Source</a>
		<div class="box" id="other-params">
			% blacklist = {
			%     'package', 'method', 'options', 'datasets', 'jobs', 'params',
			%     'starttime', 'endtime', 'exectime', '_typing', 'versions',
			% }
			<table>
				<tr><td>starttime</td><td>=</td><td>{{ datetime.fromtimestamp(params['starttime']) }}</td></tr>
				% if not aborted:
					<tr><td>endtime</td><td>=</td><td>{{ datetime.fromtimestamp(params['endtime']) }}</td></tr>
					% exectime = params['exectime']
					% for k in sorted(exectime):
						<tr><td>exectime.{{ k }}</td><td>=</td><td>{{ ! ax_repr(exectime[k]) }}</td></tr>
					% end
				% end
				% for k in sorted(set(params) - blacklist):
					<tr><td>{{ k }}</td><td>=</td><td>{{ ! ax_repr(params[k]) }}</td></tr>
				% end
				% versions = params['versions']
				% for k in sorted(versions):
					<tr><td>versions.{{ k }}</td><td>=</td><td>{{ ! ax_repr(versions[k]) }}</td></tr>
				% end
			</table>
		</div>
		% if params.options:
			<h3>options</h3>
			<div class="box">
				{
				<table>
				% for k, v in sorted(params.options.items()):
					<tr><td>{{ k }}</td><td>=</td><td>{{ ! ax_repr(v) }}</td></tr>
				% end
				</table>
				}
			</div>
		%end
		% paramspart('datasets')
		% paramspart('jobs')
	</div>
	% if datasets:
		<h2>datasets</h2>
		<div class="box">
			<ul>
				% for ds in datasets:
					<li><a href="/dataset/{{ ds }}">{{ ds }}</a> {{ '%d columns, %d lines' % ds.shape }}</li>
				% end
			</ul>
		</div>
	% end
	% if subjobs:
		<h2>subjobs</h2>
		<div class="box">
			<ul>
				% for j, is_current in subjobs:
					<li><a href="/job/{{ j }}">{{ j }}</a> {{ j.method }}
					% if not is_current:
						<span class="warning">not current</span>
					% end
					</li>
				% end
			</ul>
		</div>
	% end
	% if files:
		<h2>files</h2>
		<div class="box">
			<ul>
				% for fn in sorted(files):
					<li><a target="_blank" href="/job/{{ job }}/{{ fn }}">{{ fn }}</a></li>
				% end
			</ul>
		</div>
	% end
	% if output:
		<h2>output</h2>
		<div class="box" id="output">
			<div class="spinner"></div>
		</div>
		<script language="javascript">
			(function () {
				const output = document.getElementById('output');
				const spinner = output.querySelector('.spinner');
				const create = function (name, displayname) {
					const el = document.createElement('DIV');
					el.id = displayname;
					el.className = 'spinner';
					output.appendChild(el);
					const h3 = document.createElement('H3');
					h3.innerText = displayname;
					const pre = document.createElement('PRE');
					fetch('/job/{{ job }}/OUTPUT/' + name, {headers: {Accept: 'text/plain'}})
					.then(res => {
						if (res.status == 404) {
							el.remove();
						} else if (!res.ok) {
							throw new Error(displayname + ' got ' + res.status)
						} else {
							return res.text();
						}
					})
					.then(text => {
						el.appendChild(h3);
						pre.innerText = text;
						el.appendChild(pre);
						el.className = '';
					})
					.catch(error => {
						console.log(error);
						el.appendChild(h3);
						pre.innerText = 'FETCH ERROR';
						el.appendChild(pre);
						el.className = 'error';
					});
				};
				create('prepare', 'prepare');
				for (let sliceno = 0; sliceno < {{ job.params.slices }}; sliceno++) {
					create(sliceno, 'analysis-' + sliceno);
				}
				create('synthesis', 'synthesis');
				spinner.remove();
			})();
		</script>
	% end
</body>
