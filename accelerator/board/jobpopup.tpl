<div id="jobpopup">
	<a id="jobid" href="pelle">kalle</a>
	<div id="method"></div></br>
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
	<div id="timestamp"></div>
	<script>
		function populatelist(jobid, items, location, maxitems=5) {
			var thelist = document.querySelector(location);
			thelist.style = 'display:none';
			if (items.length) {
				thelist.style = 'display:block';
				var thetable = document.querySelector(location + 'table');
				thetable.innerHTML = '';
				ix = 0;
				for (const item of items) {
					var x = document.createElement("a");
					if (location === '#files') {
						x.href = '/job/' + jobid + '/' + item;
					} else if (location === '#datasets') {
						x.href = '/dataset/' + item;
					} else if (location === '#subjobs') {
						x.href = '/job/' + item;
					} else {
						x.href = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX';
					}
					x.textContent = item;
					var li = document.createElement("li");
					li.appendChild(x);
					thetable.appendChild(li);
					ix += 1;
					if (items.length > maxitems && ix === maxitems) {
						var sublen = items.length - maxitems;
						var x = document.createTextNode("... and " +sublen.toString() + " more.");
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
			popup.children["method"].textContent = '(' + method + ')';
			popup.children["help"].href =  "/method/" + method;
			popup.children["source"].href ='/job/' + jobid + "/method.tar.gz" + '/';
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
		}

		function jobpopup_off() {
			const popup = document.querySelector("#jobpopup");
			popup.style.display = 'none';
		}
	 </script>
</div>
