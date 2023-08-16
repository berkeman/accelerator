<div id="popupmenu" class="box">
	<div id="method" style="font-style:italic;font-weight:bold;text-align:center"></div><br>
	Job: <a id="jobid" href=""></a><br><br>
	<a id="source">Source</a>  <a id="help">Help</a>
	<div id="atmaxdepth" style="display:none"><font color="var(--popup-atmaxdepth)">
		<b>Reached recursion limit - no dependencies drawn!</b>
	</font></div>
	<div id="notinurdlist" style="display:none">
		<br>Job not in this urdlist or any of its dependencies.
	</div>
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
	<br>
	<div id="timestamp"></div>
	<script>
		function getWidth(element) {
			var styles = window.getComputedStyle(element);
			var padding = parseFloat(styles.paddingLeft) + parseFloat(styles.paddingRight);
			return element.clientWidth - padding;
		}
		function positionpopup(popup, e) {
			if (e.clientX > getWidth(document.querySelector('#jobgraph2')) / 2) {
				const x = Math.max(0, e.clientX - getWidth(popup));
				popup.style.left = x + 'px'
			} else {
				popup.style.left = e.clientX + 'px';
			}
			console.log(e.clientX, e.clientY)
			//if (e.clientY > getWidth(document.querySelector('#svgcontainer')) / 2)
			popup.style.top = e.clientY + 'px';
		}
		function populatelist(jobid, items, location, maxitems=5) {
			const thelist = document.querySelector(location);
			thelist.style = 'display:none';
			if (items.length) {
				thelist.style = 'display:block';
				var thetable = document.querySelector(location + 'table');
				thetable.innerHTML = '';
				ix = 0;
				for (const item of items) {
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
		function popupmenu(e, jobid, files, datasets, subjobs, method, atmaxdepth, timestamp, notinurdlist) {
			const popup = document.querySelector("#popupmenu");
			popup.style.display = 'block';
			popup.children["jobid"].textContent = jobid;
			popup.children["jobid"].href =  "/job/" + encodeURI(jobid);
			popup.children["method"].textContent = method;
			popup.children["help"].href =  "/method/" + method;
			popup.children["source"].href ='/job/' + encodeURI(jobid) + "/method.tar.gz" + '/';
			popup.children["timestamp"].textContent = '[' + timestamp + ']';
			if (atmaxdepth === 'True') {
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

		function popupmenu_off() {
			const popup = document.querySelector("#popupmenu");
			popup.style.display = 'none';
		}
	</script>
</div>
