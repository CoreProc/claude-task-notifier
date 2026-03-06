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

        # Extract project from cwd (last directory component)
        cwd = data.get("cwd", "")
        project = cwd.replace("\\", "/").rstrip("/").split("/")[-1] if cwd else "Unknown project"

        # Use last_assistant_message as summary, fall back to simple message
        summary = data.get("last_assistant_message", data.get("summary", "Task completed"))
        # Truncate long summaries to first 200 chars
        if len(summary) > 200:
            summary = summary[:200] + "..."

        self.server.on_notify(summary, project)

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
