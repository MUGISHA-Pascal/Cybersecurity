"""
**EDUCATIONAL DEMO ONLY – Rwanda Coding Academy Assignment**
Use exclusively in isolated VMs. Never deploy on real systems.
This code demonstrates backdoor techniques for defense learning purposes.

Simple HTTP server for Kali. Serves files (e.g. portable curl.exe) so the
Windows target can download dependencies. Run from the directory containing
curl.exe (or any file to serve).
"""

import http.server
import socketserver
import os
import sys

# ============== CONFIGURATION ==============
PORT = 8000
# Directory to serve (default: current directory; put curl.exe here)
SERVE_DIR = os.path.dirname(os.path.abspath(__file__))


class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Serves files from SERVE_DIR. Logs requests."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SERVE_DIR, **kwargs)

    def log_message(self, format, *args):
        print(f"[HTTP] {args[0]}")


def main():
    os.chdir(SERVE_DIR)
    with socketserver.TCPServer(("0.0.0.0", PORT), QuietHTTPRequestHandler) as httpd:
        print(f"[*] Serving files from {SERVE_DIR} on http://0.0.0.0:{PORT}")
        print("[*] Place curl.exe in this folder so the target can download it.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Server stopped.")


if __name__ == "__main__":
    main()
