<div id="jobpopup">
	Dataset: <a id="dataset" href="pelle">kalle</a><br>
	Job: <a id="jobid" href="pelle">kalle</a><div id=method>dfdf</div>
	<a id="source">Source</a>  <a id="help">Help</a>
	<div id="atmaxdepth" style="display:none"><font color="var(--popup-atmaxdepth)">
		<b>Reached recursion limit - no dependencies drawn!</b>
	</font></div>
	<div id="columns" style="display:none">
		<br><h1>Columns:</h1>
		<table id="columnstable" style="margin-left:10px"></table>
	</div>
	<br><div id="timestamp"></div>

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
					console.debug(item, item, location);
					var x = document.createElement("tr");
					thetable.appendChild(x);
					var t1 = document.createElement("th");
					x.appendChild(t1);
					var t2 = document.createElement("th");
					x.appendChild(t2);
					t1.textContent = item[0];
					t2.textContent = item[1];
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

		function jobpopup(e, jobid, method, ds, columns, atmaxdepth, timestamp) {
			const popup = document.querySelector("#jobpopup");
			popup.style.display = 'block';
			jobid = encodeURIComponent(jobid);
			method= encodeURIComponent(method);
			ds = encodeURIComponent(ds);
			popup.style.top = '100px';
			popup.style.left = e.clientX + 'px';
			popup.children["dataset"].textContent = decodeURIComponent(ds);
			popup.children["dataset"].href = "/dataset/" + ds;
			popup.children["jobid"].textContent = jobid;
			popup.children["jobid"].href =  "/job/" + jobid;
			popup.children["method"].textContent = '(' + method + ')';
			popup.children["help"].href = "/method/" + method;
			popup.children["source"].href ='/job/' + jobid + "/method.tar.gz" + '/';
			popup.children["timestamp"].textContent = '[' + timestamp + ']';
			console.log(atmaxdepth)
			if (atmaxdepth === true) {
				popup.children["atmaxdepth"].style.display = 'block';
			} else {
				popup.children["atmaxdepth"].style.display = 'none';
			}
			populatelist(jobid, columns, '#columns');
		}

		function jobpopup_off() {
			const popup = document.querySelector("#jobpopup");
			popup.style.display = 'none';
		}
	</script>
</div>
