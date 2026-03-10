from winotify import Notification


def show_notification(summary, project=""):
    title = f"Claude Code — {project}" if project else "Claude Code"
    msg = summary
    toast = Notification(
        app_id="Claude Code Notifier",
        title=title,
        msg=msg,
        duration="short",
    )
    toast.show()
