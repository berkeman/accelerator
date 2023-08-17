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
	<div id="method" style="font-style:italic;font-weight:bold;text-align:center"></div>
	<hr><br>
	<div id="atmaxdepth" style="display:none"><font color="var(--popup-atmaxdepth)">
		<b>Reached recursion limit,<br>no dependencies drawn!<br>&nbsp</b>
	</font></div>
	% if mode in ('job', 'urd'):
		<div id="notinurdlist" style="display:none">
			Job not in this urdlist or<br>any of its dependencies.<br>&nbsp;
		</div>
		Job: <a id="jobid" href=""></a><br>
		<div id="inthisurdlist" style="display:none">
			<br>Job in depurdlist <a href="".></a>
		</div>
		<div id="files" style="display:none">
			<br><h1>Files:</h1>
				<table id="filestable"></table>
		</div>
		<div id="datasets" style="display:none">
			<br><h1>Datasets:</h1>
				<table id="datasetstable"></table>
		</div>
		<div id="subjobs" style="display:none">
			<br><h1>Subjobs:</h1>
				<table id="subjobstable"></table>
		</div>
	% else:
		Dataset: <a id="dataset" href="pelle">kalle</a><br>
		Job: <a id="jobid" href=""></a><br>
		<div id="columns" style="display:none">
			<br><h1>Columns:</h1>
			<table id="columnstable"></table>
		</div>
	% end
	<br>
	<hr>
	<a id="source">Source</a>  <a id="help">Documentation</a>
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
					const tr = document.createElement("tr");
					const td = document.createElement("td");
					thetable.appendChild(tr);
					tr.appendChild(td);
					td.appendChild(x);
				% else:
					const x = document.createElement("tr");
					thetable.appendChild(x);
					const t1 = document.createElement("td");
					x.appendChild(t1);
					const t2 = document.createElement("td");
					x.appendChild(t2);
					t1.textContent = item[0];
					t2.textContent = item[1];
				% end
				ix += 1;
				if (items.length > maxitems && ix === maxitems) {
					const sublen = items.length - maxitems;
					const x = document.createTextNode("... and " +sublen.toString() + " more.");
					const tr = document.createElement("tr");
					const td = document.createElement("td");
					td.appendChild(x);
					tr.appendChild(td);
					thetable.appendChild(tr);
					break;
				}
			}
		}
	}

	% if mode in ('job', 'urd'):
		function popupmenu(e, jobid, files, datasets, subjobs, method, name, atmaxdepth, timestamp, notinurdlist) {
			const popup = document.querySelector("#popupmenu");
			popup.style.display = 'block';
			popup.children["jobid"].textContent = jobid;
			popup.children["jobid"].href =  "/job/" + encodeURI(jobid);
			popup.children["method"].textContent = name;
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
			positionpopup(popup, e);
		}
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
			positionpopup(popup, e);
		}
	% end

	function popupmenu_off() {
		const popup = document.querySelector("#popupmenu");
		popup.style.display = 'none';
	}
</script>
