"""
Gmail Watcher for AI Employee
Monitors Gmail for unread+important emails and creates tasks in Obsidian vault.
Silver Tier Feature
"""

import os
import time
import re
import pickle
from datetime import datetime
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import base64
from email import message_from_bytes

# Load environment variables
load_dotenv(r"C:\Users\Iqra Traders\Documents\ai_employee\.env")

# Configuration
CREDENTIALS_FILE = r"C:\Users\Iqra Traders\Documents\ai_employee\credentials.json"
TOKEN_FILE = r"C:\Users\Iqra Traders\Documents\ai_employee\token.json"
VAULT_NEEDS_ACTION = r"C:\Users\Iqra Traders\Documents\AI_Employee_Vault\Needs_Action"
PROCESSED_IDS_FILE = r"C:\Users\Iqra Traders\Documents\ai_employee\processed_email_ids.txt"
CHECK_INTERVAL = 120  # 2 minutes in seconds

# Gmail API Scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def sanitize_filename(filename):
    """Remove invalid characters from filename."""
    return re.sub(r'[<>:"/\\|?*]', "_", filename)


def load_processed_ids():
    """Load already processed email IDs from file."""
    if os.path.exists(PROCESSED_IDS_FILE):
        with open(PROCESSED_IDS_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)
    return set()


def save_processed_id(email_id):
    """Save a processed email ID to file."""
    with open(PROCESSED_IDS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{email_id}\n")


def get_gmail_service():
    """Authenticate and build Gmail API service."""
    creds = None
    
    # Load existing token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # Refresh or create new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"❌ Credentials file not found: {CREDENTIALS_FILE}")
                print("Please download credentials.json from Google Cloud Console")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save token
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    
    return build("gmail", "v1", credentials=creds)


def decode_snippet(snippet):
    """Decode base64url encoded snippet."""
    if not snippet:
        return ""
    
    # Add padding if needed
    padding = 4 - len(snippet) % 4
    if padding != 4:
        snippet += "=" * padding
    
    try:
        decoded = base64.urlsafe_b64decode(snippet)
        return decoded.decode("utf-8", errors="replace")
    except Exception:
        return snippet


def get_email_body(service, user_id, msg_id):
    """Get the full email body."""
    try:
        message = service.users().messages().get(
            userId=user_id, 
            id=msg_id,
            format="full"
        ).execute()
        
        # Try to get plain text body
        if "payload" in message and "parts" in message["payload"]:
            for part in message["payload"]["parts"]:
                if part["mimeType"] == "text/plain" and "body" in part:
                    data = part["body"].get("data", "")
                    if data:
                        return decode_snippet(data)
        
        # Fallback to snippet
        return message.get("snippet", "")
    
    except Exception as e:
        return f"Error retrieving full body: {e}"


def create_email_task(email_data):
    """Create a markdown task file for an email."""
    # Create safe filename from subject
    safe_subject = sanitize_filename(email_data["subject"])[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"EMAIL_{safe_subject}_{timestamp}.md"
    filepath = os.path.join(VAULT_NEEDS_ACTION, filename)
    
    content = f"""---
type: email
from: {email_data["from"]}
subject: {email_data["subject"]}
received: {email_data["received"]}
priority: high
status: pending
---

## Email Content
{email_data["snippet"]}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward if needed
- [ ] Archive after processing

---
*Created by AI Employee Gmail Watcher*
"""
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"  ❌ Error creating task file: {e}")
        return False


def check_gmail(service):
    """Check for new unread+important emails."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Checking Gmail...")
    
    try:
        # Load processed IDs
        processed_ids = load_processed_ids()
        
        # Search for unread + important emails
        results = service.users().messages().list(
            userId="me",
            q="is:unread is:important",
            maxResults=10
        ).execute()
        
        messages = results.get("messages", [])
        
        if not messages:
            print("  ✅ No new unread+important emails")
            return
        
        print(f"  📧 Found {len(messages)} unread+important email(s)")
        
        new_count = 0
        for msg in messages:
            msg_id = msg["id"]
            
            # Skip already processed
            if msg_id in processed_ids:
                continue
            
            # Get email details
            try:
                message = service.users().messages().get(
                    userId="me", 
                    id=msg_id,
                    format="metadata",
                    metadataHeaders=["From", "Subject", "Date", "Snippet"]
                ).execute()
                
                # Extract headers
                headers = message.get("payload", {}).get("headers", [])
                from_email = ""
                subject = ""
                date = ""
                snippet = message.get("snippet", "")
                
                for header in headers:
                    if header["name"].lower() == "from":
                        from_email = header["value"]
                    elif header["name"].lower() == "subject":
                        subject = header["value"]
                    elif header["name"].lower() == "date":
                        date = header["value"]
                
                # Decode snippet
                snippet = decode_snippet(snippet)
                
                # Create email data dict
                email_data = {
                    "from": from_email,
                    "subject": subject if subject else "(No Subject)",
                    "received": date if date else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "snippet": snippet if snippet else "(No content)"
                }
                
                # Create task file
                if create_email_task(email_data):
                    print(f"  ✅ Created task: {email_data['subject'][:40]}...")
                    save_processed_id(msg_id)
                    new_count += 1
                else:
                    print(f"  ❌ Failed to create task for: {email_data['subject']}")
            
            except Exception as e:
                print(f"  ❌ Error processing message {msg_id}: {e}")
                continue
        
        if new_count > 0:
            print(f"  📋 {new_count} new email task(s) created in Needs_Action")
        
    except HttpError as error:
        print(f"  ❌ Gmail API error: {error}")
        raise
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        raise


def main():
    """Main function to start the Gmail watcher."""
    print("=" * 60)
    print("🤖 AI Employee - Gmail Watcher (Silver Tier)")
    print("=" * 60)
    
    # Ensure vault folder exists
    if not os.path.exists(VAULT_NEEDS_ACTION):
        print(f"Creating folder: {VAULT_NEEDS_ACTION}")
        os.makedirs(VAULT_NEEDS_ACTION)
    
    print(f"\n📂 Vault Needs_Action: {VAULT_NEEDS_ACTION}")
    print(f"⏱️  Check interval: {CHECK_INTERVAL} seconds")
    print(f"📧 Monitoring: UNREAD + IMPORTANT emails")
    print("\nPress Ctrl+C to stop...\n")
    
    # Initial connection
    print("🔑 Connecting to Gmail...")
    service = get_gmail_service()
    
    if not service:
        print("❌ Failed to connect to Gmail. Please check credentials.")
        return
    
    print("✅ Connected to Gmail successfully!")
    
    # Main loop
    retry_count = 0
    max_retries = 5
    
    while True:
        try:
            check_gmail(service)
            retry_count = 0  # Reset retry count on success
            
        except Exception as e:
            retry_count += 1
            print(f"\n⚠️  Error occurred (attempt {retry_count}/{max_retries})")
            
            if retry_count >= max_retries:
                print("❌ Max retries reached. Waiting 5 minutes before retry...")
                time.sleep(300)
                retry_count = 0
            
            print(f"💤 Waiting {CHECK_INTERVAL} seconds before retry...")
            time.sleep(CHECK_INTERVAL)
            
            # Try to reconnect
            try:
                service = get_gmail_service()
                if service:
                    print("✅ Reconnected to Gmail")
                else:
                    print("⚠️  Still unable to connect to Gmail")
            except Exception:
                pass
        
        # Wait for next check
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
