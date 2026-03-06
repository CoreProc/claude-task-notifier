# Claude Code Task Notifier

A lightweight Windows app that shows toast notifications when Claude Code finishes a task. Runs in the system tray and listens for signals from Claude Code's hook system.

## How It Works

```
Claude Code finishes a task
  -> Stop hook sends task data via POST to localhost:9876
    -> Notifier shows a Windows toast with project name + task summary
```

## Setup

### 1. Install dependencies

```bash
cd claude-task-notifier
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
```

### 2. Add hooks to Claude Code settings

Add this to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cd /d <path-to-project>/claude-task-notifier && venv/Scripts/pythonw.exe -m src.notifier.main &",
            "timeout": 3,
            "async": true
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cat > /tmp/claude-hook-input.json && curl -s --connect-timeout 2 -X POST http://localhost:9876 -d @/tmp/claude-hook-input.json -H \"Content-Type: application/json\" || true",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

Replace `<path-to-project>` with the actual path to this project.

### 3. Run

Double-click `run.bat` or start Claude Code (auto-launches via SessionStart hook).

The notifier shows a "CC" icon in your system tray. Right-click to quit.

## Project Structure

```
src/notifier/
  server.py   - HTTP server listening on localhost:9876
  toast.py    - Windows toast notifications via winotify
  tray.py     - System tray icon via pystray
  main.py     - Wires everything together
tests/
  test_server.py
  test_toast.py
run.bat         - Convenience launcher
```

## Features

- Shows project name and task summary in notifications
- Auto-starts with Claude Code sessions
- Won't start a second instance if already running
- Runs silently in system tray

## Dependencies

- Python 3.12+
- winotify
- pystray
- Pillow
