# Mission Control Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
cd ~/.openclaw/workspace/Mission-Control
pip3 install -r requirements.txt
```

### 2. Set OpenAI API Key (for Opportunities Bot)
The opportunities bot needs an OpenAI API key. You have two options:

**Option A: Environment Variable (recommended)**
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

Add this to your `~/.zshrc` or `~/.bash_profile` to make it permanent.

**Option B: Hardcode in Script (less secure)**
Edit `opportunities_bot.py` and add your key:
```python
client = OpenAI(api_key="your-key-here")
```

### 3. Test the Opportunities Bot
```bash
# Generate 10 opportunities
python3 opportunities_bot.py generate --count 10

# Create a report
python3 opportunities_bot.py report --top 10

# List high-scoring opportunities
python3 opportunities_bot.py list --min-score 80
```

### 4. Set Up Daily Automation (Optional)
Edit your crontab:
```bash
crontab -e
```

Add this line to run daily at 6am:
```
0 6 * * * cd ~/.openclaw/workspace/Mission-Control && /usr/bin/python3 opportunities_bot.py generate --count 20 && /usr/bin/python3 opportunities_bot.py report --top 10
```

## Work Management System

### View Your Mission Control Dashboard

1. Download Obsidian: https://obsidian.md/
2. Open Obsidian → "Open folder as vault"
3. Select: `~/.openclaw/workspace/Mission-Control`
4. Install Dataview plugin:
   - Settings → Community plugins → Browse
   - Search "Dataview" → Install → Enable
5. Open `Dashboard/Dashboard.md`

You'll see your Kanban board with all work items organized by status.

### Create Work Items

```bash
# Create a new task
python3 work_bot.py create --title "Build landing page" --assigned_to niall --priority p1-high --due_date 2026-03-20

# Update status
python3 work_bot.py update --id 1 --status "In Progress"

# List all items
python3 work_bot.py list

# Mark complete
python3 work_bot.py complete --id 1

# Refresh dashboard
python3 work_bot.py dashboard
```

## Current Setup Status

✅ Work management system (work_bot.py)
✅ Obsidian integration with Kanban boards
✅ AI-powered opportunities research (opportunities_bot.py)
❌ OpenAI API key (you need to add this)
❌ Daily cron automation (optional)
❌ GitHub backup (pending repo URL)

## Next Steps

1. Add your OpenAI API key (see above)
2. Run `python3 opportunities_bot.py generate --count 10` to generate your first set of opportunities
3. Open Mission Control in Obsidian to see your dashboard
4. Pick 2 opportunities from the research report and create work items for them
5. Start building!

## Need Help?

Just ask Lancelot in Telegram or Discord. I'm here to help you hit that £20k target.
