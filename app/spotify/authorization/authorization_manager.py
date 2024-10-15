import base64
import secrets
import time
import urllib.parse
import webbrowser
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass

import httpx
import uvicorn
from fastapi import FastAPI, Request

from app.spotify.authorization.authorization_manager_config import AuthorizationManagerConfig
from app.spotify.models.tokens import Tokens


# Static values dictated by the Spotify API docs
TOKEN_REQUEST_CONTENT_TYPE = 'application/x-www-form-urlencoded'
USER_DATA_REQUEST_RESPONSE_TYPE = "code"
AUTHORIZATION_GRANT_TYPE = 'authorization_code'
REFRESH_TOKEN_GRANT_TYPE = 'refresh_token'

@dataclass
class AuthorizationManager:
    def __init__(self, config: AuthorizationManagerConfig, refresh_token: Optional[str] = None) -> None:
        self.__tokens: Tokens = Tokens(
            access_token=None,
            refresh_token=refresh_token
            )
        self.__config = config

    @property
    async def access_token(self):
        """Ensures tokens are up-to-date and returns the latest access_token"""
        if self.__tokens and self.__tokens.access_token and not self.__tokens.access_token.is_expired:
            print("authorization_manager - Stored access token was provided.")
            return self.__tokens.access_token
        try:
            print("authorization_manager - Access token unavailable, attempting to refresh tokens.")
            self.__tokens = await self.__refresh_tokens()
        except ValueError:
            print("authorization_manager - Unable to refresh tokens, performing full user authorization.")
            self.__tokens = await self.__perform_full_authorization()
        return self.__tokens.access_token

    def clear_access_token(self) -> None:
        #TODO: remove this method
        self.__tokens.access_token = None

    # Full authorization
    async def __perform_full_authorization(self) -> Tokens:
        state = await self.__request_authorization_to_access_user_data()
        auth_code = await self.__get_auth_code_from_user_authorization(state)
        tokens = await self.__request_new_tokens(auth_code)
        return tokens

    async def __request_authorization_to_access_user_data(self) -> str:
        synchronization_state = secrets.token_urlsafe(16)  # Generates a secure 16-byte random string to prevent CSRF
        params = urllib.parse.urlencode({
            "client_id": self.__config.client_id,
            "response_type": USER_DATA_REQUEST_RESPONSE_TYPE,
            "redirect_uri": self.__config.redirect_url,
            "state": synchronization_state,
            "scope": self.__config.scope
        })

        async with httpx.AsyncClient() as client:
            response = await client.get(self.__config.auth_url, params=params, timeout=5)
            webbrowser.get("windows-default").open(f"{response.url}")

        return synchronization_state

    async def __get_auth_code_from_user_authorization(self, synchronization_state: str) -> str:
        """ Temorarily starts a FastAPI server to handle OAuth redirect and retrieve an authorization code. """
        app = FastAPI()
        app.state.auth_code = None
        app.state.shutdown_event = asyncio.Event() # Async event to signal the server to shut down after user authorization

        @app.get("/users/authorization/redirect")
        async def extract_code_and_state(request: Request):
            code = request.query_params.get("code")
            state = request.query_params.get("state")

            if not code:
                raise ValueError("Error: code was not provided.")
            if state != synchronization_state:
                raise ValueError("Response state does not match initial state. Rejecting authentication attempt.")

            request.app.state.auth_code = code
            print("authorization_manager - Auth code received, signalling server to shut down.")
            request.app.state.shutdown_event.set()  # Signal to shut down the server
            return "Authorization successful, this window may be closed."

        config = uvicorn.Config(
            app,
            host="localhost",
            port=5000,
            log_level="critical" # Don't use automatic logging
            )
        server = uvicorn.Server(config)

        # Run the server in a separate asyncio task
        print("authorization_manager - Starting up auth server.")
        server_task = asyncio.create_task(server.serve())

        # Wait for the shutdown event to be set (when tokens are received)
        await app.state.shutdown_event.wait()

        # Ensure server task finishes after the shutdown event
        await server.shutdown()
        server_task.cancel()

        print("authorization_manager - Auth server succesfully shut down.")
        return app.state.auth_code

    async def __request_new_tokens(self, authorization_code: str) -> Tokens:
        """ Exchanges a user authorization code for an access & refresh token. """
        parameters = {
            "grant_type": AUTHORIZATION_GRANT_TYPE,
            "code": authorization_code,
            "redirect_uri": self.__config.redirect_url
        }
        headers = {
            'Authorization': 'Basic ' + self.__base_64_encode(f"{self.__config.client_id}:{self.__config.client_secret}")
        }
        return await self.__send_token_request(parameters, headers)

    # Simpler token request when a refresh_token is registered
    async def __refresh_tokens(self) -> Tokens:
        """Requests a new access and possibly refresh token using a saved refresh token."""
        parameters = {
            "grant_type": REFRESH_TOKEN_GRANT_TYPE,
            "refresh_token": self.__tokens.refresh_token
        }
        try:
            value =  await self.__send_token_request(parameters)
            return value
        except httpx.HTTPStatusError as e:
            print("Authorization_manager - Exception raised during token refresh attempt.")
            raise ValueError(f"Unable to renew tokens using refresh token {self.__tokens.refresh_token}") from e
        
    # Helper methods
    async def __send_token_request(self, parameters: Dict[str, str], additional_headers: Dict[str, str] = None) -> Tokens:
        """Utility method to send a token request and process the response."""
        headers = {
            'Content-Type': TOKEN_REQUEST_CONTENT_TYPE
        }
        if additional_headers:
            headers.update(additional_headers)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self.__config.token_url,
                data=parameters,
                headers=headers,
                timeout=5
                )
        response.raise_for_status()
        return Tokens.from_dict(response.json())

    def __base_64_encode(self, text: str) -> str:
        return base64.b64encode(text.encode()).decode() # str -> bytes -> b64_bytes -> b64_str


#TODO: fixme (refresh_token request returns 400)
if __name__ == "__main__":
    from app.configuration.config_parser import ConfigParser
    from app.environment.environment_manager import EnvironmentManager

    async def main():
        env = EnvironmentManager("app\\environment\\.env").load_from_env()
        cfg = ConfigParser(env.config_file).load_config()

        auth_config = AuthorizationManagerConfig(
            env.spotify_client_id,
            env.spotify_client_secret,
            cfg.spotify_config.api.authorization.url,
            cfg.spotify_config.api.authorization.token_url,
            cfg.spotify_config.api.authorization.redirect_url,
            cfg.spotify_config.api.authorization.permissions
        )
        auth_manager = AuthorizationManager(auth_config)

        # Await the access_token if it's an async property
        access_token = await auth_manager.access_token
        print(f"main - Access_token: {access_token}")

        print("\nmain - Clearing access_token & refetching it...\n")
        auth_manager.clear_access_token()
        access_token = await auth_manager.access_token
        print(f"main - Access_token: {access_token}")

    asyncio.run(main())  # Run the async main function
