# 🤖 Personal AI Employee

A personal AI assistant that automates task management using an Obsidian vault-based workflow.

**Hackathon 0** — Bronze Tier Complete 🥉

---

## 📖 What Is This Project?

This project implements a **Personal AI Employee** that:

- Monitors a drop folder for new files
- Automatically creates tasks in an Obsidian vault
- Processes tasks following a structured workflow
- Maintains logs, plans, and a dashboard for tracking progress
- Follows company rules and engagement guidelines

The AI Employee uses a **skill-based architecture** where capabilities are defined in markdown files (e.g., `SKILL_file_processor.md`) and executed autonomously.

---

## 🚀 How to Run the File System Watcher

### Prerequisites

1. Python 3.8 or higher
2. Install dependencies:

```bash
pip install watchdog
```

### Start the Watcher

```bash
python "C:\Users\Iqra Traders\Documents\ai_employee\filesystem_watcher.py"
```

### Usage

1. Keep the watcher running in the background
2. Drop any file into: `C:\Users\Iqra Traders\Documents\ai_employee\drop_folder\`
3. The watcher will:
   - Copy the file to the vault's `Needs_Action` folder
   - Create a task file for processing
   - Print a confirmation message

Press `Ctrl+C` to stop the watcher.

---

## 📁 Folder Structure

### Obsidian Vault (`AI_Employee_Vault/`)

```
AI_Employee_Vault/
├── Dashboard.md              # Main status dashboard
├── Company_Handbook.md       # Rules and business info
├── README.md                 # This file
├── Inbox/                    # Raw incoming items
├── Needs_Action/             # Pending tasks awaiting processing
├── Plans/                    # Task plans and execution steps
├── Done/                     # Completed tasks archive
├── Logs/                     # Activity logs
└── Skills/                   # AI Employee skill definitions
    └── SKILL_file_processor.md
```

### Application Files (`ai_employee/`)

```
ai_employee/
├── filesystem_watcher.py     # Main watcher script
└── drop_folder/              # Folder to drop files for processing
```

### Project Files (`Hackathon 0/`)

```
Hackathon 0/
├── create_*.ps1              # PowerShell helper scripts
└── ...                       # Additional utilities
```

---

## 📋 Folder Descriptions

| Folder | Purpose |
|--------|---------|
| `Inbox/` | Raw incoming items before categorization |
| `Needs_Action/` | Tasks pending processing |
| `Plans/` | Detailed plans for executing tasks |
| `Done/` | Archive of completed tasks |
| `Logs/` | Timestamped activity logs |
| `Skills/` | Markdown-defined AI capabilities |

---

## 🎯 Bronze Tier Milestones

- [x] Vault structure created
- [x] Company Handbook written
- [x] Agent Skill created (SKILL_file_processor.md)
- [x] File System Watcher running
- [x] End-to-end task flow tested

---

## 📝 Business Info

- **Business Name:** Iqra Traders
- **Currency:** PKR

---

## 📄 License

This project is part of Hackathon 0.

---

**Built with ❤️ by Iqra Traders**
