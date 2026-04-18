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
kanban_board = {
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
            kanban_board[key].append({
                'id': f'{key}-{len(kanban_board[key])+1}',
                'title': title,
                'description': 'Imported from KANBAN.md',
                'priority': 'medium' if key in ('inProgress','blocked') else 'low',
                'created': datetime.now().date().isoformat(),
                'category': 'KANBAN'
            })
        elif s.startswith('- **') and '**' in s[4:]:
            title = re.sub(r'\*\*', '', s[2:]).strip()
            kanban_board[key].append({
                'id': f'{key}-{len(kanban_board[key])+1}',
                'title': title,
                'description': 'Imported from KANBAN.md',
                'priority': 'medium',
                'created': datetime.now().date().isoformat(),
                'category': 'KANBAN'
            })

# --- Overlay Current Launch Priorities & Manual Backlog Items ---
# Load existing operating-board.json to merge with new data
existing_board = read(DATA / 'operating-board.json')
merged_board = json.loads(existing_board) if existing_board else {
    'backlog': [], 'inProgress': [], 'inReview': [], 'completed': [], 'blocked': []
}

# Add/Update items from KANBAN data into the merged board
for key in keys:
    for item in kanban_board[key]:
        if not any(x['title'] == item['title'] for x in merged_board[key]):
            merged_board[key].append(item)

# Add/Update specific launch items and manual backlog items
# Note: Manually added items from previous steps were: n8n, SEO analysis, Dashboard data gen
manual_backlog_items = [
    ('backlog', 'op-backlog-1', '5-model 24/7 debating R&D team', 'Captured for later phase, once product launches are live and revenue validation is underway.', 'low', 'Strategy'),
    ('backlog', 'op-backlog-2', 'Daily microapp factory', 'Useful later, but not before the current product launch path ships.', 'low', 'Innovation'),
    ('backlog', 'op-backlog-3', 'Expanded prompt-driven capability programme', 'Captured for later phase when core product sales flow is live and stable.', 'low', 'Capability'),
    ('backlog', 'op-backlog-4', 'n8n revenue workflow implementation', 'Stage n8n adoption properly, Phase 1 should focus on Launch Sequence Manager, Income Event Logger, and Product Demand Validator once live product execution needs automation support.', 'medium', 'Automation'),
    ('backlog', 'op-backlog-5', 'Dashboard Data Generation & Linking', 'Auto-generate dashboard data (operating-board.json, agents.json, etc.) from workspace state. Link project launch tasks to the operating board.', 'high', 'Dashboard'),
    ('backlog', 'op-backlog-6', 'Website Domain SEO Analysis', 'Analyze SEO potential for business ideas derived from WebsiteDomain.md and add to back.log. Sub-agent evaluation completed.', 'medium', 'SEO')
]

for key, item_id, title, desc, prio, cat in manual_backlog_items:
    found = False
    for existing_item in merged_board[key]:
        if existing_item['title'] == title:
            # Update existing item if necessary
            existing_item['description'] = desc
            existing_item['priority'] = prio
            existing_item['category'] = cat
            found = True
            break
    if not found:
        merged_board[key].append({
            'id': item_id,
            'title': title,
            'description': desc,
            'priority': prio,
            'created': datetime.now().date().isoformat(),
            'category': cat
        })

# Overlay current launch priorities into relevant sections
launch_items_overlay = [
    ('inProgress', 'UK Tax Navigator launch', 'GTM, landing page, Gumroad listing, launch posts, and email sequence prepared for the first validation push.', 'high', 'Launch'),
    ('inProgress', 'Business Cash Flow Forecaster follow-on launch', 'Second release being prepared behind UK Tax Navigator, with launch assets underway.', 'medium', 'Launch'),
    ('inReview', 'Mission Control live-state auto feed', 'Pages now share data sources, next step is deeper auto-generation from workspace and session state.', 'medium', 'Mission Control'),
    ('blocked', 'Shared editing for Projects page', 'Static GitHub Pages can read shared repo data, but cannot safely write synced edits without a backend layer.', 'high', 'Platform'),
]

for key, title, desc, prio, cat in launch_items_overlay:
    found = False
    for existing_item in merged_board[key]:
        if existing_item['title'] == title:
            existing_item['description'] = desc
            existing_item['priority'] = prio
            existing_item['category'] = cat
            found = True
            break
    if not found:
        merged_board[key].insert(0, {
            'id': f'{key}-overlay-{len(merged_board[key])+1}',
            'title': title,
            'description': desc,
            'priority': prio,
            'created': datetime.now().date().isoformat(),
            'category': cat,
        })

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
    {'time': datetime.now().strftime('%Y-%m-%d %H:%M'), 'title': 'Dashboard data generator updated', 'detail': 'Added explicit merging of manual backlog items into operating-board.json and refined agent/activity data generation.'},
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
    'lastMeaningfulChange': 'Dashboard data now merges KANBAN, launch priorities, and manual backlog items.'
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
