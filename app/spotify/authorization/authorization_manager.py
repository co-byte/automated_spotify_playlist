import base64
import json
import urllib
import secrets
import urllib.parse
import webbrowser
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass

import httpx
import uvicorn
from fastapi import FastAPI, Request

from app.spotify.models.tokens import Tokens


@dataclass
class Authorization_manager:
    def __init__(self, client_id: str, client_secret: str, auth_url: str, token_url: str, redirect_url: str, scope: str, tokens: Optional[Tokens] = None) -> None:
        self.state: str = None

        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__auth_url = auth_url
        self.__token_url = token_url
        self.__redirect_url = redirect_url
        self.__scope = scope

        self.tokens = tokens
        self.shutdown_event = asyncio.Event()  # Async event to signal shutdown

    @property
    async def access_token(self) -> str:
        # If there are no tokens or refresh_token is None, get new tokens
        if not self.tokens or self.tokens.refresh_token is None:
            await self.__request_user_authorization()

        # If access_token is None or expired, refresh tokens
        elif self.tokens.access_token is None or self.tokens.access_token.is_expired:
            new_tokens = await self.__refresh_tokens()
            self.tokens.update(new_tokens)  # Update with new tokens
        
        return self.tokens.access_token

    def __base_64_encode(self, text: str) -> str:
        return base64.b64encode(text.encode()).decode() # str -> byte -> b64_byte -> b64_str

    async def __start_fastapi_server(self):
        """ Starts a FastAPI server to handle OAuth redirect; gets shut down again after having received the authorization code. """
        app = FastAPI()

        @app.get("/users/authorization/redirect")
        async def extract_code_and_state(request: Request):
            """Extracts 'code' and 'state' parameters from the Spotify redirect."""
            code = request.query_params.get("code")
            state = request.query_params.get("state")

            if not code:
                raise ValueError("Error: code was not provided.")
            if state != self.state:
                raise ValueError("Response state does not match initial state. Rejecting authentication attempt.")

            self.tokens = await self.__request_new_tokens(code)
            self.shutdown_event.set()  # Signal to shut down the server
            return "Authorization successful, this window may be closed."

        config = uvicorn.Config(app, host="localhost", port=5000, log_level="critical") # Since the server is only up for a few seconds, don't use automatic logging
        server = uvicorn.Server(config)

        # Run the server in a separate asyncio task
        server_task = asyncio.create_task(server.serve())

        # Wait for the shutdown event to be set (when tokens are received)
        await self.shutdown_event.wait()

        # Ensure server task finishes after the shutdown event
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            print("Server task was cancelled cleanly.")

        print("Auth server succesfully shut down.")

    async def __request_user_authorization(self) -> None:
        self.state = secrets.token_urlsafe(16)  # Generates a secure 16-byte random string to prevent CSRF
        params = urllib.parse.urlencode({
            "client_id": self.__client_id,
            "response_type": "code",  # Static value dictated by the Spotify API docs
            "redirect_uri": self.__redirect_url,
            "state": self.state,
            "scope": self.__scope
        })

        async with httpx.AsyncClient() as client:
            response = await client.get(self.__auth_url, params=params, timeout=5)
            webbrowser.get("windows-default").open(f"{response.url}", new=1)

        # Start FastAPI server asynchronously
        await self.__start_fastapi_server()

    async def __send_token_request(self, parameters: Dict[str, str], headers: Dict[str, str]) -> Tokens:
        """Utility method to send a token request and process the response."""
        print(f"Sending token request with parameters: {parameters}")  # Debugging line

        async with httpx.AsyncClient() as client:
            response = await client.post(url=self.__token_url, data=parameters, headers=headers, timeout=5)

        response.raise_for_status()
        return Tokens.from_dict(response.json())

    async def __request_new_tokens(self, authorization_code: str) -> Tokens:
        """ Exchanges a user authorization code for an access & refresh token. """
        parameters = {
            "grant_type": 'authorization_code',
            "code": authorization_code,
            "redirect_uri": self.__redirect_url
        }
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + self.__base_64_encode(f"{self.__client_id}:{self.__client_secret}")
        }
        return await self.__send_token_request(parameters, headers)

    async def __refresh_tokens(self) -> Tokens:
        """Requests a new access and possibly refresh token using a saved refresh token."""
        parameters = {
            "grant_type": 'refresh_token',
            "refresh_token": self.tokens.refresh_token
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        return await self.__send_token_request(parameters, headers)

#TODO: fixme (refresh_token request returns 400)
if __name__ == "__main__":
    from app.configuration.config_parser import ConfigParser
    from app.environment.environment_manager import EnvironmentManager

    async def main():
        env = EnvironmentManager("app\\environment\\.env").load_from_env()
        cfg = ConfigParser(env.config_file).load_config()

        auth_manager = Authorization_manager(
            env.spotify_client_id,
            env.spotify_client_secret,
            cfg.spotify_config.api.authorization.url,
            cfg.spotify_config.api.authorization.token_url,
            cfg.spotify_config.api.authorization.redirect_url,
            cfg.spotify_config.api.authorization.permissions
        )

        # Await the access_token if it's an async property
        access_token = await auth_manager.access_token
        print(f"main - access token: {access_token}")

        auth_manager.tokens.access_token = None
        access_token = await auth_manager.access_token
        print(f"main - access token: {access_token}")
        
    asyncio.run(main())  # Run the async main function
