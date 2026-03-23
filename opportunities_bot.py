#!/usr/bin/env python3
"""
Passive Income Opportunities Bot - Powered by GPT-4o-mini
Daily research agent for finding passive income opportunities matching Niall's criteria
"""
import argparse
import datetime
import hashlib
import json
import logging
import os
import sqlite3
from openai import OpenAI

# Configuration
DB_PATH = "opportunities.db"
REPORT_DIR = "Research"
LOG_FILE = "opportunities_bot.log"

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize OpenAI client (uses OPENAI_API_KEY from environment)
client = OpenAI()

def init_db():
    """Initialize SQLite database"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS opportunities (
            opportunity_id TEXT PRIMARY KEY,
            title TEXT,
            category TEXT,
            description TEXT,
            investment_estimate REAL,
            roi_weeks REAL,
            effort_hours_week REAL,
            recurring INTEGER,
            automation_level INTEGER,
            score INTEGER,
            discovered_date TEXT
        )
        ''')
        conn.commit()

def generate_id(data_dict):
    """Generate unique hash ID for deduplication"""
    key = f"{data_dict['title']}:{data_dict['category']}"
    return hashlib.sha256(key.encode('utf-8')).hexdigest()[:16]

def calculate_score(roi_weeks, investment, effort_hours_week, recurring, automation_level):
    """Calculate opportunity score (0-100) based on criteria"""
    roi_score = max(0, min(100, (4 - roi_weeks) / 4 * 100))
    invest_score = max(0, min(100, (1000 - investment) / 1000 * 100))
    effort_score = max(0, min(100, (5 - effort_hours_week) / 5 * 100))
    recurring_score = 100 if recurring else 0
    automation_score = max(0, min(100, automation_level))
    
    total_score = (
        roi_score * 0.30 +
        invest_score * 0.25 +
        effort_score * 0.15 +
        recurring_score * 0.20 +
        automation_score * 0.10
    )
    
    return int(total_score)

def query_gpt(count=20):
    """Query GPT-4o-mini for passive income opportunities"""
    prompt = f"""Find {count} unique passive income opportunities for 2026 matching these EXACT criteria:

REQUIREMENTS (strict):
- Target ROI: 100% return in under 4 weeks
- Investment: under £1,000 (prefer £0-500)
- Post-launch effort: under 5 hours per week
- Recurring revenue: strongly preferred
- High automation potential (80%+ once set up)

EXCLUDE completely:
- Regulatory/compliance solutions
- Licensed financial services
- Legal advisory services
- Anything requiring professional certifications

FOCUS ON:
- Digital products (templates, spreadsheets, guides, checklists)
- Info products (courses, ebooks, membership sites)
- Affiliate marketing (financial tools, SaaS products)
- Print-on-demand (zero inventory e-commerce)
- No-code micro-SaaS
- Content monetization (YouTube, Medium, Substack)
- Lead generation sites

TARGET MARKET: UK focus, especially small business owners, freelancers, startup founders

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "title": "Specific opportunity name",
    "category": "Digital Products|Info Products|Affiliate|Print-on-Demand|Micro-SaaS|Content|Lead Gen",
    "description": "Brief description (max 200 chars)",
    "investment_estimate": 50.0,
    "roi_weeks": 2.0,
    "effort_hours_week": 3.0,
    "recurring": true,
    "automation_level": 85
  }}
]

Make opportunities CONCRETE and ACTIONABLE. No generic advice. Real, specific business ideas."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a passive income research expert. Return only valid JSON arrays."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"GPT API call failed: {e}")
        return None

def parse_opportunities(response_str):
    """Parse and validate JSON response from GPT"""
    try:
        data = json.loads(response_str)
        
        # Handle different response formats
        if isinstance(data, dict):
            if "opportunities" in data:
                data = data["opportunities"]
            elif "items" in data:
                data = data["items"]
            else:
                # If it's a dict with numbered keys like "1", "2", convert to list
                data = list(data.values())
        
        if not isinstance(data, list):
            logging.error(f"Response is not a list: {type(data)}")
            return []
        
        valid_items = []
        for item in data:
            required = ["title", "category", "description", "investment_estimate", 
                       "roi_weeks", "effort_hours_week", "recurring", "automation_level"]
            if not all(k in item for k in required):
                logging.warning(f"Skipping item missing fields: {item.get('title', 'unknown')}")
                continue
            
            try:
                title = str(item["title"]).strip()
                category = str(item["category"]).strip()
                description = str(item["description"]).strip()
                investment = float(item["investment_estimate"])
                roi_weeks = float(item["roi_weeks"])
                effort = float(item["effort_hours_week"])
                recurring = bool(item["recurring"])
                automation = int(item["automation_level"])
                
                if investment < 0 or roi_weeks < 0 or effort < 0:
                    continue
                automation = max(0, min(100, automation))
                
                # Filter regulatory/compliance
                desc_lower = f"{title} {category} {description}".lower()
                if any(word in desc_lower for word in ["regulatory", "compliance", "licensed", "legal advisory"]):
                    logging.info(f"Filtered: {title}")
                    continue
                
                valid_items.append({
                    "title": title,
                    "category": category,
                    "description": description,
                    "investment_estimate": investment,
                    "roi_weeks": roi_weeks,
                    "effort_hours_week": effort,
                    "recurring": recurring,
                    "automation_level": automation
                })
            except (ValueError, TypeError) as e:
                logging.warning(f"Conversion error: {e}")
                continue
        
        return valid_items
    
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        logging.error(f"Response: {response_str[:500]}")
        return []

def save_opportunities(items):
    """Save opportunities to database with deduplication"""
    saved_count = 0
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        for item in items:
            item_id = generate_id(item)
            
            c.execute("SELECT 1 FROM opportunities WHERE opportunity_id = ?", (item_id,))
            if c.fetchone():
                logging.info(f"Duplicate: {item['title']}")
                continue
            
            score = calculate_score(
                item["roi_weeks"],
                item["investment_estimate"],
                item["effort_hours_week"],
                item["recurring"],
                item["automation_level"]
            )
            
            discovered_date = datetime.datetime.utcnow().isoformat() + "Z"
            
            try:
                c.execute('''
                INSERT INTO opportunities 
                (opportunity_id, title, category, description, investment_estimate, 
                 roi_weeks, effort_hours_week, recurring, automation_level, score, discovered_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item_id, item["title"], item["category"], item["description"],
                    item["investment_estimate"], item["roi_weeks"], item["effort_hours_week"],
                    int(item["recurring"]), int(item["automation_level"]), score, discovered_date
                ))
                saved_count += 1
                logging.info(f"Saved: {item['title']} (score: {score})")
            except Exception as e:
                logging.error(f"DB save failed: {e}")
        
        conn.commit()
    
    return saved_count

def cmd_generate(count):
    """Generate new opportunities"""
    logging.info(f"Generate started: count={count}")
    print(f"🔍 Querying GPT-4o-mini for {count} opportunities...")
    
    response_str = query_gpt(count)
    if not response_str:
        print("❌ Failed to get response from GPT")
        return
    
    opportunities = parse_opportunities(response_str)
    if not opportunities:
        print("❌ No valid opportunities parsed")
        logging.error(f"Raw response: {response_str[:1000]}")
        return
    
    saved = save_opportunities(opportunities)
    print(f"✅ Saved {saved} new opportunities ({len(opportunities) - saved} duplicates filtered)")
    logging.info(f"Generate finished: {saved} saved, {len(opportunities) - saved} duplicates")

def cmd_report(top):
    """Generate markdown report"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
        SELECT title, category, description, investment_estimate, roi_weeks, 
               effort_hours_week, recurring, automation_level, score, discovered_date
        FROM opportunities
        ORDER BY score DESC
        LIMIT ?
        ''', (top,))
        rows = c.fetchall()
    
    if not rows:
        print("❌ No opportunities in database")
        return
    
    today_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    os.makedirs(REPORT_DIR, exist_ok=True)
    report_path = os.path.join(REPORT_DIR, f"{today_str}-ai-opportunities.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Top {top} AI-Generated Passive Income Opportunities - {today_str}\n\n")
        f.write("_Generated by GPT-4o-mini Research Bot_\n\n")
        f.write("---\n\n")
        
        for i, row in enumerate(rows, 1):
            title, category, desc, invest, roi, effort, recurring, automation, score, date = row
            rec_str = "Yes ✅" if recurring else "No ❌"
            
            f.write(f"## {i}. {title} (Score: {score}/100)\n\n")
            f.write(f"- **Category:** {category}\n")
            f.write(f"- **Score:** {score}/100\n")
            f.write(f"- **Investment:** £{invest:.0f}\n")
            f.write(f"- **Time to ROI:** {roi:.1f} weeks\n")
            f.write(f"- **Weekly Effort:** {effort:.1f} hours\n")
            f.write(f"- **Recurring Revenue:** {rec_str}\n")
            f.write(f"- **Automation Level:** {automation}%\n")
            f.write(f"- **Discovered:** {date[:10]}\n\n")
            f.write(f"**Description:** {desc}\n\n")
            f.write("---\n\n")
    
    print(f"✅ Report generated: {report_path}")
    logging.info(f"Report: {report_path}")

def cmd_list(min_score):
    """List opportunities by score"""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
        SELECT title, category, score, investment_estimate, roi_weeks
        FROM opportunities
        WHERE score >= ?
        ORDER BY score DESC
        ''', (min_score,))
        rows = c.fetchall()
    
    if not rows:
        print(f"❌ No opportunities with score >= {min_score}")
        return
    
    print(f"\n📊 Opportunities with score >= {min_score}:\n")
    for title, category, score, invest, roi in rows:
        print(f"  {score:3d}/100  {title}")
        print(f"          {category} | £{invest:.0f} investment | {roi:.1f}w ROI\n")

def main():
    parser = argparse.ArgumentParser(description="Passive Income Research Bot (GPT-powered)")
    subparsers = parser.add_subparsers(dest='command', required=False)
    
    parser_gen = subparsers.add_parser('generate', help='Generate opportunities')
    parser_gen.add_argument('--count', type=int, default=20, help='Number to generate (default: 20)')
    
    parser_rep = subparsers.add_parser('report', help='Generate markdown report')
    parser_rep.add_argument('--top', type=int, default=10, help='Top N (default: 10)')
    
    parser_list = subparsers.add_parser('list', help='List by score')
    parser_list.add_argument('--min-score', type=int, default=75, help='Min score (default: 75)')
    
    args = parser.parse_args()
    
    init_db()
    
    if args.command == 'generate':
        cmd_generate(args.count)
    elif args.command == 'report':
        cmd_report(args.top)
    elif args.command == 'list':
        cmd_list(args.min_score)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
