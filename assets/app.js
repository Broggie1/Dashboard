
async function loadJson(path, fallback) {
  try {
    const res = await fetch(path, { cache: 'no-store' });
    if (!res.ok) throw new Error('bad response');
    return await res.json();
  } catch {
    return fallback;
  }
}
function nav(active) {
  const items = [
    ['index.html','Overview'],
    ['mission-control.html','Mission Control'],
    ['agents.html','Agents'],
    ['projects.html','Projects'],
    ['daily-logs.html','Daily logs'],
    ['revenue.html','Revenue'],
    ['governance.html','Governance'],
    ['pipeline.html','Pipeline'],
    ['blockers.html','Blockers'],
    ['links.html','Links']
  ];
  return items.map(([href,label]) => `<a href="${href}" class="${active===href?'active':''}">${label}</a>`).join('');
}
function shell({active, title='Control', subtitle='Shared Mission Control views for Niall.', foot='GitHub Pages, repo-backed data where appropriate.'}, content) {
  return `
  <div class="layout">
    <aside class="sidebar">
      <div class="brand">
        <div class="eyebrow">Mission Control • Niall</div>
        <h1>${title}</h1>
        <p>${subtitle}</p>
      </div>
      <nav class="nav">${nav(active)}</nav>
      <div class="sidebar-foot">${foot}</div>
    </aside>
    <main class="wrap">${content}<div class="footer">Mission Control, GitHub Pages deployment, built for Niall.</div></main>
  </div>`;
}
function tickClock() {
  const clock = document.getElementById('clock');
  if (!clock) return;
  function tick() {
    clock.textContent = new Date().toLocaleString('en-GB', { weekday:'short', year:'numeric', month:'short', day:'numeric', hour:'2-digit', minute:'2-digit', second:'2-digit' });
  }
  tick(); setInterval(tick, 1000);
}
function esc(v) { return String(v ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;'); }
window.MissionControl = { loadJson, shell, tickClock, esc };
