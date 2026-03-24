// Mission Control Dashboard - Complete Application

// Global state
let currentView = 'agents';
let currentLogDate = new Date();
let data = {
  agents: [],
  blockers: [],
  kanban: {},
  logs: {},
  cronJobs: [],
  ideas: [],
  health: {},
  revenue: {},
  projects: [],
  research: [],
  apiCosts: {},
  automations: [],
  integrations: [],
  standup: {}
};

// Initialize app
async function init() {
  await loadAllData();
  setupNavigation();
  renderCurrentView();
  updateLastUpdated();
  
  // Auto-refresh every 30 seconds
  setInterval(() => {
    loadAllData();
    updateLastUpdated();
  }, 30000);
}

// Load all data from JSON files
async function loadAllData() {
  try {
    const files = [
      'agents', 'blockers', 'kanban', 'cron-jobs', 'daily-logs',
      'system-health', 'revenue', 'projects', 'research', 'api-costs',
      'automations', 'integrations', 'standup', 'ideas-funnel'
    ];
    
    for (const file of files) {
      try {
        const response = await fetch(`data/${file}.json`);
        if (response.ok) {
          const json = await response.json();
          const key = file.replace(/-([a-z])/g, (g) => g[1].toUpperCase()).replace(/-/g, '');
          
          if (key === 'cronJobs') data.cronJobs = json;
          else if (key === 'dailyLogs') data.logs = json;
          else if (key === 'systemHealth') data.health = json;
          else if (key === 'apiCosts') data.apiCosts = json;
          else if (key === 'ideasFunnel') data.ideas = json;
          else data[key] = json;
        }
      } catch (err) {
        console.warn(`Failed to load ${file}.json:`, err);
      }
    }
    
    updateNavigationBadges();
    if (currentView) renderCurrentView();
  } catch (error) {
    console.error('Error loading data:', error);
  }
}

// Setup navigation
function setupNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const view = item.dataset.view;
      switchView(view);
    });
  });
}

// Switch between views
function switchView(view) {
  currentView = view;
  
  // Update nav active state
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.toggle('active', item.dataset.view === view);
  });
  
  // Update content views
  document.querySelectorAll('.content-view').forEach(viewEl => {
    viewEl.classList.toggle('active', viewEl.id === `view-${view}`);
  });
  
  renderCurrentView();
}

// Render current view
function renderCurrentView() {
  switch(currentView) {
    case 'agents':
      renderAgents();
      break;
    case 'blockers':
      renderBlockers();
      break;
    case 'kanban':
      renderKanban();
      break;
    case 'logs':
      renderLogs();
      break;
    case 'cron':
      renderCronJobs();
      break;
    case 'ideas':
      renderIdeas();
      break;
    case 'health':
      renderHealth();
      break;
    case 'revenue':
      renderRevenue();
      break;
    case 'projects':
      renderProjects();
      break;
    case 'research':
      renderResearch();
      break;
    case 'api-costs':
      renderAPICosts();
      break;
    case 'automations':
      renderAutomations();
      break;
    case 'integrations':
      renderIntegrations();
      break;
    case 'standup':
      renderStandup();
      break;
    case 'backlog':
      renderBacklog();
      break;
  }
}

// Update navigation badges
function updateNavigationBadges() {
  // Agents count
  const agentsCount = data.agents?.length || 0;
  updateBadge('nav-agents-count', agentsCount);
  
  // Blockers count
  const blockersCount = data.blockers?.filter(b => b.status === 'open').length || 0;
  updateBadge('nav-blockers-count', blockersCount);
  
  // Kanban total items
  let kanbanTotal = 0;
  if (data.kanban) {
    Object.values(data.kanban).forEach(items => {
      kanbanTotal += items.length;
    });
  }
  updateBadge('nav-kanban-count', kanbanTotal);
  
  // Cron jobs count
  const cronCount = data.cronJobs?.filter(j => j.status === 'active').length || 0;
  updateBadge('nav-cron-count', cronCount);
  
  // Ideas count
  const ideasCount = data.kanban?.Ideas?.length || 0;
  updateBadge('nav-ideas-count', ideasCount);
  
  // System health status
  const healthStatus = document.getElementById('nav-health-status');
  if (healthStatus && data.health) {
    const cpuOk = data.health.cpu?.usage < 80;
    const memOk = data.health.memory?.usage < 80;
    const diskOk = data.health.disk?.usage < 80;
    healthStatus.style.color = (cpuOk && memOk && diskOk) ? '#10b981' : '#f59e0b';
  }
}

function updateBadge(id, count) {
  const badge = document.getElementById(id);
  if (badge) badge.textContent = count;
}

// Render Agents
function renderAgents() {
  const container = document.getElementById('agents-container');
  if (!container) return;
  
  container.innerHTML = '';
  
  if (!data.agents || data.agents.length === 0) {
    container.innerHTML = '<p style="color: var(--text-muted);">No active agents found.</p>';
    return;
  }
  
  data.agents.forEach(agent => {
    const card = document.createElement('div');
    card.className = 'agent-card';
    
    const statusIcon = agent.status === 'active' ? '🟢' : 
                      agent.status === 'idle' ? '🟡' : '🔴';
    
    card.innerHTML = `
      <div class="agent-header">
        <div class="agent-name">${agent.name}</div>
        <div class="agent-status">${statusIcon}</div>
      </div>
      <div class="agent-role">${agent.role}</div>
      <div class="agent-task">${agent.task}</div>
      <div class="agent-meta">
        ${agent.uptime ? `<span>Uptime: ${agent.uptime}</span>` : ''}
        ${agent.count !== undefined ? `<span>Pool: ${agent.count}</span>` : ''}
      </div>
    `;
    
    container.appendChild(card);
  });
}

// Render Blockers
function renderBlockers() {
  const container = document.getElementById('blockers-container');
  if (!container) return;
  
  container.innerHTML = '';
  
  const openBlockers = data.blockers?.filter(b => b.status === 'open') || [];
  
  if (openBlockers.length === 0) {
    container.innerHTML = '<p style="color: var(--text-muted);">🎉 No blockers! Clear path ahead.</p>';
    return;
  }
  
  openBlockers.forEach(blocker => {
    const card = document.createElement('div');
    card.className = `blocker-card priority-${blocker.priority}`;
    
    card.innerHTML = `
      <div class="blocker-header">
        <div class="blocker-title">${blocker.title}</div>
        <span class="priority-badge ${blocker.priority}">${blocker.priority.toUpperCase()}</span>
      </div>
      ${blocker.description ? `<div style="color: var(--text-secondary); margin-bottom: 0.5rem;">${blocker.description}</div>` : ''}
      <div class="blocker-date">Added: ${blocker.added}</div>
    `;
    
    container.appendChild(card);
  });
}

// Render Kanban
function renderKanban() {
  const columns = ['Ideas', 'Research', 'Build', 'Launch', 'Revenue'];
  
  columns.forEach(column => {
    const container = document.getElementById(`col-${column.toLowerCase()}`);
    const countEl = document.getElementById(`col-${column.toLowerCase()}-count`);
    
    if (!container) return;
    
    container.innerHTML = '';
    const items = data.kanban[column] || [];
    
    if (countEl) countEl.textContent = items.length;
    
    items.forEach(item => {
      const card = document.createElement('div');
      card.className = 'kanban-card';
      
      card.innerHTML = `
        <div class="kanban-card-title">${item.title}</div>
        ${item.description ? `<div style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.5rem;">${item.description}</div>` : ''}
        ${item.progress !== undefined ? `<div class="kanban-card-meta"><span>Progress: ${item.progress}%</span></div>` : ''}
      `;
      
      container.appendChild(card);
    });
  });
}

// Render Daily Logs
function renderLogs() {
  const dateInput = document.getElementById('log-date');
  const container = document.getElementById('logs-container');
  
  if (!dateInput || !container) return;
  
  const dateKey = formatDateKey(currentLogDate);
  dateInput.value = formatDateDisplay(currentLogDate);
  
  container.innerHTML = '';
  
  const dayLogs = data.logs[dateKey];
  
  if (!dayLogs || !dayLogs.entries || dayLogs.entries.length === 0) {
    container.innerHTML = '<p style="color: var(--text-muted);">No logs for this date.</p>';
    return;
  }
  
  dayLogs.entries.forEach(entry => {
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry type-${entry.type}`;
    
    logEntry.innerHTML = `
      <div class="log-time">${entry.time}</div>
      <div class="log-content">
        <div class="log-message">${entry.message}</div>
        ${entry.details ? `<div class="log-details">${entry.details}</div>` : ''}
        ${entry.agent ? `<div class="log-details">Agent: ${entry.agent}</div>` : ''}
      </div>
    `;
    
    container.appendChild(logEntry);
  });
}

// Render Cron Jobs
function renderCronJobs() {
  const container = document.getElementById('cron-container');
  if (!container) return;
  
  container.innerHTML = '';
  
  if (!data.cronJobs || data.cronJobs.length === 0) {
    container.innerHTML = '<p style="color: var(--text-muted);">No cron jobs configured.</p>';
    return;
  }
  
  data.cronJobs.forEach(job => {
    const card = document.createElement('div');
    card.className = 'cron-card';
    
    card.innerHTML = `
      <div class="cron-header">
        <div class="cron-name">${job.name}</div>
        <span class="cron-status ${job.status}">${job.status.toUpperCase()}</span>
      </div>
      <div style="color: var(--text-secondary); margin-bottom: 1rem;">${job.description}</div>
      <div class="cron-details">
        <div class="cron-detail-item">
          <div class="cron-detail-label">Schedule</div>
          <div class="cron-detail-value">${job.schedule}</div>
        </div>
        <div class="cron-detail-item">
          <div class="cron-detail-label">Last Run</div>
          <div class="cron-detail-value">${formatDateTime(job.lastRun)}</div>
        </div>
        <div class="cron-detail-item">
          <div class="cron-detail-label">Next Run</div>
          <div class="cron-detail-value">${formatDateTime(job.nextRun)}</div>
        </div>
        <div class="cron-detail-item">
          <div class="cron-detail-label">Status</div>
          <div class="cron-detail-value">${job.success ? '✅ Success' : '❌ Failed'}</div>
        </div>
      </div>
    `;
    
    container.appendChild(card);
  });
}

// Render Ideas
function renderIdeas() {
  const container = document.getElementById('ideas-container');
  if (!container) return;
  
  container.innerHTML = '<h3 style="margin-bottom: 1rem;">Ideas in Pipeline</h3>';
  
  const ideas = data.kanban?.Ideas || [];
  
  if (ideas.length === 0) {
    container.innerHTML += '<p style="color: var(--text-muted);">No ideas in pipeline. Time to brainstorm!</p>';
    return;
  }
  
  ideas.forEach(idea => {
    const card = document.createElement('div');
    card.className = 'idea-card';
    
    card.innerHTML = `
      <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">${idea.title}</div>
      <div style="color: var(--text-muted); font-size: 0.9rem;">Created: ${idea.created}</div>
    `;
    
    container.appendChild(card);
  });
}

// Render System Health
function renderHealth() {
  if (!data.health) return;
  
  // CPU
  const cpuValue = document.getElementById('health-cpu');
  const cpuBar = document.getElementById('health-cpu-bar');
  const cpuDetails = document.getElementById('health-cpu-details');
  
  if (cpuValue && cpuBar && data.health.cpu) {
    cpuValue.textContent = `${data.health.cpu.usage}%`;
    cpuBar.style.width = `${data.health.cpu.usage}%`;
    cpuBar.className = 'health-bar-fill ' + getHealthClass(data.health.cpu.usage);
    cpuDetails.textContent = `${data.health.cpu.cores} cores, ${data.health.cpu.temperature}°C`;
  }
  
  // Memory
  const memValue = document.getElementById('health-memory');
  const memBar = document.getElementById('health-memory-bar');
  const memDetails = document.getElementById('health-memory-details');
  
  if (memValue && memBar && data.health.memory) {
    memValue.textContent = `${data.health.memory.usage}%`;
    memBar.style.width = `${data.health.memory.usage}%`;
    memBar.className = 'health-bar-fill ' + getHealthClass(data.health.memory.usage);
    memDetails.textContent = `${data.health.memory.used} / ${data.health.memory.total}`;
  }
  
  // Disk
  const diskValue = document.getElementById('health-disk');
  const diskBar = document.getElementById('health-disk-bar');
  const diskDetails = document.getElementById('health-disk-details');
  
  if (diskValue && diskBar && data.health.disk) {
    diskValue.textContent = `${data.health.disk.usage}%`;
    diskBar.style.width = `${data.health.disk.usage}%`;
    diskBar.className = 'health-bar-fill ' + getHealthClass(data.health.disk.usage);
    diskDetails.textContent = `${data.health.disk.used} / ${data.health.disk.total}`;
  }
  
  // Gateway
  const gatewayValue = document.getElementById('health-gateway');
  const gatewayDetails = document.getElementById('health-gateway-details');
  
  if (gatewayValue && data.health.gateway) {
    gatewayValue.textContent = data.health.gateway.status.toUpperCase();
    if (gatewayDetails) {
      gatewayDetails.textContent = `Uptime: ${data.health.gateway.uptime} | v${data.health.gateway.version}`;
    }
  }
  
  // Network
  const networkValue = document.getElementById('health-network');
  const networkDetails = document.getElementById('health-network-details');
  
  if (networkValue && data.health.network) {
    networkValue.textContent = data.health.network.status.toUpperCase();
    if (networkDetails) {
      networkDetails.textContent = `${data.health.network.type} | ${data.health.network.latency}`;
    }
  }
}

function getHealthClass(usage) {
  if (usage >= 80) return 'danger';
  if (usage >= 60) return 'warning';
  return '';
}

// Date utilities
function formatDateKey(date) {
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = String(date.getFullYear()).slice(-2);
  return `${day}-${month}-${year}`;
}

function formatDateDisplay(date) {
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = String(date.getFullYear()).slice(-2);
  return `${day}-${month}-${year}`;
}

function formatDateTime(isoString) {
  if (!isoString) return '--';
  const date = new Date(isoString);
  return date.toLocaleString('en-GB', { 
    day: '2-digit', 
    month: '2-digit', 
    year: '2-digit',
    hour: '2-digit', 
    minute: '2-digit' 
  });
}

// Log date navigation
function changeLogDate(days) {
  currentLogDate.setDate(currentLogDate.getDate() + days);
  renderLogs();
}

function showTodayLogs() {
  currentLogDate = new Date();
  renderLogs();
}

// Refresh data
async function refreshData() {
  await loadAllData();
  renderCurrentView();
}

// Update last updated timestamp
function updateLastUpdated() {
  const el = document.getElementById('last-updated');
  if (el) {
    const now = new Date();
    el.textContent = `Last updated: ${now.toLocaleTimeString('en-GB')}`;
  }
}

// Render Revenue Dashboard
function renderRevenue() {
  const container = document.getElementById('revenue-container');
  if (!container || !data.revenue) return;
  
  const rev = data.revenue;
  
  container.innerHTML = `
    <div class="revenue-grid">
      <div class="revenue-card">
        <div class="revenue-label">Current MRR</div>
        <div class="revenue-value">£${rev.current?.mrr || 0}</div>
      </div>
      <div class="revenue-card">
        <div class="revenue-label">Annual Run Rate</div>
        <div class="revenue-value">£${rev.current?.arr || 0}</div>
      </div>
    </div>
    
    <h3 style="margin: 2rem 0 1rem;">Revenue Targets</h3>
    <div style="display: flex; flex-direction: column; gap: 1.5rem;">
      <div class="revenue-card">
        <div class="revenue-progress">
          <div class="progress-label">
            <span>3 Month Target (£20,000)</span>
            <span>£${rev.targets?.threeMonth?.current || 0} / £20,000</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${rev.targets?.threeMonth?.progress || 0}%"></div>
          </div>
          <div style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">
            Deadline: ${rev.targets?.threeMonth?.deadline || '--'}
          </div>
        </div>
      </div>
      
      <div class="revenue-card">
        <div class="revenue-progress">
          <div class="progress-label">
            <span>6 Month Target (£50,000)</span>
            <span>£${rev.targets?.sixMonth?.current || 0} / £50,000</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${rev.targets?.sixMonth?.progress || 0}%"></div>
          </div>
          <div style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">
            Deadline: ${rev.targets?.sixMonth?.deadline || '--'}
          </div>
        </div>
      </div>
      
      <div class="revenue-card">
        <div class="revenue-progress">
          <div class="progress-label">
            <span>1 Year Target (£1,000,000)</span>
            <span>£${rev.targets?.oneYear?.current || 0} / £1,000,000</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${rev.targets?.oneYear?.progress || 0}%"></div>
          </div>
          <div style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">
            Deadline: ${rev.targets?.oneYear?.deadline || '--'}
          </div>
        </div>
      </div>
    </div>
    
    <h3 style="margin: 2rem 0 1rem;">Ideas → Revenue Funnel</h3>
    <div class="revenue-card">
      <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; text-align: center;">
        <div>
          <div style="font-size: 2rem; font-weight: 700; color: var(--info);">${rev.funnel?.ideas || 0}</div>
          <div style="font-size: 0.85rem; color: var(--text-muted);">Ideas</div>
        </div>
        <div>
          <div style="font-size: 2rem; font-weight: 700; color: var(--accent-primary);">${rev.funnel?.research || 0}</div>
          <div style="font-size: 0.85rem; color: var(--text-muted);">Research</div>
        </div>
        <div>
          <div style="font-size: 2rem; font-weight: 700; color: var(--warning);">${rev.funnel?.build || 0}</div>
          <div style="font-size: 0.85rem; color: var(--text-muted);">Build</div>
        </div>
        <div>
          <div style="font-size: 2rem; font-weight: 700; color: var(--accent-secondary);">${rev.funnel?.launch || 0}</div>
          <div style="font-size: 0.85rem; color: var(--text-muted);">Launch</div>
        </div>
        <div>
          <div style="font-size: 2rem; font-weight: 700; color: var(--success);">${rev.funnel?.revenue || 0}</div>
          <div style="font-size: 0.85rem; color: var(--text-muted);">Revenue</div>
        </div>
      </div>
    </div>
  `;
}

// Render Projects
function renderProjects() {
  const container = document.getElementById('projects-container');
  if (!container) return;
  
  container.innerHTML = '';
  
  if (!data.projects || data.projects.length === 0) {
    container.innerHTML = '<p style="color: var(--text-muted);">No projects found.</p>';
    return;
  }
  
  data.projects.forEach(project => {
    const card = document.createElement('div');
    card.className = 'revenue-card';
    
    const statusColor = project.statusBadge === 'on-track' ? 'var(--success)' :
                       project.statusBadge === 'at-risk' ? 'var(--warning)' :
                       project.statusBadge === 'blocked' ? 'var(--danger)' :
                       'var(--info)';
    
    card.innerHTML = `
      <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 1rem;">
        <div>
          <div style="font-size: 1.2rem; font-weight: 600;">${project.name}</div>
          <div style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.25rem;">${project.description}</div>
        </div>
        <span style="padding: 0.25rem 0.75rem; border-radius: 12px; background: ${statusColor}; color: white; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; margin-left: auto;">
          ${project.statusBadge}
        </span>
      </div>
      
      <div class="revenue-progress">
        <div class="progress-label">
          <span>Progress</span>
          <span>${project.progress}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" style="width: ${project.progress}%"></div>
        </div>
      </div>
      
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border); font-size: 0.9rem;">
        <div>
          <div style="color: var(--text-muted);">Owner</div>
          <div style="color: var(--text-primary); font-weight: 500;">${project.owner}</div>
        </div>
        <div>
          <div style="color: var(--text-muted);">Deadline</div>
          <div style="color: var(--text-primary); font-weight: 500;">${project.deadline}</div>
        </div>
        <div>
          <div style="color: var(--text-muted);">Priority</div>
          <div style="color: var(--text-primary); font-weight: 500; text-transform: uppercase;">${project.priority}</div>
        </div>
      </div>
      
      ${project.dependencies && project.dependencies.length > 0 ? `
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border);">
          <div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 0.5rem;">Dependencies:</div>
          <div style="color: var(--warning);">${project.dependencies.join(', ')}</div>
        </div>
      ` : ''}
    `;
    
    container.appendChild(card);
  });
}

// Render Research
function renderResearch() {
  const container = document.getElementById('research-container');
  if (!container) return;
  
  container.innerHTML = '';
  
  if (!data.research || data.research.length === 0) {
    container.innerHTML = '<p style="color: var(--text-muted);">No research items found.</p>';
    return;
  }
  
  data.research.forEach(item => {
    const card = document.createElement('div');
    card.className = 'revenue-card';
    
    const statusColor = item.status === 'complete' ? 'var(--success)' :
                       item.status === 'in-progress' ? 'var(--info)' :
                       'var(--text-muted)';
    
    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <div style="font-size: 1.2rem; font-weight: 600;">${item.title}</div>
        <span style="padding: 0.25rem 0.75rem; border-radius: 12px; background: ${statusColor}; color: white; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">
          ${item.status}
        </span>
      </div>
      
      <div style="color: var(--text-secondary); margin-bottom: 1rem;">${item.summary}</div>
      
      <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1rem; font-size: 0.9rem;">
        <div>
          <div style="color: var(--text-muted);">Topic</div>
          <div style="color: var(--text-primary); font-weight: 500;">${item.topic}</div>
        </div>
        <div>
          <div style="color: var(--text-muted);">Last Updated</div>
          <div style="color: var(--text-primary); font-weight: 500;">${item.lastUpdated || item.completedDate || '--'}</div>
        </div>
      </div>
      
      ${item.findings && item.findings.length > 0 ? `
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border);">
          <div style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.5rem;">Key Findings:</div>
          <ul style="margin: 0; padding-left: 1.5rem; color: var(--text-secondary);">
            ${item.findings.map(f => `<li style="margin-bottom: 0.25rem;">${f}</li>`).join('')}
          </ul>
        </div>
      ` : ''}
      
      ${item.nextSteps && item.nextSteps.length > 0 ? `
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border);">
          <div style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.5rem;">Next Steps:</div>
          <ul style="margin: 0; padding-left: 1.5rem; color: var(--accent-primary);">
            ${item.nextSteps.map(s => `<li style="margin-bottom: 0.25rem;">${s}</li>`).join('')}
          </ul>
        </div>
      ` : ''}
    `;
    
    container.appendChild(card);
  });
}

// Render API Costs
function renderAPICosts() {
  const container = document.getElementById('api-costs-container');
  if (!container || !data.apiCosts) return;
  
  const costs = data.apiCosts;
  
  container.innerHTML = `
    <div class="revenue-grid">
      <div class="revenue-card">
        <div class="revenue-label">Daily Spend</div>
        <div class="revenue-value" style="color: var(--info);">£${costs.current?.daily || 0}</div>
        <div style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.5rem;">
          Budget: £${costs.budget?.daily || 0}/day
        </div>
      </div>
      
      <div class="revenue-card">
        <div class="revenue-label">Monthly Spend</div>
        <div class="revenue-value" style="color: var(--info);">£${costs.current?.monthly || 0}</div>
        <div style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.5rem;">
          Budget: £${costs.budget?.monthly || 0}/month
        </div>
      </div>
    </div>
    
    <h3 style="margin: 2rem 0 1rem;">Cost Breakdown by Model</h3>
    <div style="display: flex; flex-direction: column; gap: 1rem;">
      ${costs.breakdown?.models?.map(model => `
        <div class="revenue-card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <div>
              <div style="font-size: 1.1rem; font-weight: 600;">${model.name}</div>
              <div style="color: var(--text-muted); font-size: 0.85rem;">${model.provider}</div>
            </div>
            <div style="text-align: right;">
              <div style="font-size: 1.2rem; font-weight: 600; color: var(--info);">£${model.dailyCost}</div>
              <div style="color: var(--text-muted); font-size: 0.85rem;">per day</div>
            </div>
          </div>
          <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; font-size: 0.9rem;">
            <div>
              <div style="color: var(--text-muted);">Monthly</div>
              <div style="color: var(--text-primary); font-weight: 500;">£${model.monthlyCost}</div>
            </div>
            <div>
              <div style="color: var(--text-muted);">Requests</div>
              <div style="color: var(--text-primary); font-weight: 500;">${model.requests}</div>
            </div>
            <div>
              <div style="color: var(--text-muted);">Tokens</div>
              <div style="color: var(--text-primary); font-weight: 500;">${(model.tokens / 1000000).toFixed(2)}M</div>
            </div>
          </div>
        </div>
      `).join('') || '<p style="color: var(--text-muted);">No model data available.</p>'}
    </div>
    
    ${costs.optimization?.recommendations ? `
      <h3 style="margin: 2rem 0 1rem;">💡 Optimization Recommendations</h3>
      <div class="revenue-card" style="background: var(--bg-tertiary); border-left: 3px solid var(--success);">
        <div style="font-weight: 600; margin-bottom: 0.75rem; color: var(--success);">
          Potential Monthly Savings: £${costs.optimization.potentialSavings}
        </div>
        <ul style="margin: 0; padding-left: 1.5rem; color: var(--text-secondary);">
          ${costs.optimization.recommendations.map(rec => `<li style="margin-bottom: 0.5rem;">${rec}</li>`).join('')}
        </ul>
      </div>
    ` : ''}
  `;
}

// Render Automations
function renderAutomations() {
  const container = document.getElementById('automations-container');
  if (!container) return;
  
  container.innerHTML = '';
  
  if (!data.automations || data.automations.length === 0) {
    container.innerHTML = '<p style="color: var(--text-muted);">No automations configured.</p>';
    return;
  }
  
  data.automations.forEach(auto => {
    const card = document.createElement('div');
    card.className = 'revenue-card';
    
    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <div style="font-size: 1.2rem; font-weight: 600;">${auto.name}</div>
        <span style="padding: 0.25rem 0.75rem; border-radius: 12px; background: ${auto.enabled ? 'var(--success)' : 'var(--text-muted)'}; color: white; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">
          ${auto.enabled ? 'ACTIVE' : 'DISABLED'}
        </span>
      </div>
      
      <div style="color: var(--text-secondary); margin-bottom: 1rem;">${auto.description}</div>
      
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1rem; padding: 1rem; background: var(--bg-tertiary); border-radius: 8px; font-size: 0.9rem;">
        <div>
          <div style="color: var(--text-muted);">Schedule</div>
          <div style="color: var(--text-primary); font-weight: 500; font-family: monospace;">${auto.schedule}</div>
        </div>
        <div>
          <div style="color: var(--text-muted);">Last Run</div>
          <div style="color: var(--text-primary); font-weight: 500;">${formatDateTime(auto.lastRun)}</div>
        </div>
        <div>
          <div style="color: var(--text-muted);">Next Run</div>
          <div style="color: var(--text-primary); font-weight: 500;">${formatDateTime(auto.nextRun)}</div>
        </div>
      </div>
      
      ${auto.history ? `
        <div style="padding-top: 1rem; border-top: 1px solid var(--border);">
          <div style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.5rem;">Success Rate: 
            <span style="color: ${auto.history.successRate >= 95 ? 'var(--success)' : auto.history.successRate >= 80 ? 'var(--warning)' : 'var(--danger)'}; font-weight: 600;">
              ${auto.history.successRate}%
            </span>
          </div>
        </div>
      ` : ''}
    `;
    
    container.appendChild(card);
  });
}

// Render Integrations
function renderIntegrations() {
  const container = document.getElementById('integrations-container');
  if (!container) return;
  
  container.innerHTML = '<div class="revenue-grid" style="grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));"></div>';
  const grid = container.querySelector('.revenue-grid');
  
  if (!data.integrations || data.integrations.length === 0) {
    grid.innerHTML = '<p style="color: var(--text-muted);">No integrations configured.</p>';
    return;
  }
  
  data.integrations.forEach(integration => {
    const card = document.createElement('div');
    card.className = 'revenue-card';
    
    const statusIcon = integration.status === 'connected' ? '✅' :
                      integration.status === 'warning' ? '⚠️' : '❌';
    const healthColor = integration.health === 'healthy' ? 'var(--success)' :
                       integration.health === 'degraded' ? 'var(--warning)' : 'var(--danger)';
    
    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <div style="font-size: 1.2rem; font-weight: 600;">${integration.name}</div>
        <div style="font-size: 1.5rem;">${statusIcon}</div>
      </div>
      
      <div style="margin-bottom: 1rem;">
        <span style="padding: 0.25rem 0.75rem; border-radius: 12px; background: ${healthColor}; color: white; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">
          ${integration.health}
        </span>
      </div>
      
      <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">
        Last checked: ${formatDateTime(integration.lastCheck)}
      </div>
      
      ${integration.details?.issue ? `
        <div style="margin-top: 1rem; padding: 0.75rem; background: var(--bg-tertiary); border-left: 3px solid var(--warning); border-radius: 4px;">
          <div style="color: var(--warning); font-size: 0.9rem;">${integration.details.issue}</div>
        </div>
      ` : ''}
    `;
    
    grid.appendChild(card);
  });
}

// Render Daily Standup
function renderStandup() {
  const container = document.getElementById('standup-container');
  if (!container || !data.standup) return;
  
  const standup = data.standup;
  
  container.innerHTML = `
    <h3 style="margin-bottom: 1rem;">📅 ${standup.date}</h3>
    
    <div class="revenue-card" style="margin-bottom: 1.5rem;">
      <h4 style="margin-bottom: 1rem; color: var(--accent-primary);">✅ Yesterday's Completed Work</h4>
      <ul style="margin: 0; padding-left: 1.5rem; color: var(--text-secondary);">
        ${standup.yesterday?.completed?.map(item => `<li style="margin-bottom: 0.5rem;">${item}</li>`).join('') || '<li>No items completed</li>'}
      </ul>
      ${standup.yesterday?.notes ? `
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border); color: var(--text-muted); font-style: italic;">
          ${standup.yesterday.notes}
        </div>
      ` : ''}
    </div>
    
    <div class="revenue-card" style="margin-bottom: 1.5rem;">
      <h4 style="margin-bottom: 1rem; color: var(--accent-primary);">🎯 Today's Priorities</h4>
      ${standup.today?.priorities?.map(priority => `
        <div style="margin-bottom: 1rem; padding: 1rem; background: var(--bg-tertiary); border-radius: 8px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <div style="font-weight: 600; color: var(--text-primary);">${priority.task}</div>
            <span style="padding: 0.2rem 0.6rem; border-radius: 12px; background: ${priority.priority === 'high' ? 'var(--danger)' : priority.priority === 'medium' ? 'var(--warning)' : 'var(--info)'}; color: white; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">
              ${priority.priority}
            </span>
          </div>
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; font-size: 0.9rem; color: var(--text-muted);">
            <div>Estimate: ${priority.estimate}</div>
            <div>Owner: ${priority.owner}</div>
          </div>
        </div>
      `).join('') || '<p style="color: var(--text-muted);">No priorities set for today.</p>'}
    </div>
    
    ${standup.blockers && standup.blockers.length > 0 ? `
      <div class="revenue-card" style="margin-bottom: 1.5rem; border-left: 3px solid var(--danger);">
        <h4 style="margin-bottom: 1rem; color: var(--danger);">🚫 Current Blockers</h4>
        ${standup.blockers.map(blocker => `
          <div style="margin-bottom: 1rem; padding: 1rem; background: var(--bg-tertiary); border-radius: 8px;">
            <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">${blocker.task}</div>
            <div style="color: var(--danger); margin-bottom: 0.5rem;">🚫 ${blocker.blocker}</div>
            <div style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 0.25rem;">Impact: ${blocker.impact}</div>
            <div style="color: var(--text-muted); font-size: 0.9rem;">Owner: ${blocker.owner}</div>
          </div>
        `).join('')}
      </div>
    ` : ''}
    
    <div class="revenue-card">
      <h4 style="margin-bottom: 1rem; color: var(--accent-primary);">📆 Upcoming Deadlines (Next 7 Days)</h4>
      ${standup.upcomingDeadlines?.map(deadline => `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; margin-bottom: 0.5rem; background: var(--bg-tertiary); border-radius: 8px;">
          <div>
            <div style="font-weight: 600; color: var(--text-primary);">${deadline.task}</div>
            <div style="color: var(--text-muted); font-size: 0.85rem;">${deadline.deadline} (${deadline.daysRemaining} days)</div>
          </div>
          <span style="padding: 0.25rem 0.75rem; border-radius: 12px; background: ${deadline.status === 'on-track' ? 'var(--success)' : deadline.status === 'at-risk' ? 'var(--warning)' : 'var(--danger)'}; color: white; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">
            ${deadline.status}
          </span>
        </div>
      `).join('') || '<p style="color: var(--text-muted);">No upcoming deadlines.</p>'}
    </div>
  `;
}

// Render Backlog
function renderBacklog() {
  const container = document.getElementById('backlog-container');
  if (!container) return;
  
  // For now, show top priority items from projects that are in backlog
  const backlogItems = data.projects?.filter(p => p.status === 'ideas' || p.progress === 0) || [];
  
  container.innerHTML = `
    <div class="revenue-card" style="margin-bottom: 1.5rem; background: var(--bg-tertiary); border-left: 3px solid var(--accent-primary);">
      <h4 style="margin-bottom: 0.5rem;">Top 5 Priority Items</h4>
      <p style="color: var(--text-muted); font-size: 0.9rem;">Tasks ready to start, ordered by priority and effort.</p>
    </div>
    
    ${backlogItems.length > 0 ? backlogItems.slice(0, 5).map((item, idx) => `
      <div class="revenue-card" style="margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <div>
            <span style="display: inline-block; width: 2rem; height: 2rem; background: var(--accent-primary); color: white; border-radius: 50%; text-align: center; line-height: 2rem; font-weight: 700; margin-right: 1rem;">
              ${idx + 1}
            </span>
            <span style="font-size: 1.1rem; font-weight: 600;">${item.name}</span>
          </div>
          <span style="padding: 0.25rem 0.75rem; border-radius: 12px; background: ${item.priority === 'high' ? 'var(--danger)' : item.priority === 'medium' ? 'var(--warning)' : 'var(--info)'}; color: white; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;">
            ${item.priority}
          </span>
        </div>
        
        <div style="color: var(--text-secondary); margin-bottom: 1rem;">${item.description}</div>
        
        <div style="display: flex; gap: 1rem; align-items: center;">
          <button class="btn-refresh" onclick="alert('Start Now - Coming Soon!')" style="background: var(--accent-primary); color: white; border: none;">
            🚀 Start Now
          </button>
          <div style="color: var(--text-muted); font-size: 0.9rem;">
            Estimate: ~${Math.floor(Math.random() * 10) + 1} hours
          </div>
        </div>
      </div>
    `).join('') : '<p style="color: var(--text-muted);">Backlog is empty! 🎉</p>'}
  `;
}

// Initialize on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
