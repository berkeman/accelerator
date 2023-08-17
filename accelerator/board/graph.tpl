<script language="javascript" src="{{ name2hashed['svg.js'] }}"></script>
<div id="graph" class="box" style="height: 400px;">
	<script>
		(function () {
			const e = document.querySelector('#graph');
			% if mode == 'urd':
				fetch("/urd_graph/{{ url_quote(key) }}")
			% elif mode == 'job':
				fetch("/job_graph/{{ url_quote(key) }}")
			% else:
				fetch("/dataset_graph/{{ url_quote(key) }}")
			% end
			.then(res => {
				if (res.ok) return res.text();
				throw new Error('error response');
			})
			.then(res => {
				e.innerHTML = res;
				setTimeout(panzoom, 0);
			})
			.catch(error => {
				console.log(error);
				e.innerText = 'Failed to fetch graph';
			});
		})();
	</script>
</div>


<script>
	function getWidth(element) {
		var styles = window.getComputedStyle(element);
		var padding = parseFloat(styles.paddingLeft) + parseFloat(styles.paddingRight);
		return element.clientWidth - padding;
	}
	function positionpopup(popup, e) {
		if (e.clientX > getWidth(document.querySelector('#svg')) / 2) {
			const x = Math.max(0, e.clientX - getWidth(popup));
			popup.style.left = x + 'px'
		} else {
			popup.style.left = e.clientX + 'px';
		}
		//if (e.clientY > getWidth(document.querySelector('#svgcontainer')) / 2)
		popup.style.top = e.clientY + 'px';
	}
</script>


<div id="popupmenu" class="box">
	<div id="method" style="font-style:italic;font-weight:bold;text-align:center"></div><br>
	<div id="atmaxdepth" style="display:none"><font color="var(--popup-atmaxdepth)">
		<b>Reached recursion limit - no dependencies drawn!<br>&nbsp</b>
	</font></div>
	% if mode in ('job', 'urd'):
		<div id="notinurdlist" style="display:none">
			Job not in this urdlist or any of its dependencies.<br>&nbsp;
		</div>
		Job: <a id="jobid" href=""></a><br><br>
		<a id="source">Source</a>  <a id="help">Help</a>
		<div id="inthisurdlist" style="display:none">
			<br>Job in depurdlist <a href="".></a>
		</div>
		<div id="files" style="display:none">
			<br><h1>Files:</h1>
				<ul id="filestable"></ul>
		</div>
		<div id="datasets" style="display:none">
			<br><h1>Datasets:</h1>
				<ul id="datasetstable"></ul>
		</div>
		<div id="subjobs" style="display:none">
			<br><h1>Subjobs:</h1>
				<ul id="subjobstable"></ul>
		</div>
	% else:
		Dataset: <a id="dataset" href="pelle">kalle</a><br>
		Job: <a id="jobid" href=""></a><br><br>
		<a id="source">Source</a>  <a id="help">Help</a>
		<div id="columns" style="display:none">
			<br><h1>Columns:</h1>
			<ul id="columnstable"></ul>
		</div>
	% end
	<br>
	<div id="timestamp"></div>
</div>


<script>
	function populatelist(jobid, items, location, maxitems=5) {
		const thelist = document.querySelector(location);
		thelist.style = 'display:none';
		if (items.length) {
			thelist.style = 'display:block';
			var thetable = document.querySelector(location + 'table');
			thetable.innerHTML = '';
			ix = 0;
			for (const item of items) {
				% if mode in ('job', 'urd'):
					const x = document.createElement("a");
					if (location === '#files') {
						x.href = '/job/' + encodeURI(jobid) + '/' + item;
						x.textContent = item;
					} else if (location === '#datasets') {
						x.href = '/dataset/' + encodeURI(item);
						x.textContent = item;
					} else if (location === '#subjobs') {
						x.href = '/job/' + encodeURI(item[0]);
						x.textContent = item[0] + '    (' + item[1] + ')';
					}
					const li = document.createElement("li");
					li.appendChild(x);
					thetable.appendChild(li);
				% else:
					const x = document.createElement("tr");
					thetable.appendChild(x);
					const t1 = document.createElement("th");
					x.appendChild(t1);
					const t2 = document.createElement("th");
					x.appendChild(t2);
					t1.textContent = item[0];
					t2.textContent = item[1];
				% end
				ix += 1;
				if (items.length > maxitems && ix === maxitems) {
					const sublen = items.length - maxitems;
					const x = document.createTextNode("... and " +sublen.toString() + " more.");
					const li = document.createElement("li");
					li.appendChild(x);
					thetable.appendChild(li);
					break;
				}
			}
		}
	}

	% if mode in ('job', 'urd'):
		function popupmenu(e, jobid, files, datasets, subjobs, method, atmaxdepth, timestamp, notinurdlist) {
			const popup = document.querySelector("#popupmenu");
			popup.style.display = 'block';
			popup.children["jobid"].textContent = jobid;
			popup.children["jobid"].href =  "/job/" + encodeURI(jobid);
			popup.children["method"].textContent = method;
			popup.children["help"].href =  "/method/" + method;
			popup.children["source"].href ='/job/' + encodeURI(jobid) + "/method.tar.gz" + '/';
			popup.children["timestamp"].textContent = '[' + timestamp + ']';
			if (atmaxdepth === true) {
				popup.children["atmaxdepth"].style.display = 'block';
			} else {
				popup.children["atmaxdepth"].style.display = 'none';
			}
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
			populatelist(jobid, files, '#files');
			populatelist(jobid, datasets, '#datasets');
			populatelist(jobid, subjobs, '#subjobs');
	% else:
		function popupmenu(e, jobid, method, ds, columns, atmaxdepth, timestamp) {
			const popup = document.querySelector("#popupmenu");
			popup.style.display = 'block';
			popup.children["dataset"].textContent = ds;
			popup.children["dataset"].href = "/dataset/" + encodeURI(ds);
			popup.children["jobid"].textContent = jobid;
			popup.children["jobid"].href =  "/job/" + encodeURI(jobid);
			popup.children["method"].textContent = method;
			popup.children["help"].href = "/method/" + method;
			popup.children["source"].href ='/job/' + encodeURI(jobid) + "/method.tar.gz" + '/';
			popup.children["timestamp"].textContent = '[' + timestamp + ']';
			if (atmaxdepth === true) {
				popup.children["atmaxdepth"].style.display = 'block';
			} else {
				popup.children["atmaxdepth"].style.display = 'none';
			}
			populatelist(jobid, columns, '#columns');
	% end
		positionpopup(popup, e);
	}

	function popupmenu_off() {
		const popup = document.querySelector("#popupmenu");
		popup.style.display = 'none';
	}
</script>
