"""
Simple HTTP server to serve the web UI.
Run this to access the chatbot interface in a browser.
"""

import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 3000
DIRECTORY = Path(__file__).parent

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def main():
    print(f"Web UI server running at http://localhost:{PORT}", flush=True)
    print(f"Serving files from: {DIRECTORY}", flush=True)
    print("\nPress Ctrl+C to stop the server", flush=True)
    print("\nNote: Make sure the API server is running on http://127.0.0.1:8000", flush=True)

    # Open browser automatically
    webbrowser.open(f"http://localhost:{PORT}")

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.", flush=True)

if __name__ == "__main__":
    main()
