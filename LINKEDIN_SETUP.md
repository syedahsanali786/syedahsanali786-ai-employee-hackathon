# 📼 LinkedIn Poster Setup Guide (Silver Tier)

## Prerequisites

### 1. Install Python Dependencies

Make sure you have Playwright installed:

```bash
cd "C:\Users\Iqra Traders\Documents\ai_employee"
pip install -r requirements.txt
```

If you haven't installed Playwright browsers yet:

```bash
playwright install chromium
```

### 2. Add LinkedIn Credentials to .env

Create or edit the `.env` file at:
```
C:\Users\Iqra Traders\Documents\ai_employee\.env
```

Add your LinkedIn credentials:

```env
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password_here
```

**Security Note:** Keep your `.env` file private and never commit it to GitHub!

---

## How to Prepare a Post

### Step 1: Create LINKEDIN_POST.md

Create a file at:
```
C:\Users\Iqra Traders\Documents\AI_Employee_Vault\LINKEDIN_POST.md
```

### Step 2: Use This Format

```markdown
---
status: pending
scheduled: today
---
## Post Content
Your actual post text goes here...

You can use multiple paragraphs.

Add hashtags at the end: #AI #Automation

#AI #Automation #PersonalProductivity
```

### Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Ready to post |
| `posted` | Already posted (will be skipped) |

---

## How to Run

### Run the Poster

```bash
python "C:\Users\Iqra Traders\Documents\ai_employee\linkedin_poster.py"
```

### What Happens

1. **Browser opens** - Chromium launches in visible mode
2. **Auto-login** - Uses saved session or logs in with credentials
3. **Posts content** - Types and publishes your post
4. **Updates file** - Changes status to "posted"
5. **Moves to Done** - Archives the post file
6. **Creates log** - Logs the action in /Logs/

---

## Example Output

```
============================================================
🤖 AI Employee - LinkedIn Poster (Silver Tier)
============================================================
📄 Checking for LINKEDIN_POST.md...
📖 Reading post content...
✅ Found pending post (280 chars)
📅 Scheduled: today

============================================================
📝 POST PREVIEW:
============================================================
Excited to share that I am building my own Personal AI Employee! 🤖
...
============================================================

============================================================
🌐 LAUNCHING CHROMIUM BROWSER...
============================================================
✅ Browser launched!

============================================================
📱 OPENING LINKEDIN...
============================================================
✅ Already logged in - session restored!

============================================================
📝 POSTING TO LINKEDIN...
============================================================
  ✅ Post content entered
  🖱️  Clicking Post button...
  ✅ Post published successfully!

============================================================
✅ POST SUCCESSFUL!
============================================================
✅ Posted to LinkedIn
✅ File status updated to 'posted'
✅ File moved to Done
✅ Log entry created
```

---

## What Gets Created

### After Successful Post:

1. **Post file moved to Done:**
   ```
   Done/LINKEDIN_POST_20260321_190000.md
   ```

2. **Log entry created:**
   ```
   Logs/LOG_LINKEDIN_20260321_190000.md
   ```

3. **Original file status updated:**
   ```markdown
   ---
   status: posted
   scheduled: today
   ---
   ```

---

## Troubleshooting

### "Credentials not found"
- Make sure `.env` file exists at: `C:\Users\Iqra Traders\Documents\ai_employee\.env`
- Check variable names: `LINKEDIN_EMAIL` and `LINKEDIN_PASSWORD`

### "Login failed"
- Check your email/password in .env
- LinkedIn may require 2FA - complete it in the browser
- Session is saved after first login

### "Post button not found"
- LinkedIn changes their UI frequently
- Script tries multiple selectors
- Watch the browser - you can manually post if needed

### "Post content not entered"
- Content may be too long (LinkedIn has character limits)
- Special characters may cause issues
- Keep posts under 3000 characters for best results

---

## Tips

1. **Keep browser visible** - Don't close it during posting
2. **One post at a time** - Script processes one LINKEDIN_POST.md per run
3. **Review before posting** - Watch the browser to ensure it works
4. **Save session** - After first login, session is saved for future runs

---

## Session Storage

Your LinkedIn session is stored in:
```
C:\Users\Iqra Traders\Documents\ai_employee\linkedin_session\
```

This folder contains:
- Browser cookies
- Authentication tokens
- Local storage

**Never share this folder** - it gives access to your LinkedIn!

---

## Creating Posts Programmatically

You can create posts automatically from other AI Employee features:

```python
# Example: Create post from email
post_content = f"""---
status: pending
scheduled: today
---
## Post Content
Just closed a deal with {client_name}! 🎉

#Business #Success
"""

with open("C:/Users/Iqra Traders/Documents/AI_Employee_Vault/LINKEDIN_POST.md", "w") as f:
    f.write(post_content)
```

Then run the poster to publish it!

---

**Created for: Iqra Traders**
**Silver Tier Feature**
