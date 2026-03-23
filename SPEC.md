# Mission Control Dashboard - Technical Specification

**Version:** 1.0  
**Date:** 2026-03-20  
**Owner:** Niall Brogan  
**Developer:** Lancelot (Coordinator) + Coder sub-agent  

---

## **Overview**

A web-based Mission Control dashboard providing real-time visibility into:
- Agent activity and status
- Workflow pipelines (Kanban-style)
- Blockers requiring approval
- Revenue tracking and priorities
- System health

**Access:** Web-based, accessible from any device worldwide (via Tailscale or public URL)

---

## **Architecture**

### **Tech Stack**
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (no frameworks for simplicity)
- **Data Sources:**
  - OpenClaw Gateway API (WebSocket or REST)
  - Local JSON files for Kanban state
  - Optional: GitHub API, external APIs
- **Hosting:** Vercel (free tier) or Netlify
- **Updates:** Auto-refresh every 30s or WebSocket live updates
- **Auth:** Vercel password protection or Tailscale (no public access)

### **Components**

1. **Header**
   - Dashboard title: "Mission Control"
   - Last updated timestamp
   - System status indicator (🟢 healthy / 🟡 warning / 🔴 critical)

2. **Metrics Overview (Top Cards)**
   - Active agents (count + list)
   - Cron jobs (total / running / errors)
   - Blockers (count + priority)
   - Revenue this month (manual or API)

3. **Agent Activity Panel**
   - Table: Agent Name | Current Task | Status | Last Active
   - Status colors: 🟢 active / 🟡 idle / 🔴 error
   - Click to view session details

4. **Kanban Workflow Board**
   - Columns: Ideas | Research | Build | Launch | Revenue
   - Drag-and-drop cards (stored in local JSON)
   - Each card: Title, Priority, Owner (agent/human), Updated
   - Color-coded by priority: 🔴 high / 🟡 medium / 🟢 low

5. **Blockers Dashboard**
   - Table: Item | Reason | Priority | Date Added | Action
   - Filter: All / Approvals / Dependencies / Technical
   - Click to resolve or approve

6. **System Health Panel**
   - CPU, Memory, Disk (from system-health cron job)
   - Gateway status (running/stopped)
   - Last backup timestamp
   - Security audit status

7. **Revenue Tracker**
   - Monthly target: £20,000 (3mo), £50,000 (6mo), £1M (12mo)
   - Progress bar with current amount
   - Top revenue streams (manual entry or API)

---

## **Data Sources**

### **OpenClaw Gateway API**
- **Endpoint:** `http://127.0.0.1:18789/api` (via Tailscale: `http://100.125.39.76:18789/api`)
- **Auth:** Gateway token (from config)
- **Data:**
  - `/status` → agent count, sessions, cron jobs
  - `/sessions/list` → active sessions
  - `/cron/list` → scheduled jobs
  - `/health` → system metrics

### **Local JSON Files** (workspace/Mission-Control/data/)
- `kanban.json` → Kanban board state
- `blockers.json` → Blocker list
- `revenue.json` → Revenue tracking

### **Optional External APIs**
- GitHub: repo activity, PRs
- Stripe/PayPal: revenue data (if integrated)

---

## **File Structure**

```
Mission-Control/
├── SPEC.md                  # This file
├── index.html               # Main dashboard
├── styles.css               # Styling
├── app.js                   # JavaScript logic
├── data/
│   ├── kanban.json          # Kanban state
│   ├── blockers.json        # Blockers list
│   └── revenue.json         # Revenue tracking
├── api/
│   └── openclaw-proxy.js    # Node.js proxy for OpenClaw API (if needed)
└── README.md                # Deployment guide
```

---

## **Features**

### **Phase 1 (MVP - This Week)**
- [x] Static HTML dashboard
- [x] Agent activity display (pull from OpenClaw API)
- [x] Cron job status
- [x] Blockers list (JSON-backed)
- [x] Basic Kanban board (JSON-backed)
- [x] Auto-refresh (30s polling)
- [x] Deploy to Vercel

### **Phase 2 (Next Week)**
- [ ] Drag-and-drop Kanban (interactive)
- [ ] WebSocket live updates (instead of polling)
- [ ] Blocker approval workflow
- [ ] Revenue chart (progress over time)
- [ ] Mobile-responsive design

### **Phase 3 (Future)**
- [ ] GitHub integration (PR status)
- [ ] Email/calendar integration
- [ ] AI insights (Lancelot summarizes trends)
- [ ] Notifications (Telegram alerts for blockers)

---

## **User Flows**

### **1. View Dashboard**
1. Open `https://mission-control.vercel.app` (or Tailscale URL)
2. See real-time agent status, cron jobs, blockers
3. Auto-refreshes every 30s

### **2. Manage Kanban Board**
1. Click "Add Card" in any column
2. Enter: Title, Priority, Owner, Description
3. Card saved to `kanban.json`
4. Drag-and-drop to move between columns

### **3. Resolve Blocker**
1. Click blocker row in dashboard
2. Mark as "Resolved" or "Approved"
3. Removed from active list, archived

### **4. Track Revenue**
1. View progress bar (current vs target)
2. Update revenue manually via form
3. Saved to `revenue.json`

---

## **Security**

- **No public access** (Tailscale-only or Vercel password)
- **API token** stored in environment variable (not in code)
- **Read-only** by default (write actions require confirmation)
- **No sensitive data** in GitHub (use .env for secrets)

---

## **Deployment Plan**

### **Step 1: Build Locally**
```bash
cd ~/.openclaw/workspace/Mission-Control
# Coder sub-agent creates index.html, styles.css, app.js
```

### **Step 2: Test Locally**
```bash
# Simple HTTP server
python3 -m http.server 8080
# Open http://localhost:8080
```

### **Step 3: Deploy to Vercel**
```bash
vercel deploy --prod
# Get public URL: https://mission-control-niall.vercel.app
```

### **Step 4: Secure Access**
- Option A: Vercel password protection (Enterprise only, paid)
- Option B: Tailscale-only access (modify to use `http://100.125.39.76:18789`)
- Option C: Add basic auth in Vercel edge function

---

## **Next Steps**

1. **Approve this spec** (Niall confirms design)
2. **Spawn coder sub-agent** (build HTML/CSS/JS)
3. **Test locally** (verify OpenClaw API access)
4. **Deploy to Vercel** (make accessible remotely)
5. **Iterate based on feedback** (add features as needed)

---

## **Questions for Niall**

1. **Access method:** Tailscale-only or password-protected public URL?
2. **Revenue tracking:** Manual entry or integrate with Stripe/PayPal API?
3. **Kanban priorities:** Should agents auto-update Kanban or manual only?
4. **Notifications:** Telegram alert when new blocker added?

---

**Estimated build time:** 2-3 hours (coder sub-agent)  
**Deployment time:** 15 minutes  
**Total to live dashboard:** ~4 hours
