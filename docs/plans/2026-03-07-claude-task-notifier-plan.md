# Claude Code Task Notifier — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python system tray app that listens for HTTP POST requests from Claude Code hooks and shows Windows toast notifications with task summary and timestamp.

**Architecture:** A single Python process runs an HTTP server on localhost:9876 in a background thread, while the main thread manages a pystray system tray icon. When a POST arrives with a JSON body, the app triggers a win10toast notification. Claude Code's `Stop` hook sends the request via curl.

**Tech Stack:** Python 3.12, win10toast, pystray, Pillow, stdlib (http.server, threading, json, datetime)

---

### Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `src/notifier/__init__.py`
- Create: `tests/__init__.py`

**Step 1: Create requirements.txt**

```
win10toast
pystray
Pillow
```

**Step 2: Create virtual environment and install deps**

Run:
```bash
cd E:/Dev/Android/Projects/claude-task-notifier
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

**Step 3: Create package structure**

Create empty `src/notifier/__init__.py` and `tests/__init__.py`.

**Step 4: Create .gitignore**

```
venv/
__pycache__/
*.pyc
.pytest_cache/
```

**Step 5: Init git repo and commit**

```bash
cd E:/Dev/Android/Projects/claude-task-notifier
git init
git add .
git commit -m "chore: initial project setup with dependencies"
```

---

### Task 2: HTTP Server

**Files:**
- Create: `src/notifier/server.py`
- Create: `tests/test_server.py`

**Step 1: Write the failing test**

```python
# tests/test_server.py
import json
import threading
import time
import urllib.request
from src.notifier.server import NotificationServer


def test_server_receives_post_and_calls_callback():
    received = []

    def on_notify(summary):
        received.append(summary)

    server = NotificationServer(port=19876, on_notify=on_notify)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.3)

    try:
        data = json.dumps({"summary": "Test task done"}).encode()
        req = urllib.request.Request(
            "http://localhost:19876",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req)

        time.sleep(0.3)
        assert received == ["Test task done"]
    finally:
        server.shutdown()


def test_server_handles_missing_summary():
    received = []

    def on_notify(summary):
        received.append(summary)

    server = NotificationServer(port=19877, on_notify=on_notify)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.3)

    try:
        data = json.dumps({}).encode()
        req = urllib.request.Request(
            "http://localhost:19877",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req)

        time.sleep(0.3)
        assert received == ["Claude Code task completed"]
    finally:
        server.shutdown()
```

**Step 2: Run test to verify it fails**

Run: `cd E:/Dev/Android/Projects/claude-task-notifier && venv/Scripts/python -m pytest tests/test_server.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Write minimal implementation**

```python
# src/notifier/server.py
import json
from http.server import HTTPServer, BaseHTTPRequestHandler


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            data = {}

        summary = data.get("summary", "Claude Code task completed")
        self.server.on_notify(summary)

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass  # Suppress console output


class NotificationServer(HTTPServer):
    def __init__(self, port, on_notify):
        self.on_notify = on_notify
        super().__init__(("127.0.0.1", port), _Handler)
```

**Step 4: Run test to verify it passes**

Run: `cd E:/Dev/Android/Projects/claude-task-notifier && venv/Scripts/python -m pytest tests/test_server.py -v`
Expected: 2 passed

**Step 5: Commit**

```bash
git add src/notifier/server.py tests/test_server.py
git commit -m "feat: add HTTP notification server with tests"
```

---

### Task 3: Toast Notification

**Files:**
- Create: `src/notifier/toast.py`
- Create: `tests/test_toast.py`

**Step 1: Write the failing test**

```python
# tests/test_toast.py
from unittest.mock import patch, MagicMock
from src.notifier.toast import show_notification


@patch("src.notifier.toast.ToastNotifier")
def test_show_notification_calls_toast(mock_class):
    mock_instance = MagicMock()
    mock_class.return_value = mock_instance

    show_notification("Task X finished")

    mock_instance.show_toast.assert_called_once()
    args, kwargs = mock_instance.show_toast.call_args
    assert kwargs["title"] == "Claude Code"
    assert "Task X finished" in kwargs["msg"]
    assert kwargs["duration"] == 10
    assert kwargs["threaded"] is True
```

**Step 2: Run test to verify it fails**

Run: `cd E:/Dev/Android/Projects/claude-task-notifier && venv/Scripts/python -m pytest tests/test_toast.py -v`
Expected: FAIL with ModuleNotFoundError

**Step 3: Write minimal implementation**

```python
# src/notifier/toast.py
from datetime import datetime
from win10toast import ToastNotifier


def show_notification(summary):
    timestamp = datetime.now().strftime("%H:%M:%S")
    msg = f"{summary}\nCompleted at {timestamp}"
    toaster = ToastNotifier()
    toaster.show_toast(title="Claude Code", msg=msg, duration=10, threaded=True)
```

**Step 4: Run test to verify it passes**

Run: `cd E:/Dev/Android/Projects/claude-task-notifier && venv/Scripts/python -m pytest tests/test_toast.py -v`
Expected: 1 passed

**Step 5: Commit**

```bash
git add src/notifier/toast.py tests/test_toast.py
git commit -m "feat: add toast notification with timestamp"
```

---

### Task 4: System Tray Icon

**Files:**
- Create: `src/notifier/tray.py`
- Create: `assets/icon.png`

**Step 1: Create a simple icon**

Generate a 64x64 icon programmatically using Pillow (no external asset needed):

```python
# src/notifier/tray.py
import pystray
from PIL import Image, ImageDraw


def _create_icon_image():
    img = Image.new("RGB", (64, 64), color=(44, 62, 80))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([8, 8, 56, 56], radius=10, fill=(214, 137, 16))
    draw.text((20, 18), "CC", fill="white")
    return img


def run_tray(on_quit):
    icon = pystray.Icon(
        "claude-notifier",
        _create_icon_image(),
        "Claude Code Notifier",
        menu=pystray.Menu(
            pystray.MenuItem("Quit", lambda: on_quit(icon)),
        ),
    )
    icon.run()
```

**Step 2: Verify tray icon works manually**

Run: `cd E:/Dev/Android/Projects/claude-task-notifier && venv/Scripts/python -c "from src.notifier.tray import run_tray; run_tray(lambda icon: icon.stop())"`
Expected: Tray icon appears with "CC" label. Right-click shows "Quit".

**Step 3: Commit**

```bash
git add src/notifier/tray.py
git commit -m "feat: add system tray icon with quit menu"
```

---

### Task 5: Main Entry Point — Wire Everything Together

**Files:**
- Create: `src/notifier/main.py`

**Step 1: Write main.py**

```python
# src/notifier/main.py
import threading
import sys
from src.notifier.server import NotificationServer
from src.notifier.toast import show_notification
from src.notifier.tray import run_tray

PORT = 9876


def main():
    server = NotificationServer(port=PORT, on_notify=show_notification)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f"Listening on http://127.0.0.1:{PORT}")

    def on_quit(icon):
        server.shutdown()
        icon.stop()

    run_tray(on_quit)


if __name__ == "__main__":
    main()
```

**Step 2: Test end-to-end manually**

Terminal 1:
```bash
cd E:/Dev/Android/Projects/claude-task-notifier
venv/Scripts/python -m src.notifier.main
```

Terminal 2:
```bash
curl -X POST http://localhost:9876 -H "Content-Type: application/json" -d "{\"summary\": \"Built the notification app\"}"
```

Expected: Toast notification appears with "Built the notification app" and timestamp.

**Step 3: Commit**

```bash
git add src/notifier/main.py
git commit -m "feat: wire up main entry point"
```

---

### Task 6: Claude Code Hook Configuration

**Files:**
- Modify: `~/.claude/settings.json` (add hooks section)

**Step 1: Add the Stop hook to Claude Code settings**

Add the following `hooks` key to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "command": "curl -s -X POST http://localhost:9876 -H \"Content-Type: application/json\" -d \"{\\\"summary\\\": \\\"Claude Code finished a task\\\"}\""
      }
    ]
  }
}
```

> **Note:** The `Stop` hook fires every time Claude Code finishes its turn. The matcher is empty so it fires unconditionally. The summary is a fixed string — Claude Code hooks don't expose task context to the command, but the notification tells you Claude is done.

**Step 2: Verify hook fires**

1. Start the notifier: `cd E:/Dev/Android/Projects/claude-task-notifier && venv/Scripts/python -m src.notifier.main`
2. In another terminal, use Claude Code to do a simple task
3. When Claude finishes, a toast notification should appear

**Step 3: Commit settings change**

This is a user-level config, no git commit needed. Just verify it works.

---

### Task 7: Convenience Launch Script

**Files:**
- Create: `run.bat`

**Step 1: Create a batch file for easy launching**

```bat
@echo off
cd /d E:\Dev\Android\Projects\claude-task-notifier
start /B venv\Scripts\pythonw.exe -m src.notifier.main
echo Claude Code Notifier started.
```

> Uses `pythonw.exe` so no console window stays open.

**Step 2: Test it**

Run: double-click `run.bat` or run from terminal.
Expected: Tray icon appears, no console window.

**Step 3: Commit**

```bash
git add run.bat
git commit -m "feat: add convenience launch script"
```

---

## Summary

| Task | What | Files |
|------|------|-------|
| 1 | Project setup | requirements.txt, venv, .gitignore |
| 2 | HTTP server | src/notifier/server.py, tests/test_server.py |
| 3 | Toast notification | src/notifier/toast.py, tests/test_toast.py |
| 4 | System tray icon | src/notifier/tray.py |
| 5 | Main entry point | src/notifier/main.py |
| 6 | Claude Code hook | ~/.claude/settings.json |
| 7 | Launch script | run.bat |
