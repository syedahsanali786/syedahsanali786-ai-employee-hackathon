# Skill: File Processor

## Purpose
Process all pending tasks in the Needs_Action folder.

## Steps
1. Read all .md files inside /Needs_Action/
2. For each file:
   - Understand what task it is
   - Create a PLAN_{filename}.md inside /Plans/ with steps to complete it
   - Update the status in the original file from pending to processed
3. Update Dashboard.md:
   - Update "Last Updated" with today's date and time
   - Update "Pending Actions" count
4. Move processed task files to /Done/

## Success Condition
All pending tasks are processed and Dashboard.md is updated.

## Rules
- Never delete any file, only move to /Done/
- Always log what you did in /Logs/ folder
- If unsure about any action, ask human for approval
