import json
import threading
import time
import urllib.request
from src.notifier.server import NotificationServer


def test_server_receives_claude_hook_data():
    received = []

    def on_notify(summary, project):
        received.append((summary, project))

    server = NotificationServer(port=19876, on_notify=on_notify)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.3)

    try:
        data = json.dumps({
            "last_assistant_message": "Fixed the login bug",
            "cwd": "E:\\Dev\\Projects\\my-app",
        }).encode()
        req = urllib.request.Request(
            "http://localhost:19876",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req)

        time.sleep(0.3)
        assert received == [("Fixed the login bug", "my-app")]
    finally:
        server.shutdown()


def test_server_handles_missing_fields():
    received = []

    def on_notify(summary, project):
        received.append((summary, project))

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
        assert received == [("Task completed", "Unknown project")]
    finally:
        server.shutdown()
