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
		<div id="jobpopup">
			<a id="jobid" href="pelle">kalle</a><br>
			<div id="files" style="display:none">
				<br><b>Files:</b><br>
				<ul id="filestable"></ul>
			</div>
			<div id="datasets" style="display:none">
				<br><b>Datasets:</b><br>
				<ul id="datasetstable"></ul>
			</div>
			<div id="subjobs" style="display:none">
				<br><b>Subjobs:</b><br>
				<ul id="subjobstable"></ul>
			</div>
			<span id="message">hejsan <b>alla</b> glada  barn!</span>
		</div>
		<svg id="jobgraph" version="1.1" xmlns="http://www.w3.org/2000/svg"
		     viewBox="{{ ' '.join(str(x) for x in svgdata['bbox']) }}"
		     width="100%%" height="300px">
			% for item in svgdata['nodes'].values():
				<circle class="bar" cx="{{item.x}}" cy="{{item.y}}" r="{{item.size}}" fill="{{item.color}}"/>
				<circle class="bar" onclick="jobpopup(event, '{{escape(item.jobid)}}', '{{dumps(tuple(escape(x) for x in item.files))}}', '{{dumps(tuple(escape(x) for x in item.datasets))}}', '{{dumps(tuple(escape(x) for x in item.subjobs))}}')") cx="{{item.x}}" cy="{{item.y}}" r="{{item.size}}" fill="transparent" stroke="black" stroke_width="4"/>
				<text x="{{ item.x }}" y="{{ item.y + item.size + 15 }}" font-size="12" text-anchor="middle" fill="black">{{ item.jobid }}</text>
				<text x="{{ item.x }}" y="{{ item.y + item.size + 30 }}" font-size="12" text-anchor="middle" fill="black">{{ item.method }}</text>
			% end
			% for line in svgdata['edges']:
				% for (x1, y1, x2, y2) in line:
					<line x1="{{x1}}" x2="{{x2}}" y1="{{y1}}" y2="{{y2}}" stroke="black" stroke-width="2"/>
				% end
			% end
		</svg>
		<script>
		function createlist(items, location, tablelocation) {
		  var thelist = document.querySelector(location);
		  thelist.style = 'display:none';
		  if (items.length) {
            console.debug(thelist, items, location, tablelocation);
            thelist.style = 'display:block';
            var thetable = document.querySelector(tablelocation);
            thetable.innerHTML = '';
            ix = 0;
            for (const item of items) {
              console.debug(item)
              var x = document.createElement("a");
              x.setAttribute("href", item);
              x.textContent = item;
              var li = document.createElement("li");
              li.appendChild(x);
              thetable.appendChild(li);
              ix += 1;
              if (items.length > 5 && ix === 5) {
                var sublen = items.length - 5;
                var x = document.createTextNode("... and ${sublen} more.");
                var li = document.createElement("li");
                li.appendChild(x);
                thetable.appendChild(li);
                break;
              }
            }
		  }
		}

		function jobpopup(e, jobid, files, datasets, subjobs) {
		  const popup = document.querySelector("#jobpopup");
		  popup.style.display = 'block';
		  //popup.style.top = e.clientY + 'px';
		  popup.style.top = '100px';
		  popup.style.left = e.clientX + 'px';
		  popup.children["jobid"].textContent = jobid;
		  popup.children["jobid"].setAttribute("href", "../job/" + jobid);

		  files = JSON.parse(files);
		  createlist(files, '#files', '#filestable');
		  console.debug('1', datasets);
		  datasets = JSON.parse(datasets);
		  console.debug('2', datasets);
		  createlist(datasets, '#datasets', '#datasetstable');
		  subjobs = JSON.parse(subjobs);
		  console.debug('3', subjobs);
		  createlist(subjobs, '#subjobs', '#subjobstable');
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
