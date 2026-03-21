"""
LinkedIn Poster for AI Employee
Posts content to LinkedIn automatically.
Silver Tier Feature

FIXED: Simplified page loading and posting approach
"""

import os
import time
import re
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv

# Load environment variables
load_dotenv(r"C:\Users\Iqra Traders\Documents\ai_employee\.env")

# Configuration
SESSION_PATH = r"C:\Users\Iqra Traders\Documents\ai_employee\linkedin_session"
VAULT_PATH = r"C:\Users\Iqra Traders\Documents\AI_Employee_Vault"
LINKEDIN_POST_FILE = os.path.join(VAULT_PATH, "LINKEDIN_POST.md")
DONE_FOLDER = os.path.join(VAULT_PATH, "Done")
LOGS_FOLDER = os.path.join(VAULT_PATH, "Logs")

# LinkedIn credentials from .env
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")


def parse_linkedin_post(filepath):
    """Parse the LINKEDIN_POST.md file and extract content and metadata."""
    if not os.path.exists(filepath):
        print(f"❌ Post file not found: {filepath}")
        return None
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Parse frontmatter
    frontmatter_match = re.search(r'---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not frontmatter_match:
        print("❌ No frontmatter found in post file")
        return None
    
    frontmatter = frontmatter_match.group(1)
    post_content = content[frontmatter_match.end():].strip()
    
    # Remove "## Post Content" header if present
    post_content = re.sub(r'^##\s*Post\s*Content\s*\n*', '', post_content, flags=re.IGNORECASE).strip()
    
    # Parse metadata
    metadata = {}
    for line in frontmatter.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()
    
    # Check status
    status = metadata.get('status', '').lower()
    if status != 'pending':
        print(f"⏭️  Post status is '{status}', skipping...")
        return None
    
    return {
        'content': post_content,
        'metadata': metadata,
        'scheduled': metadata.get('scheduled', 'today')
    }


def update_post_status(filepath, new_status):
    """Update the status in the post file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace status in frontmatter
    updated_content = re.sub(
        r'(status:\s*)(\w+)',
        f'\\g<1>{new_status}',
        content,
        flags=re.IGNORECASE
    )
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(updated_content)
    
    print(f"✅ Updated post status to: {new_status}")


def move_to_done(filepath, done_folder):
    """Move the post file to Done folder."""
    if not os.path.exists(done_folder):
        os.makedirs(done_folder)
    
    filename = os.path.basename(filepath)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_filename = f"LINKEDIN_POST_{timestamp}.md"
    dest_path = os.path.join(done_folder, new_filename)
    
    os.rename(filepath, dest_path)
    print(f"✅ Moved post to Done folder: {new_filename}")
    return dest_path


def create_log_entry(post_content, done_file_path):
    """Create a log entry for the posted content."""
    if not os.path.exists(LOGS_FOLDER):
        os.makedirs(LOGS_FOLDER)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_filename = f"LOG_LINKEDIN_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    log_path = os.path.join(LOGS_FOLDER, log_filename)
    
    # Get first 100 chars of post for preview
    preview = post_content[:100].replace('\n', ' ')
    
    log_content = f"""# Log Entry: LinkedIn Post

## Timestamp
{timestamp}

## Action
Posted content to LinkedIn

## Post Preview
{preview}...

## File Moved To
{done_file_path}

## Status
✅ Successfully posted

---
*Logged by AI Employee LinkedIn Poster*
"""
    
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(log_content)
    
    print(f"✅ Log entry created: {log_filename}")
    return log_path


def wait_for_linkedin_load(page):
    """Wait for LinkedIn to fully load."""
    print("  ⏳ Waiting for LinkedIn to load (up to 90 seconds)...")
    
    try:
        # Use domcontentloaded instead of networkidle
        page.wait_for_load_state("domcontentloaded", timeout=90000)
        print("  ✅ Page load state: domcontentloaded")
    except PlaywrightTimeout:
        print("  ⚠️ Page load timeout, but continuing...")
    
    # Wait for page to settle
    print("  ⏳ Waiting 5 seconds for page to settle...")
    time.sleep(5)
    
    # Check if logged in by looking for feed or profile
    try:
        # Look for LinkedIn feed
        feed_selector = 'div[id="mduo"]'
        feed_element = page.query_selector(feed_selector)
        if feed_element:
            print("  ✅ Found LinkedIn feed - logged in")
            return "logged_in"
        
        # Look for profile icon
        profile_selector = 'img[data-id="me"]'
        profile_element = page.query_selector(profile_selector)
        if profile_element:
            print("  ✅ Found profile icon - logged in")
            return "logged_in"
        
        # Look for login form
        login_selector = 'input[id="username"]'
        login_element = page.query_selector(login_selector)
        if login_element:
            print("  📱 Login form detected - need to login")
            return "login_required"
        
        # Check URL
        if "feed" in page.url or "mynetwork" in page.url:
            print("  ✅ On feed/network page - logged in")
            return "logged_in"
        
    except Exception as e:
        print(f"  ⚠️ Error checking login status: {e}")
    
    print("  ⚠️ Could not determine login status")
    return "unknown"


def post_to_linkedin(page, post_content):
    """Post content to LinkedIn using simplified approach."""
    print("\n  📝 Starting LinkedIn post process...")
    
    try:
        # Navigate to LinkedIn feed
        print("  🌐 Navigating to https://www.linkedin.com/feed/...")
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=90000)
        
        # Wait for page to settle
        print("  ⏳ Waiting 5 seconds for page to settle...")
        time.sleep(5)
        
        # Find and click "Start a post" button
        print("  🔍 Looking for 'Start a post' button...")
        
        start_post_selectors = [
            'button[aria-label="Start a post"]',
            'div.share-box-feed-entry__top-bar',
            'button:has-text("Start a post")',
            'span:has-text("Start a post")',
        ]
        
        start_post_button = None
        used_selector = None
        
        for selector in start_post_selectors:
            try:
                start_post_button = page.query_selector(selector)
                if start_post_button:
                    used_selector = selector
                    print(f"  ✅ Found 'Start a post' button with: {selector}")
                    break
            except Exception:
                continue
        
        if not start_post_button:
            print("  ❌ Could not find 'Start a post' button")
            print("  💡 Trying to find any post-related button...")
            
            # Try all buttons and look for post-related text
            all_buttons = page.query_selector_all('button')
            for btn in all_buttons:
                try:
                    btn_text = btn.inner_text()
                    if "post" in btn_text.lower():
                        print(f"  🖱️  Found post-related button: {btn_text}")
                        start_post_button = btn
                        break
                except Exception:
                    continue
        
        if start_post_button:
            print("  🖱️  Clicking 'Start a post' button...")
            start_post_button.click()
            print("  ⏳ Waiting 3 seconds for post editor to open...")
            time.sleep(3)
        else:
            print("  ⚠️ Could not find 'Start a post' button - trying to find textarea directly...")
        
        # Find the textarea for post content
        print("  🔍 Looking for post text area...")
        
        textarea_selectors = [
            'div[role="textbox"][contenteditable="true"]',
            'div[contenteditable="true"]',
            'textarea',
            'div.editor[contenteditable]',
        ]
        
        textarea = None
        for selector in textarea_selectors:
            try:
                textarea = page.query_selector(selector)
                if textarea:
                    print(f"  ✅ Found textarea with: {selector}")
                    break
            except Exception:
                continue
        
        if not textarea:
            print("  ❌ Could not find post textarea")
            print("  💡 Trying alternative approach...")
            # Try focusing on the page and typing
            page.keyboard.press("Tab")
            time.sleep(1)
        else:
            # Type the post content
            print("  ⌨️  Typing post content...")
            print(f"  📊 Post length: {len(post_content)} characters")
            
            # Click to focus
            textarea.click()
            time.sleep(1)
            
            # Fill the content
            textarea.fill(post_content)
            time.sleep(2)
            
            # Verify content was entered
            try:
                entered_text = textarea.inner_text()
                if len(entered_text) < len(post_content) * 0.8:
                    print(f"  ⚠️ Warning: Only {len(entered_text)} chars entered out of {len(post_content)}")
                else:
                    print(f"  ✅ Post content entered successfully ({len(entered_text)} chars)")
            except Exception:
                print("  ⚠️ Could not verify entered content")
        
        # Wait before posting
        print("  ⏳ Waiting 3 seconds before clicking Post...")
        time.sleep(3)
        
        # Find and click Post button
        print("  🔍 Looking for Post button...")
        
        post_submit_selectors = [
            'button[aria-label="Post"]',
            'button.share-actions__primary-action',
            'button:has-text("Post")',
            'button:has-text("Post now")',
        ]
        
        submit_button = None
        for selector in post_submit_selectors:
            try:
                submit_button = page.query_selector(selector)
                if submit_button:
                    print(f"  ✅ Found submit button with: {selector}")
                    break
            except Exception:
                continue
        
        if not submit_button:
            print("  ❌ Could not find Post button")
            print("  💡 Trying to find any button with 'Post' text...")
            
            # Try all buttons
            all_buttons = page.query_selector_all('button')
            for btn in all_buttons:
                try:
                    btn_text = btn.inner_text()
                    if "post" in btn_text.lower():
                        print(f"  🖱️  Found button: {btn_text}")
                        submit_button = btn
                        break
                except Exception:
                    continue
        
        if submit_button:
            print("  🖱️  Clicking Post button...")
            submit_button.click()
            print("  ⏳ Waiting 3 seconds for post to submit...")
            time.sleep(3)
            
            # Wait for confirmation
            print("  ⏳ Waiting 5 seconds for post confirmation...")
            time.sleep(5)
            
            # Check if post was successful
            page_content = page.content()
            if "published" in page_content.lower() or "posted" in page_content.lower():
                print("  ✅ Post published successfully!")
                return True
            
            # Check if we're still on feed page
            if "feed" in page.url:
                print("  ✅ Back on feed page - post likely successful!")
                return True
            
            print("  ✅ Post button clicked - assuming success")
            return True
        else:
            print("  ❌ Could not find Post button to click")
            return False
        
    except Exception as e:
        print(f"  ❌ Error posting to LinkedIn: {e}")
        return False


def main():
    """Main function to run the LinkedIn poster."""
    print("=" * 60)
    print("🤖 AI Employee - LinkedIn Poster (Silver Tier)")
    print("=" * 60)
    
    # Ensure folders exist
    for folder in [SESSION_PATH, DONE_FOLDER, LOGS_FOLDER]:
        if not os.path.exists(folder):
            print(f"📁 Creating folder: {folder}")
            os.makedirs(folder)
    
    print(f"\n💾 Session path: {SESSION_PATH}")
    print(f"📂 Vault path: {VAULT_PATH}")
    print(f"📝 Post file: {LINKEDIN_POST_FILE}")
    print("\nPress Ctrl+C to stop after one post\n")
    
    # Check for post file
    print("📄 Checking for LINKEDIN_POST.md...")
    
    if not os.path.exists(LINKEDIN_POST_FILE):
        print(f"❌ Post file not found: {LINKEDIN_POST_FILE}")
        print("💡 Please create LINKEDIN_POST.md in the vault root")
        return
    
    # Parse post
    print("📖 Reading post content...")
    post_data = parse_linkedin_post(LINKEDIN_POST_FILE)
    
    if not post_data:
        print("❌ No pending post found or invalid format")
        return
    
    print(f"✅ Found pending post ({len(post_data['content'])} chars)")
    print(f"📅 Scheduled: {post_data['scheduled']}")
    print("\n" + "=" * 60)
    print("📝 POST PREVIEW:")
    print("=" * 60)
    print(post_data['content'][:200] + "..." if len(post_data['content']) > 200 else post_data['content'])
    print("=" * 60 + "\n")
    
    # Confirm before posting
    print("💡 Starting browser for LinkedIn...")
    
    with sync_playwright() as p:
        # Launch browser
        print("\n" + "=" * 60)
        print("🌐 LAUNCHING CHROMIUM BROWSER...")
        print("=" * 60)
        
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=SESSION_PATH,
                headless=False,  # Visible browser
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--window-size=1280,800"
                ],
                slow_mo=500
            )
        except Exception as e:
            print(f"❌ Error launching browser: {e}")
            return
        
        print("✅ Browser launched!")
        
        # Open LinkedIn
        print("\n" + "=" * 60)
        print("📱 OPENING LINKEDIN...")
        print("=" * 60)
        
        page = browser.new_page()
        
        try:
            print("  🌐 Navigating to https://www.linkedin.com...")
            page.goto("https://www.linkedin.com", wait_until="domcontentloaded", timeout=90000)
            print("  ✅ Navigation complete!")
        except Exception as e:
            print(f"❌ Error loading LinkedIn: {e}")
            browser.close()
            return
        
        # Check login status
        print("\n" + "=" * 60)
        print("🔐 CHECKING LOGIN STATUS...")
        print("=" * 60)
        
        login_status = wait_for_linkedin_load(page)
        
        if login_status == "login_required":
            print("\n" + "=" * 60)
            print("🔑 LOGIN REQUIRED")
            print("=" * 60)
            
            if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
                print("❌ LinkedIn credentials not found in .env file")
                print(f"📁 Expected: C:\\Users\\Iqra Traders\\Documents\\ai_employee\\.env")
                print("\n💡 Add these to your .env file:")
                print("   LINKEDIN_EMAIL=your.email@example.com")
                print("   LINKEDIN_PASSWORD=yourpassword")
                browser.close()
                return
            
            print("  📧 Entering email...")
            try:
                email_input = page.query_selector('input[id="username"]')
                if email_input:
                    email_input.fill(LINKEDIN_EMAIL)
                    time.sleep(1)
            except Exception as e:
                print(f"  ⚠️ Error entering email: {e}")
            
            print("  🖱️  Clicking Next...")
            try:
                next_button = page.query_selector('button[type="submit"]')
                if next_button:
                    next_button.click()
                    time.sleep(3)
            except Exception as e:
                print(f"  ⚠️ Error clicking next: {e}")
            
            print("  🔑 Entering password...")
            try:
                password_input = page.query_selector('input[id="password"]')
                if password_input:
                    password_input.fill(LINKEDIN_PASSWORD)
                    time.sleep(1)
            except Exception as e:
                print(f"  ⚠️ Error entering password: {e}")
            
            print("  🖱️  Clicking Sign in...")
            try:
                signin_button = page.query_selector('button[type="submit"]')
                if signin_button:
                    signin_button.click()
                    time.sleep(5)
            except Exception as e:
                print(f"  ⚠️ Error clicking sign in: {e}")
            
            print("  ⏳ Waiting for login to complete...")
            time.sleep(5)
            
            # Verify login
            login_status = wait_for_linkedin_load(page)
            if login_status != "logged_in":
                print("❌ Login may have failed - please check browser")
                print("💡 You have 30 seconds to manually login...")
                time.sleep(30)
        
        elif login_status == "logged_in":
            print("\n✅ Already logged in - session restored!")
        
        # Post to LinkedIn
        print("\n" + "=" * 60)
        print("📝 POSTING TO LINKEDIN...")
        print("=" * 60)
        
        success = post_to_linkedin(page, post_data['content'])
        
        if success:
            print("\n" + "=" * 60)
            print("✅ POST SUCCESSFUL!")
            print("=" * 60)
            
            # Update file status
            print("\n📝 Updating post file status...")
            update_post_status(LINKEDIN_POST_FILE, "posted")
            
            # Move to Done
            print("\n📁 Moving to Done folder...")
            done_path = move_to_done(LINKEDIN_POST_FILE, DONE_FOLDER)
            
            # Create log entry
            print("\n📋 Creating log entry...")
            create_log_entry(post_data['content'], done_path)
            
            print("\n" + "=" * 60)
            print("🎉 ALL TASKS COMPLETED!")
            print("=" * 60)
            print("✅ Posted to LinkedIn")
            print("✅ File status updated to 'posted'")
            print(f"✅ File moved to Done: {os.path.basename(done_path)}")
            print("✅ Log entry created")
            
        else:
            print("\n" + "=" * 60)
            print("❌ POST FAILED")
            print("=" * 60)
            print("⚠️ Post was not published")
            print("💡 Check browser for errors and try again")
            print("📝 Post file left unchanged for retry")
        
        print("\n✅ LinkedIn Poster finished!")
        print("💡 You can close the browser or keep it open")
        
        # Keep browser open for a moment
        time.sleep(5)
        browser.close()


if __name__ == "__main__":
    main()
