# callback_server.py

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

_authorization_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _authorization_code

        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if 'code' in params:
            code = params['code'][0]
            _authorization_code = code
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorization successful! You can close this tab.")
            print(f"[callback_server] Authorization code received: {code}")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing authorization code")
            print("[callback_server] No code in the callback request!")

def run_server():
    """
    Runs a small HTTP server listening on localhost:8080.
    It handles exactly one request (the OAuth2 callback), then returns the code.
    """
    global _authorization_code
    _authorization_code = None  # Reset before start

    server = HTTPServer(('localhost', 8080), CallbackHandler)
    print("[callback_server] Starting callback server on port 8080 ...")

    # Handle exactly one request, then stop
    server.handle_request()
    server.server_close()

    return _authorization_code
