async function fetchJSON(path){try{let r=await fetch(path);if(!r.ok) return null; return await r.json()}catch(e){return null}}

function el(id){return document.getElementById(id)}

async function updateTime(){let t=await fetchJSON('/api/time'); if(t) el('time').textContent = t.display}
async function updateWeather(){let w=await fetchJSON('/api/weather'); if(w && w.attributes){ let a=w.attributes; el('weather').innerHTML = `${a.temperature ?? ''}° ${a.condition ?? a.weather ?? ''}` } }
async function updateCalendar(){let c=await fetchJSON('/api/calendar'); if(c && c.length){ let html = '<ul>'; for(let e of c){ html += `<li>${e.start ? e.start.replace('T',' ') : ''} — ${e.title}</li>` } html += '</ul>'; el('calendar').innerHTML = html } }
async function updateHeadlines(){let h=await fetchJSON('/api/headlines'); if(h && h.length){ let html = '<ul>'; for(let i of h){ html += `<li>${i.title}</li>` } html += '</ul>'; el('headlines').innerHTML = html } }

// initial
updateTime(); updateWeather(); updateCalendar(); updateHeadlines();
// intervals
setInterval(updateTime,1000);
setInterval(updateWeather,30*1000);
setInterval(updateCalendar,60*1000);
setInterval(updateHeadlines,30*60*1000);
