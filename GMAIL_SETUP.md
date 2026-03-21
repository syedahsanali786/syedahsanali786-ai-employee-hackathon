# 📧 Gmail Watcher Setup Guide (Silver Tier)

## Prerequisites

### 1. Install Python Dependencies

Open terminal and run:

```bash
cd "C:\Users\Iqra Traders\Documents\ai_employee"
pip install -r requirements.txt
```

### 2. Set Up Google Cloud & Gmail API

#### Step A: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (e.g., "AI Employee")
3. Note your Project ID

#### Step B: Enable Gmail API
1. In your project, go to **APIs & Services** > **Library**
2. Search for "Gmail API"
3. Click **Enable**

#### Step C: Create OAuth Credentials
1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - User Type: **External**
   - App name: AI Employee
   - Developer email: Your email
   - Scopes: Add `.../auth/gmail.readonly`
   - Test users: Add your Gmail address
4. For Application type, select **Desktop app**
5. Click **Create**
6. Download the JSON file
7. Rename it to `credentials.json`
8. Save it to: `C:\Users\Iqra Traders\Documents\ai_employee\credentials.json`

### 3. Create .env File (Optional)

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

Edit `.env` with your settings (optional - script works without it).

---

## How to Run

### First Run (Authentication)

```bash
python "C:\Users\Iqra Traders\Documents\ai_employee\gmail_watcher.py"
```

On first run:
1. Browser will open automatically
2. Sign in with your Gmail account
3. Grant permissions to AI Employee
4. Token will be saved to `token.json`
5. Script will start monitoring

### Subsequent Runs

Just run the same command - no need to re-authenticate:

```bash
python "C:\Users\Iqra Traders\Documents\ai_employee\gmail_watcher.py"
```

---

## What It Does

1. **Checks Gmail every 2 minutes** for UNREAD + IMPORTANT emails
2. **Creates task files** in `Needs_Action` folder:
   ```
   EMAIL_Subject_20260321_170000.md
   ```
3. **Tracks processed emails** - no duplicates
4. **Handles errors gracefully** - retries if Gmail is down

---

## Example Task File Created

```markdown
---
type: email
from: client@example.com
subject: Urgent: Project Update Needed
received: 2026-03-21 17:00:00
priority: high
status: pending
---

## Email Content
Hi, I need an update on the project status...

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward if needed
- [ ] Archive after processing
```

---

## Stop the Watcher

Press `Ctrl+C` in the terminal.

---

## Troubleshooting

### "Credentials file not found"
- Make sure `credentials.json` is in: `C:\Users\Iqra Traders\Documents\ai_employee\`

### "Token expired"
- Delete `token.json` and re-run - it will re-authenticate

### "Gmail API error"
- Check your internet connection
- Verify Gmail API is enabled in Google Cloud Console

### No emails detected
- Make sure emails are marked as UNREAD and IMPORTANT in Gmail
- You can star emails to make them important

---

**Created for: Iqra Traders**
**Silver Tier Feature**
