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
