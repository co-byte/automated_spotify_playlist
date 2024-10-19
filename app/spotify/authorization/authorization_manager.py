import base64
import secrets
import urllib.parse
import webbrowser
import asyncio
from typing import Callable, Dict, Optional

import httpx
import uvicorn
from fastapi import FastAPI

from app.spotify.authorization.authorization_manager_config import AuthorizationManagerConfig
from app.spotify.authorization.authorization_server import AuthorizationServer
from app.spotify.models.tokens import Tokens


# Static values dictated by the Spotify API docs
TOKEN_REQUEST_CONTENT_TYPE = 'application/x-www-form-urlencoded'
USER_DATA_REQUEST_RESPONSE_TYPE = "code"
AUTHORIZATION_GRANT_TYPE = 'authorization_code'
REFRESH_TOKEN_GRANT_TYPE = 'refresh_token'

class AuthorizationManager:
    def __init__(self, config: AuthorizationManagerConfig, get_auth_code_from_server: Callable[[str], str], refresh_token: Optional[str] = None) -> None:
        self.__tokens: Tokens = Tokens(
            access_token=None,
            refresh_token=refresh_token
            )
        self.get_auth_code_from_server = get_auth_code_from_server
        self.__config = config

    async def get_access_token(self):
        """Ensures tokens are up-to-date and returns the latest access_token"""
        if self.__tokens and self.__tokens.access_token and not self.__tokens.access_token.is_expired:
            print("authorization_manager.get_access_token - Stored access token was provided.")
            return self.__tokens.access_token
        try:
            print("authorization_manager.get_access_token - Access token unavailable, refreshing tokens.")
            self.__tokens = await self.__refresh_tokens()
        except ValueError:
            print("authorization_manager.get_access_token - Unable to refresh tokens, performing full user authorization.")
            self.__tokens = await self.__perform_full_authorization()
        print("authorization_manager.get_access_token - New access token provided")
        return self.__tokens.access_token

    # Full authorization
    async def __perform_full_authorization(self) -> Tokens:
        state = await self.__request_authorization_to_access_user_data()
        auth_code = await self.get_auth_code_from_server(state)
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

    async def __request_new_tokens(self, authorization_code: str) -> Tokens:
        """ Exchanges a user authorization code for an access & refresh token. """
        parameters = {
            "grant_type": AUTHORIZATION_GRANT_TYPE,
            "code": authorization_code,
            "redirect_uri": self.__config.redirect_url
        }
        return await self.__send_token_request(parameters)
    
    # Simpler token request when a refresh_token is registered
    async def __refresh_tokens(self) -> Tokens:
        """Requests a new access and possibly refresh token using a saved refresh token."""
        parameters = {
            "grant_type": REFRESH_TOKEN_GRANT_TYPE,
            "refresh_token": self.__tokens.refresh_token
        }
        try:
            return await self.__send_token_request(parameters)
        except httpx.HTTPStatusError as e:
            print(f"Authorization_manager - Exception raised during token refresh attempt.\n{e}")
            raise ValueError(f"Unable to renew tokens using refresh token {self.__tokens.refresh_token}") from e

    # Helper methods
    async def __send_token_request(self, parameters: Dict[str, str]) -> Tokens:
        """Utility method to send a token request and process the response."""
        parameters = urllib.parse.urlencode(parameters) #TODO: check if urlencoding is explicitely needed
        headers = {
            'Content-Type': TOKEN_REQUEST_CONTENT_TYPE,
            'Authorization': 'Basic ' + self.__base_64_encode(f"{self.__config.client_id}:{self.__config.client_secret}")
        }
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


if __name__ == "__main__":
    from app.configuration.config_parser import ConfigParser
    from app.environment.environment_manager import EnvironmentManager

    async def main():
        env = EnvironmentManager("app\\environment\\.env").load_from_env()
        cfg = ConfigParser(env.config_file).load_config()

        auth_server_config = uvicorn.Config(
            FastAPI(),
            host="localhost",
            port=5000,
            log_level="critical"  # Don't use automatic logging
        )
        auth_server = AuthorizationServer(auth_server_config)
        
        auth_config = AuthorizationManagerConfig(
            env.spotify_client_id,
            env.spotify_client_secret,
            cfg.spotify_config.api.authorization.url,
            cfg.spotify_config.api.authorization.token_url,
            cfg.spotify_config.api.authorization.redirect_url,
            cfg.spotify_config.api.authorization.permissions
        )
        auth_manager = AuthorizationManager(
            auth_config,
            auth_server.get_authorization_code
            )

        # Await the access_token if it's an async property
        access_token = await auth_manager.get_access_token()
        print(f"main - Access_token: {access_token}")

        print("\nmain - Clearing access_token & refetching it...\n")
        access_token = await auth_manager.get_access_token()
        print(f"main - Access_token: {access_token}")

    asyncio.run(main())  # Run the async main function
