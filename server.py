"""
SysCalculus - Multi-Threaded Production Preview Server
Serves dist/ directory with clean URL rewrites, security headers, and MIME-type handling.
"""

import os
import sys
from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingTCPServer

PORT = int(os.environ.get("PORT", 3000))
DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")

class SysCalculusHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)

    def do_GET(self):
        # Clean URL rewrites
        parsed_path = self.path.split('?')[0]

        # Route / to /index.html
        if parsed_path == "/":
            self.path = "/index.html"
        # If path doesn't have an extension, try appending .html
        elif not os.path.splitext(parsed_path)[1]:
            candidate = os.path.join(DIST_DIR, parsed_path.lstrip('/')) + ".html"
            if os.path.exists(candidate):
                self.path = parsed_path + ".html"

        return super().do_GET()

    def end_headers(self):
        # Security & Privacy Headers
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Permissions-Policy", "interest-cohort=()")
        super().end_headers()

    def log_message(self, format, *args):
        # Compact access logging
        sys.stdout.write(f"[HTTP] {self.address_string()} - {args[0]} {args[1]}\n")
        sys.stdout.flush()

import threading
import time

class ServerController:
    def __init__(self, port=PORT):
        self.port = port
        self.httpd = None
        self.thread = None
        self.running = False

    def start(self):
        if self.running and self.thread and self.thread.is_alive():
            return
        if not os.path.exists(DIST_DIR):
            print("[SERVER] dist/ directory not found. Running build.py first...")
            import build
            build.build_site()

        ThreadingTCPServer.allow_reuse_address = True
        self.httpd = ThreadingTCPServer(("0.0.0.0", self.port), SysCalculusHandler)
        self.running = True
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True, name="HttpServerThread")
        self.thread.start()
        print(f"[SERVER] SysCalculus Live Server active on http://localhost:{self.port}")

    def stop(self):
        if self.httpd:
            try:
                self.httpd.shutdown()
                self.httpd.server_close()
            except Exception:
                pass
        self.running = False

    def restart(self):
        print(f"[SERVER] Restarting server on port {self.port}...")
        self.stop()
        time.sleep(0.5)
        self.start()

    def is_alive(self):
        return self.running and self.thread and self.thread.is_alive()

def start_server(port=PORT):
    controller = ServerController(port)
    controller.start()
    try:
        while controller.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()

if __name__ == "__main__":
    start_server()
