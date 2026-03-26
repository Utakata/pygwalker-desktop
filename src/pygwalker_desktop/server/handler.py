"""HTTP request handler for serving PyGWalker HTML and /comm endpoint."""

import http.server
import json
import urllib.parse

from pygwalker.api.pygwalker import PygWalker
from pygwalker.utils.encode import DataFrameEncoder


def create_handler(walker: PygWalker):
    """Factory: returns an HTTPRequestHandler class bound to the given walker."""

    class PygWalkerDesktopHandler(http.server.SimpleHTTPRequestHandler):

        def do_GET(self):
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path

            if path == "/health":
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
                return

            props = walker._get_props("web_server")
            props["communicationUrl"] = "comm"
            html = walker._get_render_iframe(props)

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        def do_POST(self):
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path

            if not path.startswith("/comm"):
                self.send_error(404)
                return

            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(post_data)

            result = walker.comm._receive_msg(payload["action"], payload["data"])

            response_bytes = json.dumps(result, cls=DataFrameEncoder).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-Length", str(len(response_bytes)))
            self.end_headers()
            self.wfile.write(response_bytes)

        def log_message(self, format, *args):
            pass  # suppress console logging

    return PygWalkerDesktopHandler
