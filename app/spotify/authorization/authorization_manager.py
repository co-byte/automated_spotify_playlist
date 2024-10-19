import base64
import secrets
import urllib.parse
import webbrowser
from typing import Callable, Dict, Optional

import httpx

from app.spotify.authorization.authorization_manager_config import AuthorizationManagerConfig
from app.spotify.models.tokens import Tokens
from app.logging.logger import get_logger

logger = get_logger(__name__)

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
        logger.debug("AuthorizationManager initialized with client ID: %s", self.__config.client_id)

    async def authorized_request(self, function: Callable): #TODO: complete this wrapper function
        def wrap(*args, **kwargs):
            logger.debug("Wrapping function %s for authorization", function.__name__)
            return function(*args, **kwargs)
        return wrap

    async def get_access_token(self):
        """Ensures tokens are up-to-date and returns the latest access_token"""
        
        logger.info("Access token requested.")
        
        # Option 1) An active access_token is already stored
        if self.__tokens and self.__tokens.access_token and not self.__tokens.access_token.is_expired:
            logger.info("A stored access token was provided.")
            return self.__tokens.access_token
        
        # Option 2) Attempt to refresh the tokens using an existing refresh_token
        if self.__tokens and self.__tokens.refresh_token:
            try:
                logger.info("Attempting to refresh tokens.")
                self.__tokens = await self.__refresh_tokens()
                logger.info("A refreshed access token was provided.")
                return self.__tokens.access_token
            except ValueError:
                logger.warning("Unable to refresh tokens, performing full user authorization.")
        
        # Option 3) Go through the complete user authorization process
        self.__tokens = await self.__perform_full_authorization()
        logger.info("A new access token was provided.")
        return self.__tokens.access_token

    # Full authorization
    async def __perform_full_authorization(self) -> Tokens:
        logger.info("Starting full user authorization process.")

        state = await self.__request_authorization_to_access_user_data()
        logger.debug("Synchronization state received: %s", state)

        auth_code = await self.get_auth_code_from_server(state)
        logger.debug("Authorization code retrieved: %s", auth_code)

        tokens = await self.__request_new_tokens(auth_code)
        logger.debug("New tokens received: %s", tokens)

        return tokens

    async def __request_authorization_to_access_user_data(self) -> str:
        logger.info("Requesting user authorization from Spotify.")
        
        synchronization_state = secrets.token_urlsafe(16)  # Generates a secure 16-byte random string to prevent CSRF
        params = urllib.parse.urlencode({
            "client_id": self.__config.client_id,
            "response_type": USER_DATA_REQUEST_RESPONSE_TYPE,
            "redirect_uri": self.__config.redirect_url,
            "state": synchronization_state,
            "scope": self.__config.scope
        })
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.__config.auth_url,
                params=params,
                timeout=5
                )
            logger.debug("Authorization URL: %s", response.url)
            webbrowser.get("windows-default").open(f"{response.url}")

        return synchronization_state

    async def __request_new_tokens(self, authorization_code: str) -> Tokens:
        """ Exchanges a user authorization code for an access & refresh token. """
        logger.info("Requesting new tokens using authorization code.")
        parameters = {
            "grant_type": AUTHORIZATION_GRANT_TYPE,
            "code": authorization_code,
            "redirect_uri": self.__config.redirect_url
        }
        return await self.__send_token_request(parameters)

    # Simpler token request when a refresh_token is registered
    async def __refresh_tokens(self) -> Tokens:
        """Requests a new access and possibly refresh token using a saved refresh token."""
        logger.info("Attempting to refresh tokens using saved refresh token.")
        parameters = {
            "grant_type": REFRESH_TOKEN_GRANT_TYPE,
            "refresh_token": self.__tokens.refresh_token
        }
        try:
            return await self.__send_token_request(parameters)
        except httpx.HTTPStatusError as e:
            logger.error("Error during token refresh attempt: %s", e)
            raise ValueError(f"Unable to renew tokens using refresh token {self.__tokens.refresh_token}") from e

    # Helper methods
    async def __send_token_request(self, parameters: Dict[str, str]) -> Tokens:
        """Utility method to send a token request and process the response."""
        logger.debug("Sending token request with parameters: %s", parameters)
        parameters = urllib.parse.urlencode(parameters)
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
        logger.debug("Token request response status: %s", response.status_code)
        response.raise_for_status()
        logger.info("Tokens successfully obtained from Spotify.")
        return Tokens.from_dict(response.json())

    def __base_64_encode(self, text: str) -> str:
        return base64.b64encode(text.encode()).decode() # str -> bytes -> b64_bytes -> b64_str
