from math import atan2, pi, cos, sin
from html import escape
from json import dumps
class SVG:
	def __init__(self):
		self.header ="""<svg id="pelle" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="%d %d %d %d" width="100%%" height="300px">
<style>
	.bar:hover {
		fill: #ec008c;
		opacity: 1;
	}
</style>
<script>
	function makebox() {
		const div = document.createElement('DIV');
		div.innerText = 'pelle' // dina länkar etc, oxo med createElement
		div.style.position = 'relative';
		div.style.top = '40px';
		div.style.left = '40px';
		container.appendChild(div);
	}
	function jobpopup(e, jobid, files, datasets, subjobs) {
		const popup = document.querySelector("#jobpopup");
		popup.style.display = 'block';
		//popup.style.top = e.clientY + 'px';
		popup.style.top = '100px';
		popup.style.left = e.clientX + 'px';
		popup.children["jobid"].textContent = jobid;
		popup.children["jobid"].setAttribute("href", "../job/" + jobid);

		const items = JSON.parse(files);
		flist = popup.children['files'];
		while( flist.firstChild ){
			flist.removeChild( flist.firstChild );
		}
		for (i = 0; i < items.length; ++i) {
			var li = document.createElement('li');
			li.innerText = items[i];
			flist.appendChild(li);
		}

		const items2 = JSON.parse(datasets);
		flist = popup.children['datasets'];
		while( flist.firstChild ){
			flist.removeChild( flist.firstChild );
		}
		for (i = 0; i < items2.length; ++i) {
			var li = document.createElement('li');
			li.innerText = items2[i];
			flist.appendChild(li);
		}

		const items3 = JSON.parse(subjobs);
		flist = popup.children['subjobs'];
		while( flist.firstChild ){
			flist.removeChild( flist.firstChild );
		}
		for (i = 0; i < items3.length; ++i) {
			var li = document.createElement('li');
			li.innerText = items3[i];
			flist.appendChild(li);
		}

	}
</script>
"""
		self.footer = """</svg>
<script>
	shape = document.getElementById("pelle");
	const container = document.querySelector("#svgcontainer");
	var mouseStartPosition = {x: 0, y: 0};
	var mousePosition = {x: 0, y: 0};
	var viewboxStartPosition = {x: 0, y: 0};
	var viewboxPosition = {x: %d, y: %d};
	var viewboxSize = {x: %d, y: %d};
	var viewboxScale = 1.0;
	var mouseDown = false;
	shape.addEventListener("mousemove", mousemove);
	shape.addEventListener("mousedown", mousedown);
	shape.addEventListener("wheel", wheel);
	function mousedown(e)
	{
		mouseStartPosition.x = e.pageX;
		mouseStartPosition.y = e.pageY;
		viewboxStartPosition.x = viewboxPosition.x;
		viewboxStartPosition.y = viewboxPosition.y;
		window.addEventListener("mouseup", mouseup);
		mouseDown = true;
		e.preventDefault();
	}
	function setviewbox()
	{
		var vp = {x: 0, y: 0};
		var vs = {x: 0, y: 0};
		vp.x = viewboxPosition.x;
		vp.y = viewboxPosition.y;
		vs.x = viewboxSize.x * viewboxScale;
		vs.y = viewboxSize.y * viewboxScale;
		shape = document.getElementById("pelle");
		shape.setAttribute("viewBox", vp.x + " " + vp.y + " " + vs.x + " " + vs.y);
	}
	function mousemove(e)
	{
		mousePosition.x = e.offsetX;
		mousePosition.y = e.offsetY;
		if (mouseDown)
		{
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
"""
		self.s = ''
		self.nodecoords = dict()

	def node(self, id, x, y, text, size=30, color='magenta'):
		self.nodecoords[id] = (x, y, size)
		r = size
		self.s += '<circle  class="bar" cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>\n'.format(cx=x, cy=y, r=r, fill=color)
		self.s += '<circle onclick="jobpopup(event, popupmsg)" class="bar" cx="{cx}" cy="{cy}" r="{r}" fill="transparent" stroke="{s}" stroke_width="{sw}">\n'.format(cx=x, cy=y, r=r, s="black", sw=4)
		self.s += '<title>"pelle<b>pelle</b>"</title>\n'
		self.s += '</circle>\n'
		for ix, line in enumerate(text.split('\n'), 1):
			self.s += '<text x="{x}" y="{y}" font-size="{fs}" text-anchor="middle" fill="{fill}">{text}</text>\n'.format(x=x, y=y+r+15*ix, fs=12, fill='black', text=line)

	def jobnode(self, id, x, y, text, size=30, color='magenta'):
		MAXLEN=5
		self.nodecoords[id] = (x, y, size)
		r = size
		files = sorted(id.files())
		files = files[:MAXLEN] if len(files) > MAXLEN else files
		datasets = list(id.datasets[:MAXLEN] if len(id.datasets) > MAXLEN else id.datasets)
		subjobs = id.post.subjobs[:MAXLEN] if len(id.post.subjobs) > MAXLEN else id.post.subjobs
		self.s += '<circle  class="bar" cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>\n'.format(cx=x, cy=y, r=r, fill=color)
		self.s += '<circle onclick="jobpopup(event, \'{jobid}\', \'{files}\', \'{datasets}\', \'{subjobs}\')" class="bar" cx="{cx}" cy="{cy}" r="{r}" fill="transparent" stroke="{s}" stroke_width="{sw}">\n'.format(
			cx=x, cy=y, r=r, s="black", sw=4, jobid=str(id),
			files=escape(dumps(sorted(files))),
			datasets=escape(dumps(sorted(datasets))),
			subjobs=escape(dumps(sorted(subjobs))),
		)
		self.s += '<title>"pelle<b>pelle</b>"</title>\n'
		self.s += '</circle>\n'
		for ix, line in enumerate(text.split('\n'), 1):
			self.s += '<text x="{x}" y="{y}" font-size="{fs}" text-anchor="middle" fill="{fill}">{text}</text>\n'.format(x=x, y=y+r+15*ix, fs=12, fill='black', text=line)

	def arrow(self, fromid, toid, linewidth=2, arrowangle=pi / 6, arrowlen=10):
		arrowangle = pi / 6
		arrowlen = 10
		x1, y1, fromradius = self.nodecoords[fromid]
		x2, y2, toradius = self.nodecoords[toid]
		a = atan2(y2 - y1, x2 - x1)
		x1 = x1 + fromradius * cos(a)
		y1 = y1 + fromradius * sin(a)
		x2 = x2 - toradius * cos(a)
		y2 = y2 - toradius * sin(a)
		self.s += '<line x1="{x1}" x2="{x2}" y1="{y1}" y2="{y2}" stroke="{s}" stroke-width="{sw}"/>\n'.format(x1=x1, x2=x2, y1=y1, y2=y2, s='black', sw=linewidth)
		px2 = x2 - arrowlen * cos(a + arrowangle)
		py2 = y2 - arrowlen * sin(a + arrowangle)
		self.s += '<line x1="{x1}" x2="{x2}" y1="{y1}" y2="{y2}" stroke="{s}" stroke-width="{sw}"/>\n'.format(x1=x2, x2=px2, y1=y2, y2=py2, s='black', sw=linewidth)
		px2 = x2 - arrowlen * cos(a - arrowangle)
		py2 = y2 - arrowlen * sin(a - arrowangle)
		self.s += '<line x1="{x1}" x2="{x2}" y1="{y1}" y2="{y2}" stroke="{s}" stroke-width="{sw}"/>\n'.format(x1=x2, x2=px2, y1=y2, y2=py2, s='black', sw=linewidth)

	def getsvg(self, bbox=(0,0,600,300)):
		return '\n'.join((self.header % bbox, self.s, self.footer % bbox))
