# 📅 Scheduler Setup Guide (Silver Tier)

## Prerequisites

### Install Python Dependencies

Make sure you have the `schedule` library installed:

```bash
cd "C:\Users\Iqra Traders\Documents\ai_employee"
pip install -r requirements.txt
```

If you haven't installed dependencies yet:

```bash
pip install schedule python-dotenv
```

---

## How to Run

### Start the Scheduler

```bash
python "C:\Users\Iqra Traders\Documents\ai_employee\scheduler.py"
```

### What Happens on Startup

1. **Shows vault path**
2. **Displays schedule overview** with next run times
3. **Lists all scheduled tasks**
4. **Runs initial overload check**
5. **Starts monitoring** in the background

---

## Scheduled Tasks

### 📰 Daily Morning Briefing (8:00 AM Every Day)

Creates `DAILY_BRIEFING.md` in vault root with:
- List of pending tasks from Needs_Action folder
- Tasks completed yesterday from Done folder
- Summary statistics

**Example Output:**
```markdown
## Good Morning! Daily Briefing - Saturday, March 21, 2026

### Pending Tasks
- [ ] EMAIL_Invoice_20260321.md
- [ ] WHATSAPP_John_Client.md
- ...

### Tasks Completed Yesterday
- [x] TEST_task.md
- [x] FILE_document.pdf_task.md

### Summary
- Total Pending: 5
- Total Done Today: 2
- Status: 🟢 AI Employee Active
```

---

### ⚠️  Overload Check (Every 30 Minutes)

Checks if more than 5 pending tasks exist in Needs_Action folder.

If overload detected:
- Creates `ALERT_overload.md` in Needs_Action folder
- Alerts user to review pending tasks

**Alert Content:**
```markdown
## ⚠️  TASK OVERLOAD ALERT

- Pending Tasks: 35
- Threshold: 5 tasks
- Status: OVERLOADED

### Recommended Actions
- [ ] Review pending tasks
- [ ] Prioritize urgent items
- [ ] Delegate or defer non-critical tasks
```

---

### 📊 Weekly CEO Briefing (Monday 9:00 AM)

Creates `MONDAY_CEO_BRIEFING.md` in vault root with:
- Summary of completed tasks this week
- Actions logged from Logs folder
- List of all pending items
- AI Employee system status

**Example Output:**
```markdown
## Monday Morning CEO Briefing

### This Week Summary
- Completed Tasks This Week: 15
- Actions Logged: 25

### Pending Items
- [email] EMAIL_Client_Inquiry.md
- [whatsapp] WHATSAPP_Urgent_Request.md

### AI Employee Status
- 🟢 All systems operational
- Watchers: Gmail ✅ WhatsApp ✅ File System ✅
```

---

## Sample Output

```
======================================================================
🤖 AI Employee - Scheduler (Silver Tier)
======================================================================

📂 Vault Path: C:\...\AI_Employee_Vault

======================================================================
📅 SCHEDULE OVERVIEW
======================================================================

  📰 Next Daily Briefing:     2026-03-22 08:00 (8:00 AM daily)
  ⚠️  Next Overload Check:    2026-03-21 20:30 (Every 30 minutes)
  📊 Next CEO Briefing:       2026-03-23 09:00 (Monday 9:00 AM)

======================================================================

📋 SCHEDULING TASKS...
======================================================================
  ✅ Daily Briefing:    Every day at 8:00 AM
  ✅ Overload Check:    Every 30 minutes
  ✅ CEO Briefing:      Every Monday at 9:00 AM
======================================================================

🔄 Running initial checks...

======================================================================
⚠️  RUNNING: Overload Check
======================================================================
  📊 Pending Tasks: 35
  ⚠️  OVERLOAD DETECTED: 35 pending tasks!
  ✅ Alert created: ALERT_overload.md
======================================================================

🚀 SCHEDULER STARTED
Press Ctrl+C to stop...
```

---

## Files Created

| File | Location | When |
|------|----------|------|
| `DAILY_BRIEFING.md` | Vault root | Daily at 8:00 AM |
| `ALERT_overload.md` | Needs_Action/ | When >5 pending tasks |
| `MONDAY_CEO_BRIEFING.md` | Vault root | Monday at 9:00 AM |

---

## Customization

### Change Schedule Times

Edit `scheduler.py` and modify these lines:

```python
# Daily briefing time (24-hour format)
schedule.every().day.at("08:00").do(run_daily_briefing)

# Overload check interval (in minutes)
schedule.every(30).minutes.do(run_overload_check)

# CEO briefing time
schedule.every().monday.at("09:00").do(run_ceo_briefing)
```

### Change Overload Threshold

Edit the threshold in `check_overload()` function:

```python
# Change from 5 to your preferred threshold
if pending_count > 5:  # Change this number
```

---

## Running in Background

### Option 1: Use a Terminal Multiplexer
Run in a separate terminal window or use tmux/screen.

### Option 2: Create a Batch File

Create `start_scheduler.bat`:

```batch
@echo off
python "C:\Users\Iqra Traders\Documents\ai_employee\scheduler.py"
```

Double-click to start.

### Option 3: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: "At startup" or "Daily at 8:00 AM"
4. Set action: Start a program
5. Program: `python.exe`
6. Arguments: Full path to `scheduler.py`
7. Start in: `C:\Users\Iqra Traders\Documents\ai_employee`

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'schedule'"
```bash
pip install schedule
```

### "No pending tasks shown"
- Make sure Needs_Action folder has .md files
- Check folder path is correct

### "Alert not created"
- Check if Needs_Action folder is writable
- Verify threshold is set correctly

### Schedule times wrong
- Check your system time zone
- Times are in 24-hour format (HH:MM)

---

## Tips

1. **Keep scheduler running** - Run in background for continuous monitoring
2. **Review daily briefings** - Check DAILY_BRIEFING.md each morning
3. **Clear completed tasks** - Move done items to Done folder regularly
4. **Monitor alerts** - When ALERT_overload.md appears, review pending tasks

---

**Created for: Iqra Traders**
**Silver Tier Feature**
