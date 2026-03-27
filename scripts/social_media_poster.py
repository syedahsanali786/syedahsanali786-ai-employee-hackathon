"""
Social Media Poster - Auto-post to Facebook and Instagram
Part of Personal AI Employee - Gold Tier
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from .env
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
VAULT_PATH = os.getenv("VAULT_PATH", r"C:\Users\Iqra Traders\Documents\AI_Employee_Vault")

# Paths
SOCIAL_POST_FILE = os.path.join(VAULT_PATH, "SOCIAL_POST.md")
DONE_FOLDER = os.path.join(VAULT_PATH, "Done")
LOGS_FOLDER = os.path.join(VAULT_PATH, "Logs")


def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs(DONE_FOLDER, exist_ok=True)
    os.makedirs(LOGS_FOLDER, exist_ok=True)


def parse_post_file():
    """Parse the SOCIAL_POST.md file and extract content and metadata"""
    if not os.path.exists(SOCIAL_POST_FILE):
        print(f"Error: Post file not found at: {SOCIAL_POST_FILE}")
        return None, None

    with open(SOCIAL_POST_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if file has frontmatter (starts with ---)
    lines = content.strip().split("\n")
    
    if lines and lines[0].strip() == "---":
        # Has frontmatter - find the closing ---
        end_index = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end_index = i
                break
        
        if end_index > 0:
            # Parse frontmatter
            frontmatter_lines = lines[1:end_index]
            post_lines = lines[end_index + 1:]
            
            # Parse metadata
            metadata = {}
            for line in frontmatter_lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()
            
            # Get post content
            post_text = "\n".join(post_lines).strip()
            
            # Remove ## Post Content header if present
            if post_text.startswith("## Post Content"):
                post_text = post_text.replace("## Post Content", "").strip()
            
            return metadata, post_text
        else:
            # Could not find closing ---, treat as no frontmatter
            print("[WARNING] Could not find closing ---, treating entire file as content")
            return {"status": "pending", "platforms": "facebook"}, content.strip()
    else:
        # No frontmatter, treat entire file as post content
        print("[INFO] No frontmatter found, treating entire file as content")
        return {"status": "pending", "platforms": "facebook"}, content.strip()


def post_to_facebook(message):
    """Post to Facebook Page using Graph API"""
    print("\n[FACEBOOK] Posting to Facebook Page...")

    url = f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}/feed"
    params = {
        "message": message,
        "access_token": FACEBOOK_ACCESS_TOKEN
    }

    try:
        response = requests.post(url, data=params, timeout=30)
        result = response.json()

        print(f"[FACEBOOK] Response status: {response.status_code}")

        if response.status_code == 200 and "id" in result:
            post_id = result["id"]
            print(f"[FACEBOOK] Success! Posted successfully! Post ID: {post_id}")
            return {"success": True, "post_id": post_id, "platform": "facebook"}
        else:
            print(f"[FACEBOOK] Error: {result}")
            return {"success": False, "error": result, "platform": "facebook"}

    except requests.exceptions.RequestException as e:
        print(f"[FACEBOOK] Request failed: {e}")
        return {"success": False, "error": str(e), "platform": "facebook"}


def get_instagram_account_id():
    """Get Instagram Business Account ID linked to Facebook Page"""
    url = f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}"
    params = {
        "fields": "instagram_business_account",
        "access_token": FACEBOOK_ACCESS_TOKEN
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        result = response.json()

        if response.status_code == 200 and "instagram_business_account" in result:
            ig_account_id = result["instagram_business_account"]["id"]
            print(f"[INSTAGRAM] Found Instagram Business Account: {ig_account_id}")
            return ig_account_id
        else:
            print(f"[INSTAGRAM] Error getting Instagram account: {result}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"[INSTAGRAM] Request failed: {e}")
        return None


def post_to_instagram(message):
    """Post to Instagram using Graph API via Facebook"""
    print("\n[INSTAGRAM] Posting to Instagram...")

    # Get Instagram Business Account ID
    ig_account_id = get_instagram_account_id()
    if not ig_account_id:
        print("[INSTAGRAM] Could not get Instagram Business Account ID")
        print("[INSTAGRAM] Make sure your Instagram account is connected to your Facebook Page")
        return {"success": False, "error": "Instagram account not found", "platform": "instagram"}

    # Step 1: Create media container
    container_url = f"https://graph.facebook.com/v18.0/{ig_account_id}/media"
    container_params = {
        "image_url": "https://via.placeholder.com/1080x1080.png?text=Post",
        "caption": message,
        "access_token": FACEBOOK_ACCESS_TOKEN
    }

    try:
        # Create container
        print("[INSTAGRAM] Creating media container...")
        container_response = requests.post(container_url, data=container_params, timeout=30)
        container_result = container_response.json()

        print(f"[INSTAGRAM] Container response status: {container_response.status_code}")

        if container_response.status_code != 200:
            print(f"[INSTAGRAM] Container creation failed: {container_result}")
            return {"success": False, "error": container_result, "platform": "instagram"}

        container_id = container_result.get("id")
        if not container_id:
            print(f"[INSTAGRAM] No container ID in response: {container_result}")
            return {"success": False, "error": "No container ID", "platform": "instagram"}

        print(f"[INSTAGRAM] Container created: {container_id}")

        # Step 2: Publish the media
        publish_url = f"https://graph.facebook.com/v18.0/{ig_account_id}/media_publish"
        publish_params = {
            "creation_id": container_id,
            "access_token": FACEBOOK_ACCESS_TOKEN
        }

        print("[INSTAGRAM] Publishing media...")
        publish_response = requests.post(publish_url, data=publish_params, timeout=30)
        publish_result = publish_response.json()

        print(f"[INSTAGRAM] Publish response status: {publish_response.status_code}")

        if publish_response.status_code == 200 and "id" in publish_result:
            media_id = publish_result["id"]
            print(f"[INSTAGRAM] Success! Posted successfully! Media ID: {media_id}")
            return {"success": True, "media_id": media_id, "platform": "instagram"}
        else:
            print(f"[INSTAGRAM] Publish failed: {publish_result}")
            return {"success": False, "error": publish_result, "platform": "instagram"}

    except requests.exceptions.RequestException as e:
        print(f"[INSTAGRAM] Request failed: {e}")
        return {"success": False, "error": str(e), "platform": "instagram"}


def update_post_status(metadata, results):
    """Update the post file status and move to Done folder"""
    # Read original file
    with open(SOCIAL_POST_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Update status to posted
    updated_content = content.replace("status: pending", "status: posted")
    updated_content = updated_content.replace(
        "scheduled: today",
        f"scheduled: today\nposted: {datetime.now().isoformat()}"
    )

    # Add results
    results_text = "\n\n## Post Results\n"
    for result in results:
        if result["success"]:
            results_text += f"- Success {result['platform'].upper()}: Posted (ID: {result.get('post_id') or result.get('media_id')})\n"
        else:
            results_text += f"- Failed {result['platform'].upper()}: {result.get('error', 'Unknown error')}\n"

    updated_content += results_text

    # Write updated content
    with open(SOCIAL_POST_FILE, "w", encoding="utf-8") as f:
        f.write(updated_content)

    # Move to Done folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    done_filename = f"SOCIAL_POST_{timestamp}.md"
    done_path = os.path.join(DONE_FOLDER, done_filename)

    os.rename(SOCIAL_POST_FILE, done_path)
    print(f"\nPost file moved to Done folder: {done_path}")

    return done_path


def create_log(results, post_content):
    """Create a log entry for the posting activity"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_FOLDER, f"social_post_{timestamp}.log")

    log_entry = f"""---
type: social_media_post
timestamp: {datetime.now().isoformat()}
status: completed
---
## Social Media Post Log

### Post Content
{post_content[:500]}{'...' if len(post_content) > 500 else ''}

### Results
"""

    for result in results:
        status = "SUCCESS" if result["success"] else "FAILED"
        log_entry += f"\n{result['platform'].upper()}: {status}\n"
        if result["success"]:
            log_entry += f"- ID: {result.get('post_id') or result.get('media_id')}\n"
        else:
            log_entry += f"- Error: {result.get('error', 'Unknown')}\n"

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(log_entry)

    print(f"Log created: {log_file}")
    return log_file


def show_setup_instructions():
    """Display instructions for getting Facebook API credentials"""
    print("\n" + "="*60)
    print("  FACEBOOK & INSTAGRAM API SETUP INSTRUCTIONS")
    print("="*60)
    print("""
To get your Facebook Page ID and Access Token:

1. CREATE A FACEBOOK APP:
   - Go to: https://developers.facebook.com/
   - Click "My Apps" > "Create App"
   - Select "Business" as app type
   - Fill in app details and create

2. GET FACEBOOK PAGE ID:
   - Go to your Facebook Page
   - Click "About" in the left menu
   - Scroll down to find "Page ID"
   - Copy the Page ID number

3. GENERATE ACCESS TOKEN:
   - Go to: https://developers.facebook.com/tools/explorer/
   - Select your app from dropdown
   - Click "Get Token" > "Get Page Access Token"
   - Select your page
   - Grant permissions: pages_manage_posts, pages_read_engagement
   - Copy the generated access token

4. FOR INSTAGRAM:
   - Your Instagram must be a Business or Creator account
   - Connect Instagram to your Facebook Page:
     * Go to Instagram Settings > Account > Linked Accounts
     * Link your Facebook Page
   - In Facebook App Dashboard, add Instagram Graph API product

5. ADD TO .ENV FILE:
   Edit: C:\\Users\\Iqra Traders\\Documents\\ai_employee\\.env

   FACEBOOK_PAGE_ID=your_page_id_here
   FACEBOOK_ACCESS_TOKEN=your_token_here

6. TOKEN EXPIRY:
   - Page access tokens from Graph Explorer expire in ~60 days
   - For production, use long-lived tokens (60 days)
   - Generate new token before expiry

For more info:
https://developers.facebook.com/docs/graph-api/
https://developers.facebook.com/docs/instagram-api/
""")
    print("="*60)


def create_sample_post():
    """Create a sample SOCIAL_POST.md file"""
    ensure_directories()
    
    sample_content = (
        "---\n"
        "status: pending\n"
        "platforms: facebook,instagram\n"
        "scheduled: today\n"
        "---\n"
        "## Post Content\n"
        "Excited to share that Iqra Traders is now using AI automation!\n"
        "\n"
        "We have built a Personal AI Employee that manages our:\n"
        "- Emails automatically\n"
        "- WhatsApp messages\n"
        "- Business invoices via Odoo\n"
        "- Social media posts\n"
        "\n"
        "The future of business is here!\n"
        "\n"
        "#IqraTraders #AI #Automation #Pakistan #Business\n"
    )

    with open(SOCIAL_POST_FILE, "w", encoding="utf-8") as f:
        f.write(sample_content)

    print(f"\nSample post file created at: {SOCIAL_POST_FILE}")
    print("\nEdit the file with your content, then run:")
    print("  python social_media_poster.py")


def main():
    """Main function"""
    ensure_directories()

    # Check for command line args FIRST
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        show_setup_instructions()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "--create-sample":
        create_sample_post()
        return

    print("\n" + "="*50)
    print("  SOCIAL MEDIA POSTER - AI Employee")
    print("="*50)
    print(f"  Vault: {VAULT_PATH}")
    print(f"  Facebook Page ID: {FACEBOOK_PAGE_ID[:10]}..." if FACEBOOK_PAGE_ID else "  Facebook Page ID: Not configured")
    print("="*50)

    # Check if credentials are configured
    if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN:
        print("\n[WARNING] Facebook credentials not configured!")
        print("Run with --setup flag to see setup instructions:\n")
        print("  python social_media_poster.py --setup\n")
        return

    # Check if post file exists
    if not os.path.exists(SOCIAL_POST_FILE):
        print(f"\n[ERROR] No post file found at: {SOCIAL_POST_FILE}")
        print("\nTo create a sample post file, run:\n")
        print("  python social_media_poster.py --create-sample\n")
        return

    # Parse post file
    print(f"\nReading post from: {SOCIAL_POST_FILE}")
    metadata, post_content = parse_post_file()

    if not metadata or not post_content:
        print("\n[ERROR] Could not parse post file. Check format.")
        return

    print(f"\nMetadata: {metadata}")
    print(f"\nPost Content:\n{post_content}\n")

    # Check status
    if metadata.get("status") == "posted":
        print("\n[INFO] This post has already been posted!")
        return

    # Get platforms to post to
    platforms = metadata.get("platforms", "facebook").split(",")
    results = []

    # Post to each platform
    for platform in platforms:
        platform = platform.strip().lower()

        if platform == "facebook":
            result = post_to_facebook(post_content)
            results.append(result)

        elif platform == "instagram":
            result = post_to_instagram(post_content)
            results.append(result)

        else:
            print(f"\n[WARNING] Unknown platform: {platform}")

    # Update post status and create log
    if results:
        done_path = update_post_status(metadata, results)
        create_log(results, post_content)

        # Summary
        print("\n" + "="*50)
        print("  POSTING SUMMARY")
        print("="*50)
        success_count = sum(1 for r in results if r["success"])
        print(f"  Total platforms: {len(results)}")
        print(f"  Successful: {success_count}")
        print(f"  Failed: {len(results) - success_count}")
        print("="*50)


if __name__ == "__main__":
    main()
