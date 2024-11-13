import base64
import secrets
import urllib.parse
import webbrowser
from typing import Dict

import httpx

from spotify.log_utils.logger import get_logger
from spotify.authorization.authorization_manager_config import (
    AuthorizationManagerConfig,
)
from spotify.authorization.models.tokens import AccessToken, Tokens


logger = get_logger(__name__)

# Static values dictated by the Spotify API docs
_TOKEN_REQUEST_CONTENT_TYPE = "application/x-www-form-urlencoded"
_USER_DATA_REQUEST_RESPONSE_TYPE = "code"
_AUTHORIZATION_GRANT_TYPE = "authorization_code"
_REFRESH_TOKEN_GRANT_TYPE = "refresh_token"


class AuthorizationError(Exception):
    """Custom exception for handling authorization process failures."""


class AuthorizationManager:
    def __init__(self, config: AuthorizationManagerConfig) -> None:
        self.__config = config
        self.__tokens = Tokens(
            access_token=None,
            refresh_token=self.__config.environment.spotify_client_refresh_token,
        )
        logger.debug(
            "AuthorizationManager initialized with client ID: %s",
            self.__config.client_id,
        )

    async def build_authorization_headers(self) -> httpx.Headers:
        try:
            access_token = await self.__get_access_token()  # Await the async method
            authorization_header = httpx.Headers(
                {"Authorization": f"Bearer {access_token.token}"}
            )
            return authorization_header

        except Exception as e:
            message = "Unable to build authorization headers."
            logger.error(message)
            raise AuthorizationError(message) from e

    async def __get_access_token(self) -> AccessToken:
        logger.info("Access token requested.")

        # Option 1: Stored valid access token
        if (
            self.__tokens
            and self.__tokens.access_token
            and not self.__tokens.access_token.is_expired
        ):
            logger.info("A stored access token was provided.")
            return self.__tokens.access_token

        # Option 2: Refresh tokens
        if self.__tokens and self.__tokens.refresh_token:
            try:
                logger.info("Attempting to refresh tokens.")
                self.__tokens = await self.__refresh_tokens()

                logger.info("A refreshed access token was provided.")
                return self.__tokens.access_token
            except ValueError as ve:
                logger.warning("Unable to refresh tokens: %s", str(ve))

        # Option 3: Full user authorization
        self.__tokens = await self.__perform_full_authorization()
        logger.info("A new access token was provided.")
        return self.__tokens.access_token

    # Full authorization
    async def __perform_full_authorization(self) -> Tokens:
        logger.info("Starting full user authorization process.")

        state = await self.__request_authorization_to_access_user_data()
        logger.debug("Synchronization state received: %s", state)

        auth_code = await self.__config.authorization_server.get_authorization_code(
            state
        )
        logger.debug("Authorization code retrieved: %s", auth_code)

        tokens = await self.__request_new_tokens(auth_code)
        logger.debug("New tokens received: %s", tokens)

        # Update the environment variable
        self.__config.environment.spotify_client_refresh_token = tokens.refresh_token

        return tokens

    async def __request_authorization_to_access_user_data(self) -> str:
        logger.info("Requesting user authorization from Spotify.")

        synchronization_state = secrets.token_urlsafe(
            16
        )  # Generates a secure 16-byte random string to prevent CSRF
        params = urllib.parse.urlencode(
            {
                "client_id": self.__config.client_id,
                "response_type": _USER_DATA_REQUEST_RESPONSE_TYPE,
                "redirect_uri": self.__config.redirect_url,
                "state": synchronization_state,
                "scope": self.__config.scope,
            }
        )
        async with httpx.AsyncClient() as client:
            response = await client.get(self.__config.auth_url, params=params)

            webbrowser.get().open(f"{response.url}")

        logger.info("Authorization URL opened in browser.")
        return synchronization_state

    async def __request_new_tokens(self, authorization_code: str) -> Tokens:
        """Exchanges a user authorization code for an access & refresh token."""

        logger.info("Requesting new tokens using authorization code.")
        parameters = {
            "grant_type": _AUTHORIZATION_GRANT_TYPE,
            "code": authorization_code,
            "redirect_uri": self.__config.redirect_url,
        }
        return await self.__send_token_request(parameters)

    # Simpler token request when a refresh_token is registered
    async def __refresh_tokens(self) -> Tokens:
        """Requests a new access and possibly refresh token using a saved refresh token."""

        logger.info("Attempting to refresh tokens using saved refresh token.")
        parameters = {
            "grant_type": _REFRESH_TOKEN_GRANT_TYPE,
            "refresh_token": self.__tokens.refresh_token,
        }
        try:
            tokens = await self.__send_token_request(parameters)
            return tokens

        except httpx.HTTPStatusError as e:
            logger.error("Error during token refresh attempt: %s", e)
            raise ValueError(
                f"Token refresh failed for refresh token {self.__tokens.refresh_token}"
            ) from e

    # Utility
    async def __send_token_request(self, parameters: Dict[str, str]) -> Tokens:
        """Utility method to send a token request and process the response."""

        logger.debug("Sending token request with parameters: %s", parameters)

        parameters = urllib.parse.urlencode(parameters)
        headers = {
            "Content-Type": _TOKEN_REQUEST_CONTENT_TYPE,
            "Authorization": "Basic "
            + self.__base_64_encode(
                f"{self.__config.client_id}:{self.__config.client_secret}"
            ),
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=self.__config.token_url, data=parameters, headers=headers
                )
                logger.debug("Token request response status: %s", response.status_code)

                response.raise_for_status()

                logger.info("Tokens successfully obtained from Spotify.")
                return Tokens.from_dict(response.json())

        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.error("Token request failed: %s", e)
            raise RuntimeError("Token request failed.") from e

    @staticmethod
    def __base_64_encode(text: str) -> str:
        return base64.b64encode(
            text.encode()
        ).decode()  # str -> bytes -> b64_bytes -> b64_str
