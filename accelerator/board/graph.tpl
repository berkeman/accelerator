<!--
	@@@ helhetsgrepp på escaping!
	@@@ javascript alla let, var, const
	@@@ css-a grafens fontstorlekar osv [Paolo]
	@@@ visa filename på csvimport kanske?
	@@@ mark node while menu active  (kanske använda "this" som Carl pratade om)

	@@@ x man vill veta vilken metod ett subjob i subjoblistan är (men den infon skickas inte över)
	@@@ X traversera urdlistor baklänges också!
	@@@ X använd ax_repr mm samt template ur board.py!
	@@@ X grafen följer inte musen i skala vid inzoom av stor graph
	@@@ X string and variable concatenation to simplify "..and x more" and input args to populatelist.
	@@@ X this is only for job graphs and urdlists,  DATASETS REMAIN
	@@@ X atmaxdepth and color are orthogonal right now, both set in graph.py
	@@@ X marginaler på sidorna runt svgn
-->


<div id="svgcontainer" class="box">
	<script>
		function getWidth(element) {
			var styles = window.getComputedStyle(element);
			var padding = parseFloat(styles.paddingLeft) + parseFloat(styles.paddingRight);
			return element.clientWidth - padding;
		}
	</script>

	% if graphtype in ('job', 'urditem'):
	%    include('jobpopup')
	% else:
	%    include('datasetpopup')
	% end

	<script>
		function positionpopup(popup, e) {
			if (e.clientX > getWidth(document.querySelector('#svgcontainer')) / 2) {
				const x = Math.max(0, e.clientX - getWidth(popup));
				popup.style.left = x + 'px'
			} else {
				popup.style.left = e.clientX + 'px';
			}
			//if (e.clientY > getWidth(document.querySelector('#svgcontainer')) / 2)
			popup.style.top = e.clientY + 'px';
		}

		function highlight_nodes(thisnode, onoff) {
			if (onoff) {
				thisnode.setAttribute('fill', 'var(--node-highlight)');
				thisnode.setAttribute('stroke-width', '5');
			} else {
				thisnode.setAttribute('fill', thisnode.getAttribute('data-origfill'));
				thisnode.setAttribute('stroke-width', '2');
			}
			const neighbour_nodes = JSON.parse(thisnode.getAttribute('data-neighbour_nodes'));
			for (const jobid of neighbour_nodes) {
				const n = document.querySelector('#' + jobid);
				if (onoff) {
					n.setAttribute('fill', 'var(--node-highlight2)');
				} else {
					n.setAttribute('fill', n.getAttribute('data-origfill'));
				}
			}
			const neighbour_edges = JSON.parse(thisnode.getAttribute('data-neighbour_edges'));
			for (const edge of neighbour_edges) {
				const group = document.querySelector('#' + edge);
				for (const n of Array.from(group.children)) {
					if (onoff) {
						n.setAttribute('stroke-width', 6);
					} else {
						n.setAttribute('stroke-width', 2);
					}
				}
			}
		}
	</script>

	<svg id="jobgraph" version="1.1" xmlns="http://www.w3.org/2000/svg"
		viewBox="{{' '.join(map(str, (svgdata['bbox'])))}}" width="100%" height="400px">
	% if graphtype in ('job', 'urditem'):
	%    include('jobgraph')
	% else:
	%    include('datasetgraph')
	% end
	</svg>

	<script>
		let svg = document.querySelector('#jobgraph');
		let move_init_epage = {x: NaN, y: NaN};            // just declaring this variable
		let move_init_viewboxposition = {x: NaN, y: NaN};  // just declaring this variable
		let pt = svg.createSVGPoint();                     // just decraling a point variable
		let viewboxScale = 1;                              // at viewboxScale==1, everything fits perfectly.
		const init = svg.viewBox.baseVal;
		let viewboxPosition = {x: init.x, y: init.y};
		let viewboxSize = {x: init.width, y: init.height};
		let actualscale = Math.max(init.width / getWidth(svg), init.height / svg.clientHeight); // svg-pixels per screen-pixels
		let mouseDown = false;
		svg.addEventListener("mousemove", mousemove);
		svg.addEventListener("mousedown", mousedown);
		svg.addEventListener("wheel", wheel);

		function mousetosvgcoords(e) {
			// mouse pointer in svg coordinate system
			pt.x = e.pageX;
			pt.y = e.pageY;
			return pt.matrixTransform(svg.getScreenCTM().inverse());
		}

		function mousedown(e) {
			move_init_epage.x = e.pageX;
			move_init_epage.y = e.pageY;
			move_init_viewboxposition.x = viewboxPosition.x;
			move_init_viewboxposition.y = viewboxPosition.y;
			window.addEventListener("mouseup", mouseup);
			mouseDown = true;
			e.preventDefault();
			popupmenu_off();
		}

		function mouseup(e) {
			window.removeEventListener("mouseup", mouseup);
			mouseDown = false;
			e.preventDefault();
		}

		function mousemove(e) {
			if (mouseDown) {
				viewboxPosition.x = move_init_viewboxposition.x + (move_init_epage.x - e.pageX) * actualscale;
				viewboxPosition.y = move_init_viewboxposition.y + (move_init_epage.y - e.pageY) * actualscale;
				setviewbox();
			}
			e.preventDefault();
		}

		function wheel(e) {
			let scale = (e.deltaY < 0) ? 0.90 : 1/0.90;
			if ((viewboxScale * scale < 8.) && (viewboxScale * scale > 1./256.))
			{
				let mpos = mousetosvgcoords(e);
				viewboxPosition.x = mpos.x * (1 - scale) + scale * viewboxPosition.x;
				viewboxPosition.y = mpos.y * (1 - scale) + scale * viewboxPosition.y;
				console.log('offset after', viewboxPosition);
				viewboxScale *= scale;
				actualscale *= scale;
				setviewbox();
				console.log(actualscale, viewboxScale);
			}
			e.preventDefault();
		}

		function setviewbox() {
			let vp = {x: 0, y: 0};
			let vs = {x: 0, y: 0};
			vp.x = viewboxPosition.x;
			vp.y = viewboxPosition.y;
			vs.x = viewboxSize.x * viewboxScale;
			vs.y = viewboxSize.y * viewboxScale;
			svg.setAttribute("viewBox", vp.x + " " + vp.y + " " + vs.x + " " + vs.y);
		}
	</script>
</div>
