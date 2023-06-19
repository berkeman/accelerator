% def fixit(x):
%     # Need something that produces valid selectors
%     return x.replace('/', 'slash').replace('.', 'dot')
% end

<!--
	@@@ helhetsgrepp på escaping!
	@@@ javascript alla let, var, const
	@@@ css-a grafens fontstorlekar osv [Paolo]
	@@@ visa filename på csvimport kanske?
	@@@ mark node while menu active  (kanske använda "this" som Carl pratade om)
	@@@ man vill veta vilken metod ett subjob i subjoblistan är (men den infon skickas inte över)

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
		function getHeight(element) {
			var styles = window.getComputedStyle(element);
			var padding = parseFloat(styles.paddingTop) + parseFloat(styles.paddingBottom);
			return element.clientHeight - padding;
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
				popup.style.left = e.clientX - getWidth(popup) + 'px'
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
		shape = document.querySelector('#jobgraph');
		console.log('init', shape.getAttribute("viewBox"));
		const init = shape.viewBox.baseVal;
		console.log('init', init);
		var mouseStartPosition = {x: 0, y: 0};
		var mousePosition = {x: 0, y: 0};
		var viewboxStartPosition = {x: 0, y: 0};
		var viewboxPosition = {x: init.x, y: init.y};
		var viewboxSize = {x: init.width, y: init.height};
		var viewboxScale = 1;
		var actualscale = Math.max(init.width / getWidth(shape), init.height / shape.clientHeight);
		console.log('actual', actualscale);
		var mouseDown = false;
		shape.addEventListener("mousemove", mousemove);
		shape.addEventListener("mousedown", mousedown);
		shape.addEventListener("wheel", wheel);
		console.log('init scale', viewboxScale)

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

		function mouseup(e) {
			window.removeEventListener("mouseup", mouseup);
			mouseDown = false;
			e.preventDefault();
		}

		function mousemove(e) {
			mousePosition.x = e.offsetX;
			mousePosition.y = e.offsetY;
			if (mouseDown) {
				viewboxPosition.x = viewboxStartPosition.x + (mouseStartPosition.x - e.pageX) * actualscale;
				viewboxPosition.y = viewboxStartPosition.y + (mouseStartPosition.y - e.pageY) * actualscale;
				setviewbox();
			}
			e.preventDefault();
		}

		function wheel(e) {
			var scale = (e.deltaY < 0) ? 0.90 : 1/0.90;
			if ((viewboxScale * scale < 8.) && (viewboxScale * scale > 1./256.))
			{
				var mpos = {x: mousePosition.x * actualscale, y: mousePosition.y * actualscale};
				viewboxPosition.x = viewboxPosition.x + (mpos.x * (1-scale));
				viewboxPosition.y = viewboxPosition.y + (mpos.y * (1-scale));
				viewboxScale *= scale;
				actualscale *= scale;
				setviewbox();
			}
			e.preventDefault();
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
	</script>
</div>
