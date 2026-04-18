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
        print(f'Error reading {path}: {e}')
        return default


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

# KANBAN -> operating board
kanban = read(ROOT / 'KANBAN.md')
headers = ['📋 Backlog', '🔄 In Progress', '👀 In Review', '✅ Completed', '🚫 Blocked']
keys = ['backlog', 'inProgress', 'inReview', 'completed', 'blocked']
board = {k: [] for k in keys}
for hdr, key in zip(headers, keys):
    m = re.search(rf'##\s+{re.escape(hdr)}(.*?)(?=^##\s+|\Z)', kanban, flags=re.S | re.M)
    if not m:
        continue
    block = m.group(1)
    for line in block.splitlines():
        s = line.strip()
        if s.startswith('- [ ] '):
            title = s[6:].strip()
            board[key].append({
                'id': f'{key}-{len(board[key])+1}',
                'title': title,
                'description': 'Imported from KANBAN.md',
                'priority': 'medium' if key in ('inProgress','blocked') else 'low',
                'created': datetime.now().date().isoformat(),
                'category': 'KANBAN'
            })
        elif s.startswith('- **') and '**' in s[4:]:
            title = re.sub(r'\*\*', '', s[2:]).strip()
            board[key].append({
                'id': f'{key}-{len(board[key])+1}',
                'title': title,
                'description': 'Imported from KANBAN.md',
                'priority': 'medium',
                'created': datetime.now().date().isoformat(),
                'category': 'KANBAN'
            })

# Overlay current launch priorities so board stays relevant
launch_items = [
    ('inProgress', 'UK Tax Navigator launch', 'GTM, landing page, Gumroad listing, launch posts, and email sequence prepared for the first validation push.', 'high', 'Launch'),
    ('inProgress', 'Business Cash Flow Forecaster follow-on launch', 'Second release being prepared behind UK Tax Navigator, with launch assets underway.', 'medium', 'Launch'),
    ('inReview', 'Mission Control live-state auto feed', 'Pages now share data sources, next step is deeper auto-generation from workspace and session state.', 'medium', 'Mission Control'),
    ('blocked', 'Shared editing for Projects page', 'Static GitHub Pages can read shared repo data, but cannot safely write synced edits without a backend layer.', 'high', 'Platform'),
]
for key, title, desc, prio, cat in launch_items:
    if not any(x['title'] == title for x in board[key]):
        board[key].insert(0, {
            'id': f'{key}-overlay-{len(board[key])+1}',
            'title': title,
            'description': desc,
            'priority': prio,
            'created': datetime.now().date().isoformat(),
            'category': cat,
        })

(DATA / 'operating-board.json').write_text(json.dumps(board, indent=2), encoding='utf-8')

# We cannot access live API here, so use workspace docs + refresh metadata fallback
agents = [
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
(DATA / 'agents.json').write_text(json.dumps(agents, indent=2), encoding='utf-8')

activity = [
    {'time': datetime.now().strftime('%Y-%m-%d %H:%M'), 'title': 'Dashboard data generator added', 'detail': 'Mission Control pages can now be regenerated from workspace state using a shared script.'},
    {'time': datetime.now().strftime('%Y-%m-%d %H:%M'), 'title': 'Operating board unified', 'detail': 'Mission Control and Projects now share a single operating-board.json source.'},
    {'time': '2026-04-18 16:40', 'title': 'Dashboard refactored into multi-page architecture', 'detail': 'Overview, Projects, Daily Logs, Revenue, Governance, Pipeline, Blockers, and Links now live as separate pages.'},
]
(DATA / 'activity.json').write_text(json.dumps(activity, indent=2), encoding='utf-8')

mem18 = read(ROOT / 'memory/2026-04-18.md')
next_focus = []
for line in mem18.splitlines():
    s = line.strip('- ').strip()
    if s.startswith('Best current focus order:'):
        next_focus = [x.strip() for x in s.split(':',1)[1].split(',')] if ':' in s else []
        break
if not next_focus:
    next_focus = ['finish sellable digital products', 'launch checkout and landing pages', 'wire follow-up email flow']

today = {
    'focus': 'Launch UK Tax Navigator, prepare Business Cash Flow Forecaster, keep Mission Control in support mode.',
    'nextJobs': ['Mission Control dashboard refresh (2-hour cycle)', 'Daily Opportunities Ranking', 'Daily initiative engine'],
    'urgentBlockers': ['Shared editing on Projects page needs a backend', 'Legacy external integrations still need credentials'],
    'lastMeaningfulChange': 'Mission Control and Projects now share one operating board data source.'
}
(DATA / 'today.json').write_text(json.dumps(today, indent=2), encoding='utf-8')

summary = {
    'primaryGoal': '£20,000 passive income in 3 months',
    'systemStatus': 'Operational',
    'metrics': {'ideas': len(board['backlog']), 'research': len(board['inReview']), 'launch': len(board['inProgress']), 'mrr': '£0'},
    'priorities': next_focus[:3],
    'quickStatus': {'hosting': 'GitHub Pages', 'primaryModel': 'GPT 5.4', 'projects': 'Shared operating board', 'refresh': '2-hour job'},
}
(DATA / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')

print('generated dashboard data')
