import base64
import json
import os
import threading
import urllib
import secrets
import urllib.parse
import webbrowser
from typing import Optional
from dataclasses import dataclass
import requests

from fastapi import FastAPI, Request
import uvicorn

from app.spotify.models.tokens import Tokens



@dataclass
class Authorization_manager:
    def __init__(self, client_id: str, client_secret: str, auth_url: str, token_url: str, redirect_url: str, scope: str, tokens: Optional[Tokens] = None) -> None:
        self.state: str = None

        #TODO: clean up
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__auth_url = auth_url
        self.__token_url = token_url
        self.__redirect_url = redirect_url
        self.__scope = scope

        self.__tokens = tokens
        
        self.auth_server: uvicorn.Server = None
        self.token_event = threading.Event()  # Event to signal token initialization
        
    @property
    def access_token(self) -> str:
        if not self.__tokens or self.__tokens.refresh_token is None:
            # Start from zero: request user authorization and new tokens
            self.__request_user_authorization()    #FIXME: actually return the code
            self.token_event.wait(timeout=10)

        elif self.__tokens.access_token is None or self.__tokens.access_token.is_expired:
            # Refresh the existing tokens
            self.__tokens.update(self.__refresh_tokens())
        return self.__tokens.access_token

    def __base_64_encode(self, text: str) -> str:
        """Encodes str to byte format, performs base64 encoding and transforms the result back to a string; """
        byte_text: bytes = text.encode()
        b64_encoded_byte_text: bytes = base64.b64encode(byte_text)
        b64_encoded_text: str = b64_encoded_byte_text.decode()
        return b64_encoded_text

    def __handle_user_interactions(self, authorization_url: str):
        # Open the authorization URL in the browser
        webbrowser.open(authorization_url, 1)

        # Start the FastAPI server in a separate thread
        threading.Thread(target=self.__start_fastapi_server, daemon=True).start()

    def __start_fastapi_server(self):
        """ Starts a FastAPI server to handle OAuth redirect; gets shut down again after having received the authorization code. """
        app = FastAPI()
        config = uvicorn.Config(app, host="localhost", port=5000)
        self.auth_server = uvicorn.Server(config)

        @app.get("/users/authorization/redirect")
        async def extract_code_and_state(request: Request):
            """Extracts 'code' and 'state' parameters from the Spotify redirect."""
            code = request.query_params.get("code")
            state = request.query_params.get("state")

            if not code:
                raise ValueError("Error: code was not provided.")
            if state != self.state:
                raise ValueError("Response state does not match initial state. Rejecting authentication attempt.")
            
            self.__tokens = self.__request_new_tokens(code)
            self.token_event.set()  # Signal that tokens are ready
            self.auth_server.shutdown()
            return "Authorization succesful, this window may be closed. "

        self.auth_server.run()

    def __request_user_authorization(self) -> None:
        self.state=secrets.token_urlsafe(16)    # Generates a secure 16-byte random string to prevent CSRF
        params = urllib.parse.urlencode({
            "client_id": self.__client_id,
            "response_type": "code",    # Static value dictated by the Spotify API docs
            "redirect_uri": self.__redirect_url,
            "state": self.state,
            "scope": self.__scope
            })
        response = requests.get(self.__auth_url, params, timeout=5)
        return self.__handle_user_interactions(response.url)

    def __request_new_tokens(self, authorization_code: str) -> Tokens:
        """ Exchanges a user authorization code for an access & refresh token. """
        url = self.__token_url
        parameters = {
            "grant_type": 'authorization_code',  # Static value dictated by the Spotify API docs
            "code": authorization_code,
            "redirect_uri": self.__redirect_url
            }
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + self.__base_64_encode(f"{self.__client_id}:{self.__client_secret}") # Form should be "Basic <base64 encoded client_id:client_secret>"
            }
        response = requests.post(
            url=url,
            params=parameters,
            headers=headers,
            timeout=5
            )
        if not response.ok:
            raise requests.HTTPError(f"{response.status_code} - {response.reason}: {response.text}")
        response_content = json.loads(response.content)
        return Tokens.from_dict(response_content)

    def __refresh_tokens(self) -> Tokens:
        params = urllib.parse.urlencode({
            "grant_type": 'refresh_token',
            "refresh_token": self.__tokens.refresh_token,
            "client_id": self.__client_id
        })
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(
            url=self.__token_url,
            params=params,
            headers=headers,
            timeout=5
            )
        if not response.ok:
            raise requests.HTTPError(f"{response.status_code} - {response.reason}: {response.text}")
        response_content = response.content.decode()
        return Tokens.from_dict(response_content)

#TODO: remove this
if __name__ == "__main__":
    from app.configuration.config_parser import ConfigParser
    from app.environment.environment_manager import EnvironmentManager

    env = EnvironmentManager("app\\environment\\.env").load_from_env()
    cfg = ConfigParser(env.config_file).load_config()

    auth_initializer = Authorization_manager(
        env.spotify_client_id,
        env.spotify_client_secret,
        cfg.spotify_config.api.authorization.url,
        cfg.spotify_config.api.authorization.token_url,
        cfg.spotify_config.api.authorization.redirect_url,
        cfg.spotify_config.api.authorization.permissions
    )

    print(f"main - access token: {auth_initializer.access_token}")
    print("done...")