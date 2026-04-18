from pathlib import Path
import json, re
from datetime import datetime, timezone

ROOT = Path('/Users/sirlancelot/.openclaw/workspace')
DASH = ROOT / 'Dashboard'
DATA = DASH / 'data'
DATA.mkdir(exist_ok=True)


def read(path, default=''):
    try:
        return Path(path).read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        # print(f'Error reading {path}: {e}') # Suppress print for cleaner output
        return default

def write_json(path, data):
    try:
        path.write_text(json.dumps(data, indent=2), encoding='utf-8')
        # print(f'Successfully wrote to {path}') # Suppress print for cleaner output
    except Exception as e:
        # print(f'Error writing to {path}: {e}') # Suppress print for cleaner output
        pass


def extract_bullets(section_text):
    bullets = []
    for line in section_text.splitlines():
        s = line.strip()
        if s.startswith('- ') or s.startswith('* '):
            bullets.append(s[2:].strip())
    return bullets

def section(md, header):
    parts = re.split(r'^##\s+', md, flags=re.M)
    for p in parts:
        if p.startswith(header):
            return p.split('\n', 1)[1] if '\n' in p else ''
    return ''

# --- KANBAN Data Processing ---
kanban_md_content = read(ROOT / 'KANBAN.md')
kanban_board_items = {
    'backlog': [],
    'inProgress': [],
    'inReview': [],
    'completed': [],
    'blocked': []
}
headers = ['📋 Backlog', '🔄 In Progress', '👀 In Review', '✅ Completed', '🚫 Blocked']
keys = ['backlog', 'inProgress', 'inReview', 'completed', 'blocked']

for hdr, key in zip(headers, keys):
    match = re.search(rf'##\s+{re.escape(hdr)}(.*?)(?=^##\s+|\Z)', kanban_md_content, flags=re.S | re.M)
    if not match:
        continue
    block_content = match.group(1)
    for line in block_content.splitlines():
        s = line.strip()
        if s.startswith('- [ ] '):
            title = s[6:].strip()
            kanban_board_items[key].append({
                'id': f'{key}-{len(kanban_board_items[key])+1}',
                'title': title,
                'description': 'Imported from KANBAN.md',
                'priority': 'medium' if key in ('inProgress','blocked') else 'low',
                'created': datetime.now().date().isoformat(),
                'category': 'KANBAN'
            })
        elif s.startswith('- **') and '**' in s[4:]:
            title = re.sub(r'\*\*', '', s[2:]).strip()
            kanban_board_items[key].append({
                'id': f'{key}-{len(kanban_board_items[key])+1}',
                'title': title,
                'description': 'Imported from KANBAN.md',
                'priority': 'medium',
                'created': datetime.now().date().isoformat(),
                'category': 'KANBAN'
            })

# --- Load Existing Data and Merge ---
existing_board_content = read(DATA / 'operating-board.json')
merged_board = json.loads(existing_board_content) if existing_board_content else {
    'backlog': [], 'inProgress': [], 'inReview': [], 'completed': [], 'blocked': []
}

# Merge KANBAN items, avoiding duplicates based on title
for key in keys:
    for kanban_item in kanban_board_items[key]:
        if not any(x['title'] == kanban_item['title'] for x in merged_board[key]):
            merged_board[key].append(kanban_item)

# --- Add/Update Specific Manual Backlog Items & Launch Priorities ---
# These are items explicitly added or updated through conversation
manual_and_launch_items = {
    'backlog': [
        {'id': 'op-backlog-1', 'title': '5-model 24/7 debating R&D team', 'description': 'Captured for later phase, once product launches are live and revenue validation is underway.', 'priority': 'low', 'created': datetime.now().date().isoformat(), 'category': 'Strategy'},
        {'id': 'op-backlog-2', 'title': 'Daily microapp factory', 'description': 'Useful later, but not before the current product launch path ships.', 'priority': 'low', 'created': datetime.now().date().isoformat(), 'category': 'Innovation'},
        {'id': 'op-backlog-3', 'title': 'Expanded prompt-driven capability programme', 'description': 'Captured for later phase when core product sales flow is live and stable.', 'priority': 'low', 'created': datetime.now().date().isoformat(), 'category': 'Capability'},
        {'id': 'op-backlog-4', 'title': 'n8n revenue workflow implementation', 'description': 'Stage n8n adoption properly, Phase 1 should focus on Launch Sequence Manager, Income Event Logger, and Product Demand Validator once live product execution needs automation support.', 'priority': 'medium', 'created': datetime.now().date().isoformat(), 'category': 'Automation'},
        {'id': 'op-backlog-5', 'title': 'Dashboard Data Generation & Linking', 'description': 'Auto-generate dashboard data (operating-board.json, agents.json, etc.) from workspace state. Link project launch tasks to the operating board.', 'priority': 'high', 'created': datetime.now().date().isoformat(), 'category': 'Dashboard'},
        {'id': 'op-backlog-6', 'title': 'Website Domain SEO Analysis', 'description': 'Analyze SEO potential for business ideas derived from WebsiteDomain.md and add to back.log. Sub-agent evaluation completed.', 'priority': 'medium', 'created': datetime.now().date().isoformat(), 'category': 'SEO'}
    ],
    'inProgress': [
        {'id': 'op-progress-1', 'title': 'UK Tax Navigator launch', 'description': 'GTM, landing page, Gumroad listing, launch posts, and email sequence prepared for the first validation push.', 'priority': 'high', 'created': datetime.now().date().isoformat(), 'category': 'Launch'},
        {'id': 'op-progress-2', 'title': 'Business Cash Flow Forecaster follow-on launch', 'description': 'Second release being prepared behind UK Tax Navigator, with launch assets underway.', 'priority': 'medium', 'created': datetime.now().date().isoformat(), 'category': 'Launch'},
        {'id': 'op-progress-3', 'title': 'Mission Control live-state auto feed', 'description': 'Pages now share data sources, next step is deeper auto-generation from workspace and session state.', 'priority': 'medium', 'created': datetime.now().date().isoformat(), 'category': 'Mission Control'}
    ],
    'inReview': [
        {'id': 'op-review-1', 'title': 'Mission Control live-state auto feed', 'description': 'Next step is deciding how much should auto-pull from sessions, cron, memory, and KANBAN sources.', 'priority': 'medium', 'created': datetime.now().date().isoformat(), 'category': 'Mission Control'},
        {'id': 'op-review-2', 'title': 'Product launch sequencing', 'description': 'Current recommendation is Tax first, Cash Flow second, but early buyer feedback should confirm that ordering.', 'priority': 'medium', 'created': datetime.now().date().isoformat(), 'category': 'Launch'}
    ],
    'blocked': [
        {'id': 'op-blocked-1', 'title': 'Shared editing on Projects page', 'description': 'Static GitHub Pages can read shared repo data, but not safely write synced edits without a backend layer.', 'priority': 'high', 'created': datetime.now().date().isoformat(), 'category': 'Platform'},
        {'id': 'op-blocked-2', 'title': 'Legacy external integrations', 'description': 'Email, Calendar, VPS, Coolify and other older KANBAN items still need credentials or connection details.', 'priority': 'medium', 'created': datetime.now().date().isoformat(), 'category': 'Infrastructure'}
    ]
}

for key, items in manual_and_launch_items.items():
    existing_titles = {x['title'] for x in merged_board.get(key, [])}
    for item in items:
        if item['title'] not in existing_titles:
            merged_board.setdefault(key, []).append(item)
        else:
            # Update existing items if the title matches
            for existing_item in merged_board[key]:
                if existing_item['title'] == item['title']:
                    existing_item.update(item)
                    break

write_json(DATA / 'operating-board.json', merged_board)

# --- Agents Data Processing ---
agents_data = [
    {
        'id': 'main', 'name': 'Lancelot ⚔️', 'status': 'amber', 'statusLabel': 'Thinking',
        'task': 'Coordinating launches, Mission Control, and execution priorities', 'lastActive': 'active today',
        'model': 'GPT 5.4', 'workstream': 'Coordinator',
        'summary': 'Knightly coordinator, concise, direct, delegates real task work instead of doing it by hand'
    },
    {
        'id': 'dashboard-refresh', 'name': 'Dashboard Refresh Job', 'status': 'green', 'statusLabel': 'Available',
        'task': 'Rebuilds dashboard data every 2 hours using a free model for routine upkeep', 'lastActive': 'scheduled',
        'model': 'Gemini 2.5 Flash Lite', 'workstream': 'Mission Control',
        'summary': 'Quiet housekeeping agent, keeps the dashboard current and sanitised'
    },
    {
        'id': 'daily-initiative', 'name': 'Daily Initiative Engine', 'status': 'green', 'statusLabel': 'Available',
        'task': 'Runs daily to pick a high-impact move toward revenue goals', 'lastActive': 'scheduled',
        'model': 'Gemini 2.5 Flash Lite', 'workstream': 'Revenue initiatives',
        'summary': 'Finds one practical move that pushes revenue goals forward without wasting spend'
    },
    {
        'id': 'opportunity-engine', 'name': 'Opportunity Engine', 'status': 'red', 'statusLabel': 'Busy',
        'task': 'Scanning and ranking opportunities across active workstreams', 'lastActive': 'active cadence',
        'model': 'Gemini 2.5 Flash Lite', 'workstream': 'Opportunities',
        'summary': 'Relentless scout, hunts for revenue angles and surfaces promising openings'
    }
]
write_json(DATA / 'agents.json', agents_data)

# --- Activity Data Processing ---
activity_data = [
    {'time': datetime.now().strftime('%Y-%m-%d %H:%M'), 'title': 'Dashboard data generation refined', 'detail': 'Updated script to correctly merge KANBAN items with manual backlog and launch priorities into operating-board.json.'},
    {'time': '2026-04-18 17:37', 'title': 'Dashboard reverted to stable state', 'detail': 'Reverted recent changes that caused rendering issues.'},
    {'time': '2026-04-18 17:34', 'title': 'Dashboard data generator added', 'detail': 'Mission Control pages can now be regenerated from workspace state using a shared script.'},
    {'time': '2026-04-18 17:34', 'title': 'Operating board unified', 'detail': 'Mission Control and Projects now share a single operating-board.json source.'},
    {'time': '2026-04-18 16:40', 'title': 'Dashboard refactored into multi-page architecture', 'detail': 'Overview, Projects, Daily Logs, Revenue, Governance, Pipeline, Blockers, and Links now live as separate pages.'},
]
write_json(DATA / 'activity.json', activity_data)

# --- Today Data Processing ---
mem18_content = read(ROOT / 'memory/2026-04-18.md')
next_focus = []
focus_lines = re.findall(r'- \*\*Best current focus order:\*\*(.*)', mem18_content, flags=re.DOTALL)
if focus_lines:
    next_focus_str = focus_lines[0].strip()
    if ':' in next_focus_str:
        next_focus = [x.strip() for x in next_focus_str.split(':', 1)[1].split(',')] if next_focus_str.split(':', 1)[1] else []

if not next_focus:
    next_focus = ['finish sellable digital products', 'launch checkout and landing pages', 'wire follow-up email flow']

today_data = {
    'focus': 'Launch UK Tax Navigator, prepare Business Cash Flow Forecaster, manage dashboard updates.',
    'nextJobs': ['Mission Control dashboard data regeneration (scheduled)', 'Daily Opportunities Ranking', 'Daily initiative engine'],
    'urgentBlockers': ['Shared editing for Projects page needs a backend', 'Legacy external integrations still need credentials', 'Refine dashboard data sources for live agent state'],
    'lastMeaningfulChange': 'Dashboard data generation script updated to merge all backlog items.'
}
write_json(DATA / 'today.json', today_data)

# --- Summary Data Processing ---
summary_data = {
    'primaryGoal': '£20,000 passive income in 3 months',
    'systemStatus': 'Operational',
    'metrics': {
        'ideas': len(merged_board.get('backlog', [])),
        'research': len(merged_board.get('inReview', [])),
        'launch': len(merged_board.get('inProgress', [])),
        'mrr': '£0'
    },
    'priorities': next_focus[:3],
    'quickStatus': {
        'hosting': 'GitHub Pages',
        'primaryModel': 'GPT 5.4',
        'projects': 'Shared operating board',
        'refresh': 'Data regeneration script'
    },
}
write_json(DATA / 'summary.json', summary_data)

print('Dashboard data generated and consolidated.')
