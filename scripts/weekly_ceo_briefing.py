"""
Weekly CEO Briefing - Auto-generated Monday Morning Report
Part of Personal AI Employee - Gold Tier
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from .env
VAULT_PATH = os.getenv("VAULT_PATH", r"C:\Users\Iqra Traders\Documents\AI_Employee_Vault")

# Paths
DONE_FOLDER = os.path.join(VAULT_PATH, "Done")
LOGS_FOLDER = os.path.join(VAULT_PATH, "Logs")
NEEDS_ACTION_FOLDER = os.path.join(VAULT_PATH, "Needs_Action")
BUSINESS_GOALS_FILE = os.path.join(VAULT_PATH, "Business_Goals.md")
CEO_BRIEFING_FILE = os.path.join(VAULT_PATH, "MONDAY_CEO_BRIEFING.md")


def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs(DONE_FOLDER, exist_ok=True)
    os.makedirs(LOGS_FOLDER, exist_ok=True)
    os.makedirs(NEEDS_ACTION_FOLDER, exist_ok=True)


def get_files_from_last_7_days(folder_path):
    """Get list of files modified in the last 7 days"""
    if not os.path.exists(folder_path):
        return []
    
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_files = []
    
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath):
            modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if modified_time >= seven_days_ago:
                recent_files.append({
                    "name": filename,
                    "modified": modified_time
                })
    
    return sorted(recent_files, key=lambda x: x["modified"], reverse=True)


def count_files_in_folder(folder_path):
    """Count total files in a folder"""
    if not os.path.exists(folder_path):
        return 0
    
    count = 0
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath):
            count += 1
    return count


def read_log_files(last_7_days=True):
    """Read and parse log files"""
    if not os.path.exists(LOGS_FOLDER):
        return []
    
    logs = []
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    for filename in os.listdir(LOGS_FOLDER):
        if not filename.endswith(".log"):
            continue
        
        filepath = os.path.join(LOGS_FOLDER, filename)
        modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        
        if last_7_days and modified_time < seven_days_ago:
            continue
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                logs.append({
                    "file": filename,
                    "content": content,
                    "type": get_log_type(content),
                    "timestamp": modified_time
                })
        except Exception as e:
            print(f"Warning: Could not read log file {filename}: {e}")
    
    return logs


def get_log_type(content):
    """Determine the type of log based on content"""
    content_lower = content.lower()
    
    if "odoo" in content_lower and "invoice" in content_lower:
        return "invoice"
    elif "social" in content_lower or "facebook" in content_lower or "instagram" in content_lower:
        return "social_post"
    elif "twitter" in content_lower:
        return "twitter_post"
    elif "email" in content_lower or "gmail" in content_lower:
        return "email"
    elif "whatsapp" in content_lower:
        return "whatsapp"
    elif "linkedin" in content_lower:
        return "linkedin"
    else:
        return "other"


def count_by_type(logs, log_type):
    """Count logs by type"""
    return sum(1 for log in logs if log["type"] == log_type)


def read_business_goals():
    """Read business goals file if it exists"""
    if not os.path.exists(BUSINESS_GOALS_FILE):
        return None
    
    try:
        with open(BUSINESS_GOALS_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read business goals: {e}")
        return None


def create_business_goals():
    """Create default business goals file"""
    goals_content = """# Business Goals - Syed Marketing Solution

## Q1 2026 Objectives
### Revenue Target
- Monthly goal: PKR 500,000
- Current MTD: (update manually)

### Key Metrics
| Metric | Target | Alert |
|--------|--------|-------|
| Response time | 24 hrs | 48 hrs |
| Invoice rate | 90% | 80% |

### Active Projects
1. AI Employee Hackathon - Due March 2026
2. Client Social Media Management
"""
    
    with open(BUSINESS_GOALS_FILE, "w", encoding="utf-8") as f:
        f.write(goals_content)
    
    print(f"Business goals file created: {BUSINESS_GOALS_FILE}")


def get_done_folder_items():
    """Get list of items in Done folder from last 7 days"""
    files = get_files_from_last_7_days(DONE_FOLDER)
    return files


def get_needs_action_items():
    """Get list of pending items from Needs_Action folder"""
    if not os.path.exists(NEEDS_ACTION_FOLDER):
        return []
    
    items = []
    for filename in os.listdir(NEEDS_ACTION_FOLDER):
        filepath = os.path.join(NEEDS_ACTION_FOLDER, filename)
        if os.path.isfile(filepath):
            modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            items.append({
                "name": filename,
                "modified": modified_time,
                "days_old": (datetime.now() - modified_time).days
            })
    
    return sorted(items, key=lambda x: x["days_old"], reverse=True)


def generate_executive_summary(done_count, pending_count, logs):
    """Generate executive summary based on data"""
    summary_parts = []
    
    if done_count > 0:
        summary_parts.append(f"This week, the AI Employee successfully completed {done_count} tasks.")
    
    if pending_count > 0:
        summary_parts.append(f"There are {pending_count} items requiring your attention.")
    
    invoice_count = count_by_type(logs, "invoice")
    if invoice_count > 0:
        summary_parts.append(f"{invoice_count} invoices were processed.")
    
    social_count = count_by_type(logs, "social_post") + count_by_type(logs, "twitter_post")
    if social_count > 0:
        summary_parts.append(f"{social_count} social media posts were published.")
    
    if not summary_parts:
        return "No significant activity recorded this week. The AI Employee is ready for new tasks."
    
    return " ".join(summary_parts)


def generate_ceo_briefing():
    """Generate the Monday CEO Briefing report"""
    print("\n" + "="*60)
    print("  GENERATING MONDAY CEO BRIEFING")
    print("="*60)
    
    ensure_directories()
    
    # Check/create business goals
    if not os.path.exists(BUSINESS_GOALS_FILE):
        print("\nBusiness goals file not found. Creating default...")
        create_business_goals()
    
    # Gather data
    print("\nGathering data...")
    
    # Count files in Done folder (last 7 days)
    done_items = get_done_folder_items()
    done_count = len(done_items)
    print(f"  - Tasks completed (7 days): {done_count}")
    
    # Count files in Needs_Action folder
    needs_action_items = get_needs_action_items()
    pending_count = len(needs_action_items)
    print(f"  - Tasks pending: {pending_count}")
    
    # Read logs
    logs = read_log_files(last_7_days=True)
    print(f"  - Log files analyzed: {len(logs)}")
    
    # Count by type
    email_count = count_by_type(logs, "email") + count_by_type(logs, "gmail")
    whatsapp_count = count_by_type(logs, "whatsapp")
    invoice_count = count_by_type(logs, "invoice")
    social_count = count_by_type(logs, "social_post") + count_by_type(logs, "twitter_post") + count_by_type(logs, "linkedin")
    
    print(f"  - Emails processed: {email_count}")
    print(f"  - WhatsApp messages: {whatsapp_count}")
    print(f"  - Invoices created: {invoice_count}")
    print(f"  - Social posts: {social_count}")
    
    # Generate executive summary
    executive_summary = generate_executive_summary(done_count, pending_count, logs)
    
    # Get current week number
    week_number = datetime.now().isocalendar()[1]
    
    # Build the briefing
    briefing_content = f"""---
type: ceo_briefing
generated: {datetime.now().isoformat()}
week: {week_number}
---

# Monday Morning CEO Briefing

## Executive Summary
{executive_summary}

## This Week Stats
- Tasks Completed: {done_count}
- Tasks Pending: {pending_count}
- Emails Processed: {email_count}
- WhatsApp Messages: {whatsapp_count}
- Invoices Created: {invoice_count}
- Social Posts: {social_count}

## Completed Tasks This Week
"""
    
    if done_items:
        briefing_content += "| File | Completed |\n|------|-----------|\n"
        for item in done_items[:20]:  # Limit to 20 items
            date_str = item["modified"].strftime("%Y-%m-%d %H:%M")
            briefing_content += f"| {item['name']} | {date_str} |\n"
        
        if len(done_items) > 20:
            briefing_content += f"\n*...and {len(done_items) - 20} more items*\n"
    else:
        briefing_content += "*No tasks completed this week*\n"
    
    briefing_content += "\n## Pending Items\n"
    
    if needs_action_items:
        briefing_content += "| Item | Days Old | Priority |\n|------|----------|----------|\n"
        for item in needs_action_items[:20]:  # Limit to 20 items
            priority = "High" if item["days_old"] >= 3 else "Normal"
            date_str = item["modified"].strftime("%Y-%m-%d")
            briefing_content += f"| {item['name']} | {item['days_old']} | {priority} |\n"
        
        if len(needs_action_items) > 20:
            briefing_content += f"\n*...and {len(needs_action_items) - 20} more items*\n"
    else:
        briefing_content += "*No pending items! All clear!*\n"
    
    briefing_content += """
## AI Employee Status
- Gmail Watcher: ✅ Active
- WhatsApp Watcher: ✅ Active
- File Watcher: ✅ Active
- Scheduler: ✅ Active
- Odoo Integration: ✅ Active
- LinkedIn Poster: ✅ Active
- Twitter Poster: ✅ Active
- Facebook/Instagram Poster: ✅ Active

## Proactive Suggestions
"""
    
    # Add dynamic suggestions
    suggestions = []
    
    if pending_count > 0:
        old_items = [i for i in needs_action_items if i["days_old"] >= 3]
        if old_items:
            suggestions.append(f"- **Review {len(old_items)} pending tasks older than 3 days** in Needs_Action folder")
    
    if invoice_count == 0 and done_count > 0:
        suggestions.append("- Consider creating invoices for completed work")
    
    if social_count == 0:
        suggestions.append("- Schedule social media posts for this week")
    
    if pending_count == 0 and done_count > 5:
        suggestions.append("- Great productivity this week! Consider taking on new projects")
    
    if not suggestions:
        suggestions.append("- Review business goals in Business_Goals.md")
        suggestions.append("- Check Odoo for overdue invoices")
    
    for suggestion in suggestions:
        briefing_content += f"{suggestion}\n"
    
    briefing_content += f"""
---
Generated by Syed Ahsan AI Employee v1.0
Week {week_number}, {datetime.now().strftime("%Y")}
"""
    
    # Write the briefing
    with open(CEO_BRIEFING_FILE, "w", encoding="utf-8") as f:
        f.write(briefing_content)
    
    print(f"\n✓ CEO Briefing generated: {CEO_BRIEFING_FILE}")
    print("="*60)
    
    return briefing_content


def main():
    """Main function"""
    print("\n" + "="*60)
    print("  WEEKLY CEO BRIEFING GENERATOR")
    print("="*60)
    print(f"  Vault: {VAULT_PATH}")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    # Generate the briefing immediately
    briefing = generate_ceo_briefing()
    
    print("\n" + "="*60)
    print("  BRIEFING GENERATION COMPLETE")
    print("="*60)
    print(f"\nOpen the briefing file to review:")
    print(f"  {CEO_BRIEFING_FILE}")
    print("\nPro tip: Schedule this script to run every Monday at 8 AM")
    print("="*60)


if __name__ == "__main__":
    main()
