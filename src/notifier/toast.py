from datetime import datetime
from winotify import Notification


def show_notification(summary, project=""):
    timestamp = datetime.now().strftime("%H:%M:%S")
    title = f"Claude Code — {project}" if project else "Claude Code"
    msg = f"{summary}\n{timestamp}"
    toast = Notification(
        app_id="Claude Code Notifier",
        title=title,
        msg=msg,
        duration="short",
    )
    toast.show()
