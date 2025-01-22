# google_oauth_client.py

from connections.oauth2.base_oauth_client import BaseOAuthClient
import requests


class GoogleOAuthClient(BaseOAuthClient):
    def exchange_code_for_token(self, code, code_verifier):
        """Exchanges the authorization code for tokens with Google."""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
            "code_verifier": code_verifier,
        }
        response = requests.post(self.token_endpoint, data=data)
        if response.status_code >= 400:
            raise Exception(f"Token endpoint error {response.status_code}: {response.text}")
        return response.json()
