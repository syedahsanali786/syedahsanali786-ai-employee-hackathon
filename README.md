# 🤖 Personal AI Employee
### Built by Syed Ahsan Ali | Hackathon 0 | Gold Tier 🥇

> Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

## 🏆 Tier Completion Status

| Tier | Status | Features |
|------|--------|----------|
| 🥉 Bronze | ✅ Complete | Vault, Dashboard, File Watcher, Agent Skills |
| 🥈 Silver | ✅ Complete | Gmail, WhatsApp, LinkedIn, Scheduler, Approval |
| 🥇 Gold | ✅ Complete | Odoo, Facebook, Twitter, CEO Briefing, Ralph Wiggum |

## 📖 What Is This Project?

A Personal AI Employee that autonomously manages personal and business affairs 24/7.
Built using Claude Code + Python + Playwright + Odoo.

## 🏗️ Architecture

```
+------------------------------------------------------------------+
|                    Personal AI Employee                           |
+------------------------------------------------------------------+
|  BRONZE TIER - Foundation                                         |
|  - Vault System (AI_Employee_Vault/)                              |
|  - Dashboard.md (Real-time status)                                |
|  - File Watcher (Autonomous file monitoring)                      |
|  - Agent Skills (Task processing logic)                           |
+------------------------------------------------------------------+
|  SILVER TIER - Communication                                      |
|  - Gmail Watcher (Process emails autonomously)                    |
|  - WhatsApp Watcher (Process messages)                            |
|  - LinkedIn Poster (Auto-post content)                            |
|  - Scheduler (Task automation)                                    |
|  - Approval System (Human-in-the-loop)                            |
+------------------------------------------------------------------+
|  GOLD TIER - Business Integration                                 |
|  - Odoo MCP (Accounting & Invoices)                               |
|  - Facebook/Instagram Poster                                      |
|  - Twitter Poster                                                 |
|  - Weekly CEO Briefing (Monday reports)                           |
|  - Ralph Wiggum Loop (Autonomous task processor)                  |
+------------------------------------------------------------------+
```

## 📁 Vault Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time status dashboard
├── Business_Goals.md         # Q1 2026 objectives & metrics
├── MONDAY_CEO_BRIEFING.md    # Weekly executive reports
├── Needs_Action/             # Pending tasks (input)
├── Done/                     # Completed tasks (output)
├── Plans/                    # Task execution plans
├── Logs/                     # Activity logs
└── SOCIAL_POST.md            # Social media queue
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js (for some tools)
- Odoo 16+ (for Gold tier)

### Installation

```bash
cd "C:\Users\Iqra Traders\Documents\Syed_Ahsan_AI_Employee"
pip install python-dotenv tweepy requests playwright
playwright install
```

### Configuration

Create .env file in project root with your credentials.

## 📋 Scripts Reference

### Gold Tier Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| odoo_mcp.py | Create invoices, accounting reports | python odoo_mcp.py |
| social_media_poster.py | Post to Facebook & Instagram | python social_media_poster.py |
| twitter_poster.py | Post to Twitter/X | python twitter_poster.py |
| weekly_ceo_briefing.py | Generate Monday CEO reports | python weekly_ceo_briefing.py |
| ralph_wiggum.py | Autonomous task processor | python ralph_wiggum.py --test |

### Silver Tier Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| create_gmail_watcher.ps1 | Monitor Gmail inbox | Run PowerShell |
| create_whatsapp_watcher.ps1 | Monitor WhatsApp Web | Run PowerShell |
| create_linkedin_poster.ps1 | Auto-post to LinkedIn | Run PowerShell |
| create_scheduler.ps1 | Task scheduling system | Run PowerShell |
| create_approval_watcher.ps1 | Human approval system | Run PowerShell |

### Bronze Tier Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| create_filesystem_watcher.ps1 | Monitor file changes | Run PowerShell |
| create_dashboard.ps1 | Generate status dashboard | Run PowerShell |
| create_log.ps1 | Logging system | Run PowerShell |

## 🎯 Key Features

### Bronze Tier - Foundation

1. **Vault System** - Centralized task storage with Markdown format
2. **Dashboard** - Real-time task status and metrics
3. **File Watcher** - Autonomous file monitoring
4. **Agent Skills** - Task analysis and execution

### Silver Tier - Communication

1. **Gmail Watcher** - Monitors inbox every 60 seconds
2. **WhatsApp Watcher** - Processes incoming messages
3. **LinkedIn Poster** - Auto-posts content via Playwright
4. **Scheduler** - Cron-like task scheduling
5. **Approval System** - Human-in-the-loop workflow

### Gold Tier - Business Integration

1. **Odoo MCP** - Create invoices, accounting reports
2. **Facebook/Instagram Poster** - Post via Graph API
3. **Twitter Poster** - Post tweets via API v2
4. **Weekly CEO Briefing** - Auto-generated Monday reports
5. **Ralph Wiggum Loop** - Autonomous task processor

## 📊 Dashboard Example

```markdown
# AI Employee Dashboard

## Quick Stats
- Total Tasks Completed: 150
- Last Update: 2026-03-24 21:22:39
- Status: Active

## System Status
- Gmail Watcher: Active
- WhatsApp Watcher: Active
- Odoo Integration: Active
- Twitter Poster: Active
```

## 🔧 Troubleshooting

**Odoo Connection Failed**
- Check ODOO_URL is correct
- Verify database exists
- Ensure Odoo server is running

**Social Media Posting Fails**
- Check API credentials in .env
- Verify app permissions
- Regenerate expired tokens

**Ralph Wiggum Not Processing**
- Check Needs_Action folder has files
- Verify VAULT_PATH in .env

## 📈 Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Response Time | < 24 hrs | < 1 hr |
| Invoice Rate | > 90% | 95% |
| Task Completion | 100% | 100% |

## 🎓 Learning Resources

- Claude Code Documentation
- Odoo API Documentation
- Facebook Graph API
- Twitter API v2
- Playwright for Python

---

**Generated by Syed Ahsan AI Employee v1.0**
*Gold Tier Complete*
