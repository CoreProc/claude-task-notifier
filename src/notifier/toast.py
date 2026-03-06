from datetime import datetime
from win10toast import ToastNotifier


def show_notification(summary):
    timestamp = datetime.now().strftime("%H:%M:%S")
    msg = f"{summary}\nCompleted at {timestamp}"
    toaster = ToastNotifier()
    toaster.show_toast(title="Claude Code", msg=msg, duration=10, threaded=True)
