// Mission Control Dashboard - Data embedded (no fetch needed)

// Embedded data (update these directly)
const kanbanData = {
  Ideas: [
    'AI Money-Making Research',
    'Passive Income Research'
  ],
  Research: [
    'KGB Financial Quiz (100% complete)'
  ],
  Build: [],
  Launch: [
    'Mission Control',
    'TaxReady'
  ],
  Revenue: []
};

const blockersData = [
  { title: 'Discord token update', priority: 'High', date: '2026-03-21' }
];

const agentsData = [
  { name: 'Lancelot (Coordinator)', status: '🟢', task: 'Active - Managing projects' },
  { name: 'Sub-agents', status: '🟡', task: 'Idle - Awaiting tasks' }
];

const systemHealthData = {
  cpu: 35,
  memory: 42,
  disk: 18,
  gateway: 'Running'
};

// Render functions
function createAgentCard(agent) {
  const div = document.createElement('div');
  div.className = 'card agent-card';
  div.innerHTML = `
    <div class="agent-name">${agent.name}</div>
    <div class="agent-status">${agent.status} ${agent.task}</div>
  `;
  return div;
}

function createBlockerCard(blocker) {
  const div = document.createElement('div');
  div.className = `card blocker-card priority-${blocker.priority.toLowerCase()}`;
  div.innerHTML = `
    <div class="blocker-title">${blocker.title}</div>
    <div class="blocker-meta">
      <span class="priority-badge">${blocker.priority}</span>
      <span class="blocker-date">${blocker.date}</span>
    </div>
  `;
  return div;
}

function createKanbanCard(text) {
  const div = document.createElement('div');
  div.className = 'kanban-card';
  div.textContent = text;
  return div;
}

function renderAgents() {
  const container = document.getElementById('agents-cards');
  if (!container) return;
  container.innerHTML = '';
  agentsData.forEach(agent => {
    container.appendChild(createAgentCard(agent));
  });
  document.getElementById('agents-count').textContent = agentsData.length;
}

function renderBlockers() {
  const container = document.getElementById('blockers-cards');
  if (!container) return;
  container.innerHTML = '';
  blockersData.forEach(blocker => {
    container.appendChild(createBlockerCard(blocker));
  });
  document.getElementById('blockers-count').textContent = blockersData.length;
}

function renderKanban() {
  Object.keys(kanbanData).forEach(column => {
    const container = document.querySelector(`[data-column="${column}"] .kanban-cards-list`);
    if (!container) return;
    container.innerHTML = '';
    kanbanData[column].forEach(item => {
      container.appendChild(createKanbanCard(item));
    });
    const countEl = document.getElementById(`count-${column.toLowerCase()}`);
    if (countEl) {
      countEl.textContent = kanbanData[column].length;
    }
  });
}

function renderSystemHealth() {
  const cpuEl = document.getElementById('cpu-usage');
  const memEl = document.getElementById('memory-usage');
  const diskEl = document.getElementById('disk-usage');
  const gatewayEl = document.getElementById('gateway-status');
  
  if (cpuEl) {
    cpuEl.textContent = `${systemHealthData.cpu}%`;
    const cpuBar = document.getElementById('cpu-bar');
    if (cpuBar) cpuBar.style.width = `${systemHealthData.cpu}%`;
  }
  
  if (memEl) {
    memEl.textContent = `${systemHealthData.memory}%`;
    const memBar = document.getElementById('memory-bar');
    if (memBar) memBar.style.width = `${systemHealthData.memory}%`;
  }
  
  if (diskEl) {
    diskEl.textContent = `${systemHealthData.disk}%`;
    const diskBar = document.getElementById('disk-bar');
    if (diskBar) diskBar.style.width = `${systemHealthData.disk}%`;
  }
  
  if (gatewayEl) {
    gatewayEl.textContent = systemHealthData.gateway;
  }
}

function updateLastUpdated() {
  const el = document.getElementById('last-updated');
  if (el) {
    const now = new Date();
    el.textContent = `Last updated: ${now.toLocaleTimeString()}`;
  }
}

function init() {
  renderAgents();
  renderBlockers();
  renderKanban();
  renderSystemHealth();
  updateLastUpdated();
  
  // Auto-refresh every 30 seconds
  setInterval(() => {
    updateLastUpdated();
  }, 30000);
  
  // Fade-in animation
  document.body.classList.add('loaded');
}

// Run on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
