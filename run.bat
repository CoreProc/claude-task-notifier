@echo off
cd /d E:\Dev\Android\Projects\claude-task-notifier
start /B venv\Scripts\pythonw.exe -m src.notifier.main
echo Claude Code Notifier started.
