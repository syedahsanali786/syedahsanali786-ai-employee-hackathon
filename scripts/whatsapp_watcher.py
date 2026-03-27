"""
WhatsApp Watcher for AI Employee
Monitors WhatsApp Web for unread messages with priority keywords.
Silver Tier Feature

FIXED: Updated selectors for chat scanning + Debug mode
"""

import os
import time
import re
import json
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
SESSION_PATH = r"C:\Users\Iqra Traders\Documents\ai_employee\whatsapp_session"
VAULT_NEEDS_ACTION = r"C:\Users\Iqra Traders\Documents\AI_Employee_Vault\Needs_Action"
CHECK_INTERVAL = 30  # 30 seconds
PROCESSED_MESSAGES_FILE = r"C:\Users\Iqra Traders\Documents\ai_employee\processed_whatsapp_messages.txt"
DEBUG_SCREENSHOT_PATH = r"C:\Users\Iqra Traders\Documents\ai_employee\whatsapp_debug.png"

# Keywords to watch for (case-insensitive)
KEYWORDS = ["urgent", "asap", "invoice", "payment", "help", "price", "order"]

# Debug mode - set to True to enable detailed HTML output
DEBUG_MODE = True


def sanitize_filename(filename):
    """Remove invalid characters from filename."""
    return re.sub(r'[<>:"/\\|?*]', "_", filename)


def load_processed_messages():
    """Load already processed message IDs from file."""
    if os.path.exists(PROCESSED_MESSAGES_FILE):
        with open(PROCESSED_MESSAGES_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)
    return set()


def save_processed_message(msg_id):
    """Save a processed message ID to file."""
    with open(PROCESSED_MESSAGES_FILE, "a", encoding="utf-8") as f:
        f.write(f"{msg_id}\n")


def check_keywords(text):
    """Check if text contains any priority keywords."""
    text_lower = text.lower()
    found_keywords = [kw for kw in KEYWORDS if kw in text_lower]
    return found_keywords


def create_whatsapp_task(message_data):
    """Create a markdown task file for a WhatsApp message."""
    # Create safe filename from contact name
    safe_name = sanitize_filename(message_data["contact"])[:30]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"WHATSAPP_{safe_name}_{timestamp}.md"
    filepath = os.path.join(VAULT_NEEDS_ACTION, filename)

    content = f"""---
type: whatsapp
from: {message_data["contact"]}
message: {message_data["message"][:100]}
received: {message_data["received"]}
keyword_matched: {message_data["keyword"]}
status: pending
---

## WhatsApp Message
From: {message_data["contact"]}
Message: {message_data["message"]}

## Suggested Actions
- [ ] Reply to contact
- [ ] Create invoice if needed
- [ ] Follow up tomorrow

---
*Created by AI Employee WhatsApp Watcher*
"""

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"  ❌ Error creating task file: {e}")
        return False


def wait_for_whatsapp_load(page):
    """
    Wait for WhatsApp to fully load.
    Returns: "qr" if QR code visible, "chat" if chat list visible, "error" if neither
    """
    print("  ⏳ Waiting for WhatsApp Web to load (up to 60 seconds)...")
    
    # Wait for page to fully load with extended timeout
    try:
        page.wait_for_load_state("networkidle", timeout=60000)
        print("  ✅ Page load state: networkidle")
    except PlaywrightTimeout:
        print("  ⚠️ Page load timeout, but continuing...")
    
    # Give extra time for WhatsApp to render
    print("  ⏳ Allowing extra time for WhatsApp to render...")
    time.sleep(10)
    
    # Check for QR code (login screen)
    print("  🔍 Checking for QR code (login screen)...")
    try:
        # Multiple selectors for QR code - WhatsApp changes these occasionally
        qr_selectors = [
            'canvas',  # QR code canvas
            'div[data-ref="qr"]',  # QR container
            'img[alt*="QR"]',  # QR image
            'div[data-testid="qr"]',  # Test ID for QR
        ]
        
        for selector in qr_selectors:
            try:
                qr_element = page.query_selector(selector)
                if qr_element:
                    print(f"  📱 Found QR code element with selector: {selector}")
                    return "qr"
            except Exception:
                continue
        
        # Also check by looking for login-related text
        page_content = page.content()
        if "scan" in page_content.lower() and "qr" in page_content.lower():
            print("  📱 Found QR code indicators in page content")
            return "qr"
            
    except Exception as e:
        print(f"  ⚠️ Error checking for QR code: {e}")
    
    # Check for chat list (already logged in)
    print("  🔍 Checking for chat list (already logged in)...")
    try:
        chat_selectors = [
            'div[role="listitem"]',  # Chat list items
            'div[data-testid="chat-list-item"]',  # Chat list test ID
            'div[data-list-scroll-container]',  # List scroll container
            'div[data-testid="default-user"]',  # Default user view
        ]
        
        for selector in chat_selectors:
            try:
                chat_element = page.query_selector(selector)
                if chat_element:
                    print(f"  📱 Found chat list with selector: {selector}")
                    return "chat"
            except Exception:
                continue
        
    except Exception as e:
        print(f"  ⚠️ Error checking for chat list: {e}")
    
    # Check for welcome screen
    print("  🔍 Checking for welcome screen...")
    try:
        welcome_element = page.query_selector('div[data-ref="welcome"]')
        if welcome_element:
            print("  📱 Found welcome screen")
            return "chat"  # Welcome screen means logged in
    except Exception:
        pass
    
    print("  ❌ Could not detect QR code or chat list")
    return "error"


def scan_for_unread_messages(page):
    """Scan WhatsApp Web for unread messages using multiple selector strategies."""
    messages = []

    try:
        print("  🔍 Scanning chat list for unread messages...")
        
        # ===== STRATEGY 1: Find chat list container =====
        print("  📋 Step 1: Finding chat list container...")
        
        chat_list_selectors = [
            'div[aria-label="Chat list"]',
            'div[data-testid="chat-list"]',
            '#pane-side',
            'div._aigs',
            'div.two',
        ]
        
        chat_list_container = None
        used_selector = None
        
        for selector in chat_list_selectors:
            try:
                chat_list_container = page.query_selector(selector)
                if chat_list_container:
                    used_selector = selector
                    print(f"  ✅ Found chat list container with: {selector}")
                    break
                else:
                    print(f"  ⚠️ Not found with: {selector}")
            except Exception as e:
                print(f"  ⚠️ Error with {selector}: {e}")
        
        if not chat_list_container:
            print("  ❌ No chat list container found with any selector")
            if DEBUG_MODE:
                save_debug_info(page)
            return messages
        
        # ===== STRATEGY 2: Find chat items within container =====
        print("  📋 Step 2: Finding individual chat items...")
        
        chat_item_selectors = [
            'div[role="listitem"]',
            'div[data-testid="chat-list-item"]',
            'div._aigs div[role="listitem"]',
            'div._aigs > div > div > div',
            '#pane-side > div > div > div',
        ]
        
        chat_items = []
        for selector in chat_item_selectors:
            try:
                if chat_list_container:
                    chat_items = chat_list_container.query_selector_all(selector)
                if not chat_items:
                    chat_items = page.query_selector_all(selector)
                if chat_items:
                    print(f"  ✅ Found {len(chat_items)} chat items with: {selector}")
                    break
                else:
                    print(f"  ⚠️ No chat items with: {selector}")
            except Exception as e:
                print(f"  ⚠️ Error with {selector}: {e}")
        
        if not chat_items:
            print("  ❌ No chat items found with any selector")
            if DEBUG_MODE:
                save_debug_info(page)
            return messages
        
        print(f"  📊 Total chat items to check: {len(chat_items)}")
        
        # ===== STRATEGY 3: Check each chat for unread indicator =====
        print("  📋 Step 3: Checking for unread indicators...")
        
        unread_badge_selectors = [
            'span[data-testid="icon-unread-count"]',
            'span[aria-label*="unread"]',
            'div[data-testid="cell-frame-container"]',
            'span.x1rg5ohu',
            'span[data-testid="unread-chat-count"]',
        ]
        
        # Contact name selectors
        contact_selectors = [
            'div[data-testid="cell-frame-title"]',
            'span[title]',
            'span.x1iyjqo2',
        ]
        
        # Message text selectors
        message_selectors = [
            'div[data-testid="last-msg-text"]',
            'span.x78zum5',
            'div[role="gridcell"]',
            'span[data-testid="last-message-status"]',
        ]
        
        for idx, chat in enumerate(chat_items[:15]):  # Check first 15 chats
            try:
                # Check for unread indicator
                unread_badge = None
                for badge_selector in unread_badge_selectors:
                    try:
                        unread_badge = chat.query_selector(badge_selector)
                        if unread_badge:
                            print(f"  💬 Chat {idx+1}: Found unread badge with {badge_selector}")
                            break
                    except Exception:
                        continue
                
                if not unread_badge:
                    continue  # Skip read chats
                
                # Get contact name
                contact_name = "Unknown"
                for contact_selector in contact_selectors:
                    try:
                        contact_elem = chat.query_selector(contact_selector)
                        if contact_elem:
                            contact_name = contact_elem.inner_text().strip()
                            if contact_name and contact_name != "Unknown":
                                print(f"  👤 Contact name: {contact_name}")
                                break
                    except Exception:
                        continue
                
                # Get last message preview
                message_text = ""
                for msg_selector in message_selectors:
                    try:
                        message_elem = chat.query_selector(msg_selector)
                        if message_elem:
                            message_text = message_elem.inner_text().strip()
                            if message_text:
                                print(f"  💭 Message preview: {message_text[:50]}...")
                                break
                    except Exception:
                        continue
                
                # Check keywords
                found_keywords = check_keywords(message_text)
                if not found_keywords:
                    print(f"  ⏭️  Skipping (no keywords): {contact_name}")
                    continue
                
                # Create message data
                msg_data = {
                    "contact": contact_name,
                    "message": message_text,
                    "received": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "keyword": ", ".join(found_keywords)
                }
                
                messages.append(msg_data)
                print(f"  ✅ MATCH from {contact_name}: {message_text[:50]}... (keywords: {msg_data['keyword']})")
                
            except Exception as e:
                print(f"  ⚠️ Error processing chat {idx+1}: {e}")
                continue
        
        print(f"\n  📊 Total matching messages found: {len(messages)}")
        
    except Exception as e:
        print(f"  ⚠️ Error scanning messages: {e}")
        if DEBUG_MODE:
            try:
                save_debug_info(page)
            except Exception:
                pass
    
    return messages


def save_debug_info(page):
    """Save debug information including HTML and screenshot."""
    print("\n  🔍 ===== DEBUG MODE ENABLED =====")
    print("  📸 Saving screenshot...")
    
    try:
        page.screenshot(path=DEBUG_SCREENSHOT_PATH, full_page=True)
        print(f"  ✅ Screenshot saved to: {DEBUG_SCREENSHOT_PATH}")
    except Exception as e:
        print(f"  ❌ Could not save screenshot: {e}")
    
    print("  📄 Saving page HTML (first 2000 chars)...")
    try:
        page_content = page.content()
        debug_html_path = DEBUG_SCREENSHOT_PATH.replace(".png", "_debug.html")
        with open(debug_html_path, "w", encoding="utf-8") as f:
            f.write(page_content[:2000])
        print(f"  ✅ HTML snippet saved to: {debug_html_path}")
        
        # Also print visible text
        print("\n  📋 Page visible text (first 1000 chars):")
        print("  " + "-" * 50)
        try:
            visible_text = page.inner_text("body")
            print(f"  {visible_text[:1000]}")
        except Exception:
            print("  (Could not extract visible text)")
        print("  " + "-" * 50)
        
    except Exception as e:
        print(f"  ❌ Could not save HTML: {e}")
    
    print("  🔍 ===== END DEBUG INFO =====\n")


def main():
    """Main function to start the WhatsApp watcher."""
    print("=" * 60)
    print("🤖 AI Employee - WhatsApp Watcher (Silver Tier)")
    print("=" * 60)

    # Ensure folders exist
    for folder in [SESSION_PATH, VAULT_NEEDS_ACTION]:
        if not os.path.exists(folder):
            print(f"📁 Creating folder: {folder}")
            os.makedirs(folder)

    print(f"\n💾 Session path: {SESSION_PATH}")
    print(f"📂 Vault Needs_Action: {VAULT_NEEDS_ACTION}")
    print(f"⏱️  Check interval: {CHECK_INTERVAL} seconds")
    print(f"🔑 Keywords: {', '.join(KEYWORDS)}")
    if DEBUG_MODE:
        print(f"🐛 Debug mode: ENABLED")
        print(f"📸 Debug screenshots: {DEBUG_SCREENSHOT_PATH}")
    print("\nPress Ctrl+C to stop...\n")

    processed_messages = load_processed_messages()
    print(f"📋 Already processed messages: {len(processed_messages)}")

    with sync_playwright() as p:
        # Launch browser with persistent context
        print("\n" + "=" * 60)
        print("🌐 LAUNCHING CHROMIUM BROWSER...")
        print("=" * 60)
        
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=SESSION_PATH,
                headless=False,  # NON-headless mode - visible browser
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",  # Disable GPU for better compatibility
                    "--window-size=1280,800"  # Set window size
                ],
                slow_mo=500  # Slow down operations for better visibility
            )
        except Exception as e:
            print(f"❌ Error launching browser: {e}")
            print("💡 Try closing any open Chromium/Chrome windows and try again")
            return

        print("✅ Browser launched successfully!")

        # Open WhatsApp Web
        print("\n" + "=" * 60)
        print("📱 OPENING WHATSAPP WEB...")
        print("=" * 60)
        
        page = browser.new_page()

        try:
            print("  🌐 Navigating to https://web.whatsapp.com...")
            page.goto("https://web.whatsapp.com", wait_until="networkidle", timeout=60000)
            print("  ✅ Navigation complete!")
        except Exception as e:
            print(f"❌ Error loading WhatsApp Web: {e}")
            print("💡 Check your internet connection")
            browser.close()
            return

        # Wait for WhatsApp to load with extended timeout
        print("\n" + "=" * 60)
        print("⏳ WAITING FOR WHATSAPP TO LOAD...")
        print("=" * 60)
        
        # Initial wait
        print("  ⏳ Initial wait (10 seconds)...")
        time.sleep(10)
        
        # Check load status
        load_status = wait_for_whatsapp_load(page)
        
        if load_status == "qr":
            print("\n" + "=" * 60)
            print("🔴 🔴 🔴 SCAN QR CODE NOW! 🔴 🔴 🔴")
            print("=" * 60)
            print("\n💡 Open WhatsApp on your phone:")
            print("   Android: Menu > Linked devices > Link a device")
            print("   iPhone: Settings > Linked devices > Link a device")
            print("\n⏳ Waiting 60 seconds for QR code scan...\n")
            
            # Wait for QR scan - check periodically
            for i in range(60, 0, -5):
                time.sleep(5)
                print(f"  ⏳ Time remaining: {i} seconds...")
                
                # Check if logged in now
                new_status = wait_for_whatsapp_load(page)
                if new_status == "chat":
                    print("\n✅ QR code scanned successfully!")
                    print("✅ WhatsApp logged in!")
                    break
            else:
                print("\n⚠️ QR code not scanned within 60 seconds")
                print("💡 Script will continue - you can scan on next iteration")
        
        elif load_status == "chat":
            print("\n" + "=" * 60)
            print("✅ WHATSAPP LOADED SUCCESSFULLY!")
            print("=" * 60)
            print("✅ Already logged in - session restored from previous run")
        
        else:
            print("\n" + "=" * 60)
            print("⚠️ WHATSAPP LOAD STATUS: UNKNOWN")
            print("=" * 60)
            print("💡 Waiting additional 30 seconds for page to stabilize...")
            time.sleep(30)
            
            # Check again
            load_status = wait_for_whatsapp_load(page)
            if load_status == "error":
                print("⚠️ Still cannot detect WhatsApp properly")
                print("💡 Continuing anyway - may need manual intervention")

        # Wait a moment for initial sync
        print("\n  ⏳ Final sync wait (5 seconds)...")
        time.sleep(5)

        print("\n" + "=" * 60)
        print("🚀 STARTING MESSAGE MONITORING...")
        print("=" * 60)

        # Main monitoring loop
        retry_count = 0
        max_retries = 10
        new_message_count = 0

        while True:
            try:
                # Check if still on WhatsApp Web
                current_url = page.url
                if "whatsapp.com" not in current_url:
                    print("\n⚠️ Navigated away from WhatsApp, reloading...")
                    try:
                        page.goto("https://web.whatsapp.com", wait_until="networkidle", timeout=60000)
                        time.sleep(5)
                    except Exception as e:
                        print(f"  ❌ Error reloading: {e}")
                
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Scanning for unread messages...")
                
                # Scan for unread messages
                unread_messages = scan_for_unread_messages(page)

                if unread_messages:
                    print(f"\n  📧 Found {len(unread_messages)} unread message(s) with priority keywords")

                    for msg_data in unread_messages:
                        # Create unique message ID
                        msg_id = f"{msg_data['contact']}_{msg_data['message'][:30]}"

                        # Skip if already processed
                        if msg_id in processed_messages:
                            print(f"  ⏭️  Skipping already processed: {msg_data['contact']}")
                            continue

                        # Create task file
                        if create_whatsapp_task(msg_data):
                            print(f"  ✅ Created task: {msg_data['contact']} (keywords: {msg_data['keyword']})")
                            save_processed_message(msg_id)
                            new_message_count += 1
                        else:
                            print(f"  ❌ Failed to create task for: {msg_data['contact']}")

                    if new_message_count > 0:
                        print(f"\n  📋 Total tasks created this session: {new_message_count}")
                else:
                    print("  ✅ No new priority messages")

                retry_count = 0  # Reset retry count on success

            except Exception as e:
                retry_count += 1
                print(f"\n⚠️  Error occurred (attempt {retry_count}/{max_retries}): {e}")

                if retry_count >= max_retries:
                    print("❌ Max retries reached. Attempting to recover...")
                    try:
                        page.goto("https://web.whatsapp.com", wait_until="networkidle", timeout=60000)
                        time.sleep(5)
                        retry_count = 0
                        print("✅ Recovery successful")
                    except Exception:
                        print("❌ Recovery failed. Continuing...")

                print(f"💤 Waiting {CHECK_INTERVAL} seconds before next check...")
                time.sleep(CHECK_INTERVAL)
                continue

            # Wait for next check
            print(f"\n💤 Next check in {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
