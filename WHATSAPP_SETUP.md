# 📱 WhatsApp Watcher Setup Guide (Silver Tier)

## Prerequisites

### 1. Install Python Dependencies

Open terminal and run:

```bash
cd "C:\Users\Iqra Traders\Documents\ai_employee"
pip install -r requirements.txt
```

### 2. Install Playwright Browsers

After installing playwright, install Chromium browser:

```bash
playwright install chromium
```

This downloads Chromium (~150MB). Wait for completion.

---

## How to Run

### First Run (QR Code Scan Required)

```bash
python "C:\Users\Iqra Traders\Documents\ai_employee\whatsapp_watcher.py"
```

On first run:
1. Chromium browser will open automatically
2. WhatsApp Web will load with a QR code
3. Open WhatsApp on your phone:
   - **Android**: Menu > Linked devices > Link a device
   - **iPhone**: Settings > Linked devices > Link a device
4. Scan the QR code with your phone
5. Session is saved to `whatsapp_session` folder
6. Script starts monitoring for messages

### Subsequent Runs

Just run the same command - no need to scan QR again:

```bash
python "C:\Users\Iqra Traders\Documents\ai_employee\whatsapp_watcher.py"
```

The browser will open with your saved session already logged in.

---

## What It Does

1. **Checks WhatsApp every 30 seconds** for unread messages
2. **Filters by keywords**: urgent, asap, invoice, payment, help, price, order
3. **Creates task files** in `Needs_Action` folder:
   ```
   WHATSAPP_ContactName_20260321_180000.md
   ```
4. **Tracks processed messages** - no duplicates
5. **Handles errors gracefully** - auto-recovers if WhatsApp disconnects

---

## Example Task File Created

```markdown
---
type: whatsapp
from: John Client
message: Hi, I need urgent help with the invoice payment
received: 2026-03-21 18:00:00
keyword_matched: urgent, invoice, payment
status: pending
---

## WhatsApp Message
From: John Client
Message: Hi, I need urgent help with the invoice payment. 
         Can you send me the details ASAP?

## Suggested Actions
- [ ] Reply to contact
- [ ] Create invoice if needed
- [ ] Follow up tomorrow
```

---

## Keywords Monitored

| Keyword | Purpose |
|---------|---------|
| urgent | High priority messages |
| asap | Time-sensitive requests |
| invoice | Payment/billing related |
| payment | Money transactions |
| help | Support requests |
| price | Pricing inquiries |
| order | Order-related messages |

---

## Stop the Watcher

Press `Ctrl+C` in the terminal.

The browser will close automatically and your session is saved.

---

## Troubleshooting

### "Browser won't launch"
- Make sure Playwright browsers are installed: `playwright install chromium`
- Check if antivirus is blocking Chromium

### "QR code keeps showing"
- Make sure you're scanning with the correct WhatsApp account
- Try logging out of WhatsApp Web on all devices and re-scan
- Delete `whatsapp_session` folder and re-run

### "No messages detected"
- Make sure messages are unread (not opened)
- Check if message contains one of the priority keywords
- WhatsApp Web structure may change - script uses common selectors

### "Session expired"
- Delete `whatsapp_session` folder
- Re-run script and scan QR code again

### "Page keeps reloading"
- Check your internet connection
- WhatsApp Web may require phone to be connected to internet

---

## Tips

1. **Keep browser visible**: Don't minimize the browser window too much
2. **Phone connection**: Your phone needs internet for WhatsApp Web to work
3. **Multiple devices**: If using multiple linked devices, messages may sync differently
4. **Archive old chats**: Keep only active chats visible for faster scanning

---

## Session Storage

Your WhatsApp session is stored in:
```
C:\Users\Iqra Traders\Documents\ai_employee\whatsapp_session\
```

This folder contains:
- Browser cookies
- Local storage
- Authentication tokens

**Never share this folder** - it gives access to your WhatsApp!

---

**Created for: Iqra Traders**
**Silver Tier Feature**
