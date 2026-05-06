const fetchJSON = async (path) => {
	try {
		const res = await fetch(path);
		if (!res.ok) return null;
		return await res.json();
	} catch (e) {
		return null;
	}
};

const el = (id) => document.getElementById(id);

function animatePanel(id) {
	const node = el(id);
	if (!node) return;
	node.classList.add('pulse');
	setTimeout(() => node.classList.remove('pulse'), 1600);
}

async function updateTime() {
	const t = await fetchJSON('/api/time');
	const clock = el('clock');
	if (!clock) return;
	if (t && t.iso) {
		const dt = new Date(t.iso);
		clock.textContent = dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
	} else {
		const now = new Date();
		clock.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
	}
}

async function updateWeather() {
	const w = await fetchJSON('/api/weather');
	const node = el('weather');
	const body = node && node.querySelector('.panel-body');
	if (!body) return;
	let html = '—';
	if (w && w.attributes) {
		const a = w.attributes;
		const temp = a.temperature !== undefined ? `${a.temperature}°` : '';
		const cond = a.condition || a.state || a.weather || '';
		html = `<div class="big">${temp}</div><div class="small">${cond}</div>`;
	}
	body.innerHTML = html;
	animatePanel('weather');
}

async function updateCalendar() {
	const c = await fetchJSON('/api/calendar');
	const node = el('calendar');
	const body = node && node.querySelector('.panel-body');
	if (!body) return;
	let html = '<div class="small">No events</div>';
	if (c && c.length) {
		html = '<ul>';
		for (let e of c.slice(0, 4)) {
			const start = e.start ? e.start.replace('T', ' ').split('+')[0] : '';
			html += `<li>${start} — ${e.title || e.name || 'Event'}</li>`;
		}
		html += '</ul>';
	}
	body.innerHTML = html;
	animatePanel('calendar');
}

async function updateHeadlines() {
	const h = await fetchJSON('/api/headlines');
	const node = el('headlines');
	const body = node && node.querySelector('.panel-body');
	if (!body) return;
	let html = '<div class="small">—</div>';
	if (h && h.length) {
		html = '<ul>';
		for (let item of h.slice(0, 3)) {
			html += `<li>${item.title}</li>`;
		}
		html += '</ul>';
	}
	body.innerHTML = html;
	animatePanel('headlines');
}

// initial
updateTime();
updateWeather();
updateCalendar();
updateHeadlines();

// intervals
setInterval(updateTime, 1000);
setInterval(updateWeather, 30 * 1000);
setInterval(updateCalendar, 60 * 1000);
setInterval(updateHeadlines, 30 * 60 * 1000);
