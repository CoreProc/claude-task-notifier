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
