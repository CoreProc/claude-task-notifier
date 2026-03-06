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
