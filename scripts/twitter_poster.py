"""
Twitter Poster - Auto-post to Twitter/X
Part of Personal AI Employee - Gold Tier
"""

import os
import sys
import tweepy
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from .env
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "")
VAULT_PATH = os.getenv("VAULT_PATH", r"C:\Users\Iqra Traders\Documents\AI_Employee_Vault")

# Paths
TWITTER_POST_FILE = os.path.join(VAULT_PATH, "TWITTER_POST.md")
DONE_FOLDER = os.path.join(VAULT_PATH, "Done")
LOGS_FOLDER = os.path.join(VAULT_PATH, "Logs")


def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs(DONE_FOLDER, exist_ok=True)
    os.makedirs(LOGS_FOLDER, exist_ok=True)


def get_twitter_client():
    """Create and return Twitter API client"""
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET,
            wait_on_rate_limit=True
        )
        return client
    except Exception as e:
        print(f"Error creating Twitter client: {e}")
        return None


def parse_post_file():
    """Parse the TWITTER_POST.md file and extract content and metadata"""
    if not os.path.exists(TWITTER_POST_FILE):
        print(f"Error: Post file not found at: {TWITTER_POST_FILE}")
        return None, None

    with open(TWITTER_POST_FILE, "r", encoding="utf-8") as f:
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
            return {"status": "pending"}, content.strip()
    else:
        # No frontmatter, treat entire file as post content
        print("[INFO] No frontmatter found, treating entire file as content")
        return {"status": "pending"}, content.strip()


def post_tweet(text):
    """Post a tweet to Twitter/X"""
    print("\n[TWITTER] Posting tweet...")
    
    # Check tweet length
    if len(text) > 280:
        print(f"[TWITTER] Warning: Tweet is {len(text)} characters (max 280). Truncating...")
        text = text[:277] + "..."
    
    client = get_twitter_client()
    if not client:
        return {"success": False, "error": "Could not create Twitter client"}
    
    try:
        # Post the tweet
        response = client.create_tweet(text=text)
        
        if response.data and "id" in response.data:
            tweet_id = response.data["id"]
            
            # Construct tweet URL
            tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
            
            print(f"[TWITTER] Success! Tweet posted!")
            print(f"[TWITTER] Tweet ID: {tweet_id}")
            print(f"[TWITTER] URL: {tweet_url}")
            
            return {"success": True, "tweet_id": tweet_id, "tweet_url": tweet_url}
        else:
            print(f"[TWITTER] Error: Unexpected response: {response}")
            return {"success": False, "error": str(response)}
            
    except tweepy.errors.TweepyException as e:
        print(f"[TWITTER] Tweepy error: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        print(f"[TWITTER] Unexpected error: {e}")
        return {"success": False, "error": str(e)}


def update_post_status(metadata, result):
    """Update the post file status and move to Done folder"""
    # Read original file
    with open(TWITTER_POST_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Update status to posted
    updated_content = content.replace("status: pending", "status: posted")
    updated_content = updated_content.replace(
        "scheduled: today",
        f"scheduled: today\nposted: {datetime.now().isoformat()}"
    )

    # Add results
    results_text = "\n\n## Post Results\n"
    if result["success"]:
        results_text += f"- Success: Posted to Twitter\n"
        results_text += f"- Tweet ID: {result.get('tweet_id')}\n"
        results_text += f"- URL: {result.get('tweet_url')}\n"
    else:
        results_text += f"- Failed: {result.get('error', 'Unknown error')}\n"

    updated_content += results_text

    # Write updated content
    with open(TWITTER_POST_FILE, "w", encoding="utf-8") as f:
        f.write(updated_content)

    # Move to Done folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    done_filename = f"TWITTER_POST_{timestamp}.md"
    done_path = os.path.join(DONE_FOLDER, done_filename)

    os.rename(TWITTER_POST_FILE, done_path)
    print(f"\nPost file moved to Done folder: {done_path}")

    return done_path


def create_log(result, post_content):
    """Create a log entry for the posting activity"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_FOLDER, f"twitter_post_{timestamp}.log")

    log_entry = f"""---
type: twitter_post
timestamp: {datetime.now().isoformat()}
status: completed
---
## Twitter Post Log

### Post Content
{post_content[:280]}

### Results
"""

    if result["success"]:
        log_entry += f"\nStatus: SUCCESS\n"
        log_entry += f"- Tweet ID: {result.get('tweet_id')}\n"
        log_entry += f"- URL: {result.get('tweet_url')}\n"
    else:
        log_entry += f"\nStatus: FAILED\n"
        log_entry += f"- Error: {result.get('error', 'Unknown')}\n"

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(log_entry)

    print(f"Log created: {log_file}")
    return log_file


def show_setup_instructions():
    """Display instructions for getting Twitter API credentials"""
    print("\n" + "="*60)
    print("  TWITTER API SETUP INSTRUCTIONS")
    print("="*60)
    print("""
To get your Twitter API credentials:

1. CREATE A TWITTER DEVELOPER ACCOUNT:
   - Go to: https://developer.twitter.com/
   - Sign in with your Twitter account
   - Apply for a developer account

2. CREATE A PROJECT AND APP:
   - Once approved, go to Developer Portal
   - Click "Projects & Apps" > "Create Project"
   - Create an App within the project

3. GET API KEYS:
   - Go to your App settings
   - Click "Keys and Tokens"
   - Generate:
     * API Key (Consumer Key)
     * API Key Secret (Consumer Secret)
     * Access Token
     * Access Token Secret

4. SET PERMISSIONS:
   - In App settings, set permissions to "Read and Write"

5. ADD TO .ENV FILE:
   Edit: C:\\Users\\Iqra Traders\\Documents\\ai_employee_ahsan\\.env
   
   TWITTER_API_KEY=your_api_key_here
   TWITTER_API_SECRET=your_api_secret_here
   TWITTER_ACCESS_TOKEN=your_access_token_here
   TWITTER_ACCESS_SECRET=your_access_secret_here

For more info:
https://developer.twitter.com/en/docs
https://docs.tweepy.org/
""")
    print("="*60)


def create_sample_post():
    """Create a sample TWITTER_POST.md file"""
    ensure_directories()
    
    sample_content = """---
status: pending
---
## Post Content
Excited to share that I built a Personal AI Employee! 🤖

It automatically manages:
✅ Gmail & WhatsApp
✅ LinkedIn posts
✅ Business invoices
✅ Twitter posts

Built with Claude Code + Python!

#AI #Automation #Pakistan #ClaudeCode
"""

    with open(TWITTER_POST_FILE, "w", encoding="utf-8") as f:
        f.write(sample_content)

    print(f"\nSample post file created at: {TWITTER_POST_FILE}")
    print("\nEdit the file with your content, then run:")
    print("  python twitter_poster.py")


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
    print("  TWITTER POSTER - AI Employee")
    print("="*50)
    print(f"  Vault: {VAULT_PATH}")
    
    # Check if credentials are configured
    if not TWITTER_API_KEY or not TWITTER_API_SECRET:
        print("\n[WARNING] Twitter credentials not configured!")
        print("Run with --setup flag to see setup instructions:\n")
        print("  python twitter_poster.py --setup\n")
        return

    if TWITTER_API_KEY and len(TWITTER_API_KEY) > 10:
        print(f"  API Key: {TWITTER_API_KEY[:10]}...")
    else:
        print("  API Key: Not configured")
    print("="*50)

    # Check if post file exists
    if not os.path.exists(TWITTER_POST_FILE):
        print(f"\n[ERROR] No post file found at: {TWITTER_POST_FILE}")
        print("\nTo create a sample post file, run:\n")
        print("  python twitter_poster.py --create-sample\n")
        return

    # Parse post file
    print(f"\nReading post from: {TWITTER_POST_FILE}")
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

    # Post to Twitter
    result = post_tweet(post_content)

    # Update post status and create log
    done_path = update_post_status(metadata, result)
    create_log(result, post_content)

    # Summary
    print("\n" + "="*50)
    print("  POSTING SUMMARY")
    print("="*50)
    if result["success"]:
        print(f"  Status: SUCCESS")
        print(f"  Tweet URL: {result.get('tweet_url')}")
    else:
        print(f"  Status: FAILED")
        print(f"  Error: {result.get('error', 'Unknown')}")
    print("="*50)


if __name__ == "__main__":
    main()
