# base_oauth_client.py

import json
import secrets
import hashlib
import base64
from abc import ABC, abstractmethod
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import requests
import urllib.parse
import os


class BaseOAuthClient(ABC):
    def __init__(self, client_id, client_secret, redirect_uri, auth_endpoint, token_endpoint, scopes):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_endpoint = auth_endpoint
        self.token_endpoint = token_endpoint
        self.scopes = scopes
        self.authorization_code = None

    @staticmethod
    def generate_pkce():
        """Generates a PKCE code_verifier and code_challenge."""
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode("ascii")).digest()
        ).decode("ascii").rstrip("=")
        return code_verifier, code_challenge

    def build_auth_url(self, code_challenge):
        """Builds the OAuth2 authorization URL."""
        scope_str = " ".join(self.scopes)
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": scope_str,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "access_type": "offline",
            "prompt": "consent",
        }
        return requests.Request("GET", self.auth_endpoint, params=params).prepare().url

    def start_callback_server(self):
        """Starts the local HTTP server to listen for OAuth callbacks."""
        def handle_callback():
            class OAuthCallbackHandler(BaseHTTPRequestHandler):
                def do_GET(inner_self):
                    parsed_url = urllib.parse.urlparse(inner_self.path)
                    params = urllib.parse.parse_qs(parsed_url.query)
                    if "code" in params:
                        self.authorization_code = params["code"][0]
                        inner_self.send_response(200)
                        inner_self.end_headers()
                        inner_self.wfile.write(
                            b"Authorization successful! You can close this browser tab."
                        )
                    else:
                        inner_self.send_response(400)
                        inner_self.end_headers()
                        inner_self.wfile.write(b"Missing authorization code.")

            with HTTPServer(("localhost", 8080), OAuthCallbackHandler) as server:
                server.handle_request()

        threading.Thread(target=handle_callback, daemon=True).start()

    @abstractmethod
    def exchange_code_for_token(self, code, code_verifier):
        """Exchanges the authorization code for tokens."""
        pass

    def store_tokens(self, token_data, app_name, directory="tokens"):
        """
        Stores tokens securely in a JSON file specific to the app.

        Args:
            token_data (dict): The token data to store.
            app_name (str): A unique name for the app (e.g., 'google_drive').
            directory (str): Directory to save token files (default: 'tokens').
        """
        os.makedirs(directory, exist_ok=True)  # Ensure the directory exists
        file_path = os.path.join(directory, f"{app_name}_tokens.json")

        try:
            with open(file_path, "w") as f:
                json.dump(token_data, f, indent=2)
            print(f"[GoogleOAuthClient] Tokens for '{app_name}' stored in '{file_path}'.")
        except Exception as e:
            print(f"[GoogleOAuthClient] Error storing tokens: {e}")
