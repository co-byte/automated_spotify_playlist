import base64
import urllib
import secrets
import urllib.parse
from dataclasses import dataclass

import requests


@dataclass
class AuthInitializer:
    def __init__(self, client_id: str, client_secret: str, auth_url: str, token_url: str, redirect_url: str, scope: str) -> None:
        client_credentials: bytes = f"{client_id}:{client_secret}"
        self.__b64_encoded_credentials = self.__base_64_encode(client_credentials)

        #TODO: clean up
        self.client_id = client_id
        self.auth_url = auth_url
        self.token_url = token_url
        self.redirect_url = redirect_url
        self.scope = scope

    def __base_64_encode(self, text: str) -> str:
        """Encodes str to byte format, performs base64 encoding and transforms the result back to a string; """
        byte_text: bytes = text.encode()
        b64_encoded_byte_text: bytes = base64.b64encode(byte_text)
        b64_encoded_text: str = b64_encoded_byte_text.decode()
        return b64_encoded_text

    def request_user_authorization(self):
        state = secrets.token_urlsafe(16), # Generates a secure 16-byte random string to prevent CSRF

        params = urllib.parse.urlencode({
            "client_id": self.client_id,
            "response_type": "code",    # Static value dictated by the Spotify API docs
            "redirect_uri": self.redirect_url,
            "state": state,
            "scope": self.scope
            })

        response = requests.get(self.auth_url, params, timeout=5)
        print(response.url)
    