# src/notifier/main.py
import queue
import socket
import sys
import threading
from src.notifier.server import NotificationServer
from src.notifier.toast import show_notification
from src.notifier.tray import run_tray

PORT = 9876


def _is_already_running():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(("127.0.0.1", PORT))
        sock.close()
        return True
    except ConnectionRefusedError:
        return False


def main():
    if _is_already_running():
        print("Claude Code Notifier is already running.")
        sys.exit(0)
    notify_queue = queue.Queue()

    def queue_notification(summary, project):
        notify_queue.put((summary, project))

    server = NotificationServer(port=PORT, on_notify=queue_notification)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f"Listening on http://127.0.0.1:{PORT}")

    # Process notifications from queue on a dedicated thread
    def notification_worker():
        while True:
            summary, project = notify_queue.get()
            try:
                show_notification(summary, project)
            except Exception as e:
                print(f"Notification error: {e}")

    worker = threading.Thread(target=notification_worker, daemon=True)
    worker.start()

    def on_quit(icon):
        server.shutdown()
        icon.stop()

    run_tray(on_quit)


if __name__ == "__main__":
    main()
