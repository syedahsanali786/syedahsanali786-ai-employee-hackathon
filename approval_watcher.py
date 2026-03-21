"""
Approval Watcher for AI Employee
Handles Human-in-the-Loop approvals for sensitive actions.
Silver Tier Feature
"""

import os
import time
import shutil
import re
from datetime import datetime
from pathlib import Path

# Configuration
VAULT_PATH = r"C:\Users\Iqra Traders\Documents\AI_Employee_Vault"
PENDING_APPROVAL_FOLDER = os.path.join(VAULT_PATH, "Pending_Approval")
APPROVED_FOLDER = os.path.join(VAULT_PATH, "Approved")
REJECTED_FOLDER = os.path.join(VAULT_PATH, "Rejected")
DONE_FOLDER = os.path.join(VAULT_PATH, "Done")
LOGS_FOLDER = os.path.join(VAULT_PATH, "Logs")

# Check interval in seconds
CHECK_INTERVAL = 5

# Track processed files to avoid duplicates
processed_pending = set()
processed_approved = set()


def ensure_folders_exist():
    """Create all required folders if they don't exist."""
    folders = [
        PENDING_APPROVAL_FOLDER,
        APPROVED_FOLDER,
        REJECTED_FOLDER,
        DONE_FOLDER,
        LOGS_FOLDER
    ]
    
    print("\n📁 Checking folders...")
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"  ✅ Created: {folder}")
        else:
            print(f"  📂 Exists: {folder}")


def parse_frontmatter(filepath):
    """Parse the frontmatter from a markdown file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Parse frontmatter
    frontmatter_match = re.search(r'---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not frontmatter_match:
        return {}, content
    
    frontmatter = frontmatter_match.group(1)
    body = content[frontmatter_match.end():].strip()
    
    # Parse metadata
    metadata = {}
    for line in frontmatter.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()
    
    return metadata, body


def create_log_entry(action_type, filename, details=""):
    """Create a log entry for an approval action."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_filename = f"LOG_APPROVAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    log_path = os.path.join(LOGS_FOLDER, log_filename)
    
    log_content = f"""# Log Entry: Approval Action

## Timestamp
{timestamp}

## Action Type
{action_type}

## File
{filename}

## Details
{details if details else "N/A"}

## Status
✅ Processed

---
*Logged by AI Employee Approval Watcher*
"""
    
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(log_content)
    
    print(f"  📋 Log entry created: {log_filename}")
    return log_path


def check_pending_approvals():
    """Check for new files in Pending_Approval folder."""
    if not os.path.exists(PENDING_APPROVAL_FOLDER):
        return
    
    files = [f for f in os.listdir(PENDING_APPROVAL_FOLDER) if f.endswith('.md')]
    
    for filename in files:
        if filename in processed_pending:
            continue
        
        filepath = os.path.join(PENDING_APPROVAL_FOLDER, filename)
        
        print("\n" + "=" * 70)
        print("⚠️  APPROVAL NEEDED")
        print("=" * 70)
        print(f"📄 File: {filename}")
        print(f"📁 Location: {PENDING_APPROVAL_FOLDER}")
        print("=" * 70)
        
        # Read and display file content
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            print("\n📝 FILE CONTENT:")
            print("-" * 70)
            print(content)
            print("-" * 70)
            
            # Parse metadata for additional info
            metadata, body = parse_frontmatter(filepath)
            
            if metadata:
                print("\n📊 METADATA:")
                for key, value in metadata.items():
                    print(f"  • {key}: {value}")
            
            print("\n" + "=" * 70)
            print("💡 ACTION REQUIRED:")
            print("  To Approve: Move file to /Approved folder")
            print("  To Reject:  Move file to /Rejected folder")
            print("=" * 70)
            
            # Mark as processed (shown)
            processed_pending.add(filename)
            
        except Exception as e:
            print(f"❌ Error reading file: {e}")


def check_approved_files():
    """Check for new files in Approved folder and execute actions."""
    if not os.path.exists(APPROVED_FOLDER):
        return
    
    files = [f for f in os.listdir(APPROVED_FOLDER) if f.endswith('.md')]
    
    for filename in files:
        if filename in processed_approved:
            continue
        
        filepath = os.path.join(APPROVED_FOLDER, filename)
        
        print("\n" + "=" * 70)
        print("✅ APPROVED: Executing action")
        print("=" * 70)
        print(f"📄 File: {filename}")
        
        try:
            # Read file
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Parse metadata
            metadata, body = parse_frontmatter(filepath)
            
            if not metadata:
                print("⚠️  No metadata found in file")
                continue
            
            # Get action type
            action_type = metadata.get('type', 'unknown')
            action = metadata.get('action', 'unspecified')
            status = metadata.get('status', 'pending')
            
            print(f"  • Type: {action_type}")
            print(f"  • Action: {action}")
            print(f"  • Status: {status}")
            
            # Execute based on type
            print("\n🔧 EXECUTING ACTION...")
            
            if action_type == "approval_request":
                print(f"  ✅ Processing approval request: {action}")
                
                # Handle specific actions
                if action == "send_email":
                    recipient = metadata.get('recipient', 'Unknown')
                    amount = metadata.get('amount', '0')
                    print(f"  📧 Would send email to: {recipient}")
                    print(f"  💰 Amount: Rs. {amount}")
                    print(f"  ✅ Action logged (email sending would be implemented here)")
                
                elif action == "payment":
                    recipient = metadata.get('recipient', 'Unknown')
                    amount = metadata.get('amount', '0')
                    print(f"  💰 Processing payment to: {recipient}")
                    print(f"  💰 Amount: Rs. {amount}")
                    print(f"  ✅ Payment logged (payment processing would be implemented here)")
                
                elif action == "invoice":
                    client = metadata.get('client', 'Unknown')
                    amount = metadata.get('amount', '0')
                    print(f"  📄 Creating invoice for: {client}")
                    print(f"  💰 Amount: Rs. {amount}")
                    print(f"  ✅ Invoice creation logged")
                
                else:
                    print(f"  ⚙️  Generic action: {action}")
                    print(f"  ✅ Action logged for execution")
            
            else:
                print(f"  ⚙️  Unknown type: {action_type}")
                print(f"  ✅ Logged for manual review")
            
            # Create log entry
            log_details = f"Type: {action_type}\nAction: {action}\nContent: {body[:200]}"
            create_log_entry("APPROVED", filename, log_details)
            
            # Move to Done folder
            print("\n📁 Moving to Done folder...")
            
            if not os.path.exists(DONE_FOLDER):
                os.makedirs(DONE_FOLDER)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"APPROVED_{filename.replace('.md', '')}_{timestamp}.md"
            dest_path = os.path.join(DONE_FOLDER, new_filename)
            
            shutil.move(filepath, dest_path)
            print(f"  ✅ Moved to: {new_filename}")
            
            # Mark as processed
            processed_approved.add(filename)
            
            print("\n" + "=" * 70)
            print("✅ APPROVAL EXECUTED SUCCESSFULLY!")
            print("=" * 70)
            
        except Exception as e:
            print(f"❌ Error processing approved file: {e}")
            print("💡 File left in Approved folder for manual review")


def check_rejected_files():
    """Check for new files in Rejected folder and log them."""
    if not os.path.exists(REJECTED_FOLDER):
        return
    
    files = [f for f in os.listdir(REJECTED_FOLDER) if f.endswith('.md')]
    
    for filename in files:
        if filename in processed_approved:  # Use same tracking
            continue
        
        filepath = os.path.join(REJECTED_FOLDER, filename)
        
        print("\n" + "=" * 70)
        print("❌ REJECTED: Logging rejection")
        print("=" * 70)
        print(f"📄 File: {filename}")
        
        try:
            # Read file
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Parse metadata
            metadata, body = parse_frontmatter(filepath)
            
            if metadata:
                action_type = metadata.get('type', 'unknown')
                action = metadata.get('action', 'unspecified')
                print(f"  • Type: {action_type}")
                print(f"  • Action: {action}")
            
            # Create log entry
            log_details = f"REJECTED\nContent: {body[:200]}"
            create_log_entry("REJECTED", filename, log_details)
            
            # Move to Done folder
            print("\n📁 Moving to Done folder...")
            
            if not os.path.exists(DONE_FOLDER):
                os.makedirs(DONE_FOLDER)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"REJECTED_{filename.replace('.md', '')}_{timestamp}.md"
            dest_path = os.path.join(DONE_FOLDER, new_filename)
            
            shutil.move(filepath, dest_path)
            print(f"  ✅ Moved to: {new_filename}")
            
            # Mark as processed
            processed_approved.add(filename)
            
            print("\n" + "=" * 70)
            print("❌ REJECTION LOGGED")
            print("=" * 70)
            
        except Exception as e:
            print(f"❌ Error processing rejected file: {e}")


def create_test_approval_file():
    """Create a test approval file for demonstration."""
    test_file_path = os.path.join(PENDING_APPROVAL_FOLDER, "TEST_approval.md")
    
    # Don't overwrite if exists
    if os.path.exists(test_file_path):
        print(f"\n📝 Test approval file already exists: TEST_approval.md")
        return
    
    test_content = """---
type: approval_request
action: send_email
amount: 500
recipient: Test Client
status: pending
created: today
---

## Action Required
Send invoice email to Test Client for Rs. 500

## To Approve
Move this file to /Approved folder

## To Reject  
Move this file to /Rejected folder
"""
    
    try:
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(test_content)
        print(f"\n✅ Created test approval file: TEST_approval.md")
    except Exception as e:
        print(f"❌ Error creating test file: {e}")


def main():
    """Main function to run the approval watcher."""
    print("=" * 70)
    print("🤖 AI Employee - Approval Watcher (Silver Tier)")
    print("=" * 70)
    print("\nHuman-in-the-Loop Approval System")
    print("=" * 70)
    
    # Ensure folders exist
    ensure_folders_exist()
    
    # Create test approval file
    create_test_approval_file()
    
    print("\n" + "=" * 70)
    print("📂 MONITORING FOLDERS:")
    print("=" * 70)
    print(f"  ⏳ Pending:  {PENDING_APPROVAL_FOLDER}")
    print(f"  ✅ Approved: {APPROVED_FOLDER}")
    print(f"  ❌ Rejected: {REJECTED_FOLDER}")
    print("=" * 70)
    print(f"\n⏱️  Check interval: {CHECK_INTERVAL} seconds")
    print("\nPress Ctrl+C to stop...\n")
    
    # Main loop
    while True:
        try:
            # Check pending approvals
            check_pending_approvals()
            
            # Check approved files
            check_approved_files()
            
            # Check rejected files
            check_rejected_files()
            
            # Wait before next check
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n" + "=" * 70)
            print("⏹️  Approval Watcher stopped by user")
            print("=" * 70)
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
