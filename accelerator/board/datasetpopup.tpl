<div id="popupmenu" class="box">
	<div id="method" style="font-style:italic;font-weight:bold;text-align:center"></div><br>
	<div id="atmaxdepth" style="display:none"><font color="var(--popup-atmaxdepth)">
		<b>Reached recursion limit - no dependencies drawn!<br>&nbsp</b>
	</font></div>
	Dataset: <a id="dataset" href="pelle">kalle</a><br>
	Job: <a id="jobid" href=""></a><br><br>
	<a id="source">Source</a>  <a id="help">Help</a>
	<div id="columns" style="display:none">
		<br><h1>Columns:</h1>
		<ul id="columnstable"></ul>
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
			if (e.clientX > getWidth(document.querySelector('#svg')) / 2) {
				const x = Math.max(0, e.clientX - getWidth(popup));
				popup.style.left = x + 'px'
			} else {
				popup.style.left = e.clientX + 'px';
			}
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
					const x = document.createElement("tr");
					thetable.appendChild(x);
					const t1 = document.createElement("th");
					x.appendChild(t1);
					const t2 = document.createElement("th");
					x.appendChild(t2);
					t1.textContent = item[0];
					t2.textContent = item[1];
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

		function popupmenu_off() {
			const popup = document.querySelector("#popupmenu");
			popup.style.display = 'none';
		}
	</script>
</div>
