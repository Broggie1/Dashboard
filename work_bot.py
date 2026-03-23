"""
Work Bot for Mission Control

Features:
- Manage work items with SQLite + Obsidian Markdown sync
- Status workflow: Backlog -> Planned -> In Progress -> Blocked -> Review -> Complete
- Priority tags: #p0-critical, #p1-high, #p2-medium, #p3-low
- Dependencies and blocking support
- Generate Dashboard.md with Dataview Kanban board queries
- CLI commands: create, update, list, complete, block

Setup:
- Requires Python 3.9+
- Requires sqlite3 (builtin), pyyaml, argparse
- Place work_bot.py inside the Obsidian vault root

Usage examples:
  python work_bot.py create --title "New Task" --assigned_to niall --priority p1-high --due_date 2026-03-30
  python work_bot.py update --id 1 --status "In Progress"
  python work_bot.py list --status Planned
  python work_bot.py complete --id 1
  python work_bot.py block --id 2

"""

import os
import sys
import sqlite3
import yaml
import argparse
from datetime import datetime

VAULT_PATH = os.path.abspath(os.path.dirname(__file__))
WORK_ITEMS_PATH = os.path.join(VAULT_PATH, "Work-Items")
TEMPLATE_PATH = os.path.join(VAULT_PATH, "Templates", "WorkItemTemplate.md")
DASHBOARD_PATH = os.path.join(VAULT_PATH, "Dashboard", "Dashboard.md")

STATUS_FLOW = ["Backlog", "Planned", "In Progress", "Blocked", "Review", "Complete"]
PRIORITY_TAGS = ["p0-critical", "p1-high", "p2-medium", "p3-low"]

class WorkBot:
    def __init__(self, db_path=os.path.join(VAULT_PATH, "work_items.db")):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()

    def _create_table(self):
        c = self.conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS work_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Backlog',
            priority TEXT NOT NULL DEFAULT 'p2-medium',
            assigned_to TEXT,
            created TEXT NOT NULL,
            updated TEXT NOT NULL,
            due_date TEXT,
            tags TEXT,
            dependencies TEXT
        )
        ''')
        self.conn.commit()

    def _get_current_date(self):
        return datetime.now().strftime("%Y-%m-%d")

    def create_item(self, title, assigned_to=None, priority="p2-medium", due_date=None, tags=None, dependencies=None):
        created = self._get_current_date()
        tags_str = ",".join(tags) if tags else ""
        dependencies_str = ",".join(str(dep) for dep in dependencies) if dependencies else ""
        c = self.conn.cursor()
        c.execute('''
        INSERT INTO work_items (title, status, priority, assigned_to, created, updated, due_date, tags, dependencies)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, "Backlog", priority, assigned_to, created, created, due_date, tags_str, dependencies_str))
        self.conn.commit()
        item_id = c.lastrowid
        self._create_markdown(item_id, title, "Backlog", priority, assigned_to, created, created, due_date, tags, dependencies)
        print(f"Created work item {item_id}: {title}")
        return item_id

    def _create_markdown(self, item_id, title, status, priority, assigned_to, created, updated, due_date, tags, dependencies):
        filename = f"{item_id} - {title}.md"
        filepath = os.path.join(WORK_ITEMS_PATH, filename)
        frontmatter = {
            "status": status,
            "priority": priority,
            "assigned_to": assigned_to,
            "created": created,
            "updated": updated,
            "due_date": due_date,
            "tags": tags or [],
            "dependencies": dependencies or []
        }
        content = f"---\n" + yaml.dump(frontmatter) + "---\n\n# " + title + "\n"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def update_item(self, item_id, **kwargs):
        c = self.conn.cursor()
        updates = []
        values = []
        for k, v in kwargs.items():
            if k == "tags" or k == "dependencies":
                v = ",".join(v) if isinstance(v, list) else v
            if k == "updated":
                continue  # updated will be set by us
            updates.append(f"{k} = ?")
            values.append(v)
        if not updates:
            print("No updates provided.")
            return
        # Set updated date
        updates.append("updated = ?")
        values.append(self._get_current_date())
        values.append(item_id)
        sql = f"UPDATE work_items SET {', '.join(updates)} WHERE id = ?"
        c.execute(sql, values)
        self.conn.commit()
        # Sync markdown
        self._sync_markdown(item_id)
        print(f"Updated work item {item_id}")

    def _sync_markdown(self, item_id):
        c = self.conn.cursor()
        c.execute("SELECT title, status, priority, assigned_to, created, updated, due_date, tags, dependencies FROM work_items WHERE id = ?", (item_id,))
        row = c.fetchone()
        if not row:
            print(f"Work item {item_id} not found in DB.")
            return
        title, status, priority, assigned_to, created, updated, due_date, tags_str, deps_str = row
        tags = tags_str.split(",") if tags_str else []
        dependencies = [int(d) for d in deps_str.split(",") if d] if deps_str else []
        filename = f"{item_id} - {title}.md"
        filepath = os.path.join(WORK_ITEMS_PATH, filename)
        frontmatter = {
            "status": status,
            "priority": priority,
            "assigned_to": assigned_to,
            "created": created,
            "updated": updated,
            "due_date": due_date,
            "tags": tags,
            "dependencies": dependencies
        }
        content = f"---\n" + yaml.dump(frontmatter) + "---\n\n# " + title + "\n"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def list_items(self, status=None):
        c = self.conn.cursor()
        if status and status in STATUS_FLOW:
            c.execute("SELECT id, title, status, priority, assigned_to, due_date FROM work_items WHERE status = ? ORDER BY due_date", (status,))
        else:
            c.execute("SELECT id, title, status, priority, assigned_to, due_date FROM work_items ORDER BY status, due_date")
        rows = c.fetchall()
        for row in rows:
            print(f"ID {row[0]}: {row[1]} [{row[2]}] Priority: {row[3]} Assigned: {row[4]} Due: {row[5]}")

    def complete_item(self, item_id):
        self.update_item(item_id, status="Complete")

    def block_item(self, item_id):
        self.update_item(item_id, status="Blocked")

    def generate_dashboard(self):
        # Generates Dashboard.md with Dataview Kanban queries
        content = "# Dashboard\n\n"
        for status in STATUS_FLOW:
            content += f"## {status}\n"
            content += f"```dataview\n"
            content += f"table priority as Priority, assigned_to as Assigned, due_date as Due\n"
            content += f"from \"Work-Items\"\n"
            content += f"where status = \"{status}\"\n"
            content += f"sort priority asc, due_date asc\n"
            content += f"\n"
            content += f"kanban\n"
            content += f"```\n\n"
        with open(DASHBOARD_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Dashboard.md updated at {DASHBOARD_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Work Bot CLI for Mission Control")
    subparsers = parser.add_subparsers(dest="command")

    # create
    create_parser = subparsers.add_parser("create", help="Create a new work item")
    create_parser.add_argument("--title", required=True, help="Title of the work item")
    create_parser.add_argument("--assigned_to", help="Person assigned to this item")
    create_parser.add_argument("--priority", choices=PRIORITY_TAGS, default="p2-medium")
    create_parser.add_argument("--due_date", help="Due date YYYY-MM-DD")
    create_parser.add_argument("--tags", nargs="*", help="Tags (space separated)")
    create_parser.add_argument("--dependencies", nargs="*", type=int, help="IDs of dependencies")

    # update
    update_parser = subparsers.add_parser("update", help="Update a work item")
    update_parser.add_argument("--id", type=int, required=True, help="ID of the work item")
    update_parser.add_argument("--status", choices=STATUS_FLOW)
    update_parser.add_argument("--priority", choices=PRIORITY_TAGS)
    update_parser.add_argument("--assigned_to")
    update_parser.add_argument("--due_date")
    update_parser.add_argument("--tags", nargs="*", help="Tags (space separated)")
    update_parser.add_argument("--dependencies", nargs="*", type=int, help="IDs of dependencies")

    # list
    list_parser = subparsers.add_parser("list", help="List work items")
    list_parser.add_argument("--status", choices=STATUS_FLOW, help="Filter by status")

    # complete
    complete_parser = subparsers.add_parser("complete", help="Mark a work item complete")
    complete_parser.add_argument("--id", type=int, required=True, help="ID of the work item")

    # block
    block_parser = subparsers.add_parser("block", help="Block a work item")
    block_parser.add_argument("--id", type=int, required=True, help="ID of the work item")

    # dashboard
    dash_parser = subparsers.add_parser("dashboard", help="Generate Dashboard.md with Dataview queries")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    bot = WorkBot()

    if args.command == "create":
        bot.create_item(args.title, args.assigned_to, args.priority, args.due_date, args.tags, args.dependencies)
    elif args.command == "update":
        updates = {k: v for k, v in vars(args).items() if k not in ["command", "id"] and v is not None}
        bot.update_item(args.id, **updates)
    elif args.command == "list":
        bot.list_items(args.status)
    elif args.command == "complete":
        bot.complete_item(args.id)
    elif args.command == "block":
        bot.block_item(args.id)
    elif args.command == "dashboard":
        bot.generate_dashboard()

if __name__ == "__main__":
    main()
