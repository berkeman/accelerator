%from json import dumps

<!--
	@@@ atmaxdepth and color are orthogonal right now, both set in graph.py
	@@@ grafen följer inte musen i skala vid inzoom av stor graph
	@@@ marginaler på sidorna runt svgn
	@@@ visa filename på csvimport kanske?
	@@@ this is only for job graphs and urdlists,  DATASETS REMAIN
	@@@ string and variable concatenation to simplify "..and x more" and input args to populatelist.
	@@@ mark node while menu active  (kanske använda "this" som Carl pratade om)
-->

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
			<div id="timestamp"></div>
			<div id="atmaxdepth" style="display:none"><font color="#cc5522">
				<b>Reached recursion limit - no dependencies drawn!</b>
			</font></div>
			<div id="notinurdlist" style="display:none"><font color="#55cc22">
				<b>Job not in this urdlist or any of its dependencies.</b>
			</font></div>
			<div id="inthisurdlist" style="display:none"><font color="#55cc22">
				<b>Job in depurdlist <a href="".></a></b>
			</font></div>
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
				<nav>
					<ul id="subjobstable"></ul>
				</nav>
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
							 x.href = '/job/' + jobid + '/' + item;
						 } else if (location === '#datasets') {
							 x.href = '/dataset/' + item;
						 } else {
							 x.href= item;
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
			 function jobpopup(e, jobid, files, datasets, subjobs, method, atmaxdepth, timestamp, notinurdlist) {
				 const popup = document.querySelector("#jobpopup");
				 popup.style.display = 'block';
				 //popup.style.top = e.clientY + 'px';
				 popup.style.top = '100px';
				 popup.style.left = e.clientX + 'px';
				 popup.children["jobid"].textContent = jobid;
				 popup.children["jobid"].href =  "/job/" + jobid;
				 popup.children["source"].textContent = method;
				 popup.children["source"].href ='/job/' + jobid + "/method.tar.gz" + '/';
				 console.log(jobid, atmaxdepth)
				 popup.children["timestamp"].textContent = '[' + timestamp + ']';
				 if (atmaxdepth === 'True') {
					 popup.children["atmaxdepth"].style.display = 'block';
				 } else {
					 popup.children["atmaxdepth"].style.display = 'none';
				 }
				 console.debug('atmax and notinurdlist', atmaxdepth, notinurdlist);
				 if (notinurdlist === false ) {
					 popup.children["notinurdlist"].style.display = 'none';
					 popup.children["inthisurdlist"].style.display = 'none';
				 } else if (notinurdlist === true) {
					 popup.children["notinurdlist"].style.display = 'block';
					 popup.children["inthisurdlist"].style.display = 'none';
				 } else {
					 popup.children["notinurdlist"].style.display = 'none';
					 popup.children["inthisurdlist"].style.display = 'block';
					 const n = popup.querySelector('#inthisurdlist a');
					 n.href = '/urd/' + notinurdlist;
					 n.textContent = notinurdlist;
				 }
				 populatelist(jobid, files, '#files', '#filestable');
				 populatelist(jobid, datasets, '#datasets', '#datasetstable');
				 populatelist(jobid, subjobs, '#subjobs', '#subjobstable');
			 }

			 function jobpopup_off(e, jobid, files, datasets, subjobs, method) {
				 const popup = document.querySelector("#jobpopup");
				 popup.style.display = 'none';
			 }

			 % # egna attribut börja med "data-"
			 function highlight_nodes(thisnode, onoff) {
				 if (onoff) {
					 thisnode.setAttribute('fill', '#eeff88');
					 thisnode.setAttribute('stroke-width', '5');
				 } else {
					 thisnode.setAttribute('fill', thisnode.getAttribute('origfill'));
					 thisnode.setAttribute('stroke-width', '2');
				 }
				 const neighbour_nodes = JSON.parse(thisnode.getAttribute('neighbour_nodes'));
				 for (const jobid of neighbour_nodes) {
					 const n = document.querySelector('#' + jobid);
					 if (onoff) {
						 n.setAttribute('fill', 'var(--bgerr)');
					 } else {
						 n.setAttribute('fill', n.getAttribute('origfill'));
					 }
				 }
				 const neighbour_edges = JSON.parse(thisnode.getAttribute('neighbour_edges'));
				 for (const edge of neighbour_edges) {
					 const nn = document.querySelectorAll('#' + edge);
					 for (const n of nn) {
						 if (onoff) {
							 n.setAttribute('stroke-width', 6);
						 } else {
							 n.setAttribute('stroke-width', 2);
						 }
					 }
				 }
			 }
			</script>
        </div>

		<svg id="jobgraph" version="1.1" xmlns="http://www.w3.org/2000/svg"
				 viewBox="{{ ' '.join(str(x) for x in svgdata['bbox']) }}"
				 width="100%" height="300px">
			% for item in svgdata['nodes'].values():
			<text x="{{item.x}}" y="{{item.y + 5}}" fill="blue4" text-anchor="middle" font-weight="bold">
				{{ ''.join(('D' if item.datasets else '', 'F' if item.files else '', 'S' if item.subjobs else ''))}}
			</text>
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
					neighbour_nodes="{{dumps(list(svgdata['neighbour_nodes'][item.jobid]))}}"
					neighbour_edges="{{dumps(list(svgdata['neighbour_edges'][item.jobid]))}}"
					cx="{{item.x}}" cy="{{item.y}}" r="{{item.size}}"
					fill="{{item.color}}" origfill="{{item.color}}"
					stroke="black" stroke-width="2"
				/>
				<text x="{{ item.x }}" y="{{ item.y + item.size + 15 }}" font-weight="bold"
					font-size="12" text-anchor="middle" fill="black">
					<a href="{{ '/job/' + item.jobid }}">{{ item.jobid }}</a>
				</text>
				<text x="{{ item.x }}" y="{{ item.y + item.size + 30 }}"
					font-size="12" text-anchor="middle" fill="black">
					<a href="{{ '/job/' + item.jobid + '/method.tar.gz' + '/'}}">{{ item.method }}</a>
				</text>
			% end
			% for key, line in svgdata['edges'].items():
				% for (x1, y1, x2, y2) in line:
				% # @@@  stoppa in svg-kontainer "g" här som har pilens id
					<line x1="{{x1}}" x2="{{x2}}" y1="{{y1}}" y2="{{y2}}" id={{key}} stroke="black" stroke-width="2"/>
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
