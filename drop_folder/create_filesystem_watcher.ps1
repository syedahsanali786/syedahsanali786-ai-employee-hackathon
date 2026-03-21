$scriptContent = @'
"""
Filesystem Watcher for AI Employee
Monitors drop folder and creates tasks for new files.
"""

import os
import time
import shutil
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
DROP_FOLDER = r"C:\Users\Iqra Traders\Documents\ai_employee\drop_folder"
VAULT_NEEDS_ACTION = r"C:\Users\Iqra Traders\Documents\AI_Employee_Vault\Needs_Action"


class FileDropHandler(FileSystemEventHandler):
    """Handle file drop events."""
    
    def on_created(self, event):
        """Called when a file or directory is created."""
        if event.is_directory:
            return
        
        file_path = event.src_path
        filename = os.path.basename(file_path)
        
        # Skip hidden files and temporary files
        if filename.startswith("~") or filename.startswith("."):
            return
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📁 File detected: {filename}")
        
        # Copy file to Needs_Action folder
        dest_path = os.path.join(VAULT_NEEDS_ACTION, filename)
        
        try:
            # Wait a moment to ensure file is fully written
            time.sleep(0.5)
            shutil.copy2(file_path, dest_path)
            print(f"  ✅ Copied to: {dest_path}")
        except Exception as e:
            print(f"  ❌ Error copying file: {e}")
            return
        
        # Create task file for the dropped file
        task_filename = f"FILE_{filename}_task.md"
        task_path = os.path.join(VAULT_NEEDS_ACTION, task_filename)
        
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        task_content = f"""---
type: file_drop
original_name: {filename}
received: {current_datetime}
status: pending
---

## New File Received
File {filename} has been dropped for processing.

## Suggested Actions
- [ ] Review the file
- [ ] Move to relevant folder
- [ ] Move to Done when complete
"""
        
        try:
            with open(task_path, "w", encoding="utf-8") as f:
                f.write(task_content)
            print(f"  ✅ Task created: {task_filename}")
        except Exception as e:
            print(f"  ❌ Error creating task file: {e}")
        
        print(f"  📋 Task ready for processing in Needs_Action folder")


def ensure_folders_exist():
    """Create necessary folders if they don't exist."""
    folders = [DROP_FOLDER, VAULT_NEEDS_ACTION]
    
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")
        else:
            print(f"Folder exists: {folder}")


def main():
    """Main function to start the file watcher."""
    print("=" * 60)
    print("🤖 AI Employee - Filesystem Watcher")
    print("=" * 60)
    
    # Ensure folders exist
    ensure_folders_exist()
    
    print("\n👁️  Watching for new files in drop folder...")
    print(f"📂 Drop folder: {DROP_FOLDER}")
    print(f"📁 Target vault: {VAULT_NEEDS_ACTION}")
    print("\nPress Ctrl+C to stop...\n")
    
    # Set up the observer
    event_handler = FileDropHandler()
    observer = Observer()
    observer.schedule(event_handler, DROP_FOLDER, recursive=False)
    
    # Start watching
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping filesystem watcher...")
        observer.stop()
    
    observer.join()
    print("✅ Filesystem watcher stopped.")


if __name__ == "__main__":
    main()
'@

$scriptContent | Out-File -FilePath "C:\Users\Iqra Traders\Documents\ai_employee\filesystem_watcher.py" -Encoding UTF8
