import urllib
from enum import Enum
from typing import Optional, Dict, Any
import urllib.parse

import httpx

from app.spotify_service.logging.logger import get_logger
from app.spotify_service.authorization.authorization_manager import (
    AuthorizationError,
    AuthorizationManager,
)
from app.spotify_service.repository.api_client.api_client_config import ApiClientConfig


logger = get_logger(__name__)


class SpotifyApiError(Exception):
    """Custom exception for Spotify API errors."""


class SpotifyApiHeaderError(SpotifyApiError):
    """Custom exception for Spotify API request header errors."""


class ApiClient:
    """Provides CRUD operations for the Spotify API with authorization support."""

    class __RequestMethod(Enum):
        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"

    def __init__(self, config: ApiClientConfig, auth_manager: AuthorizationManager):
        self.__base_url = f"{config.base_address}/{config.api_version}"
        self.__auth_manager = auth_manager

    def __build_url(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> httpx.URL:
        url = f"{self.__base_url}/{endpoint}"
        if params:
            url += f"?{urllib.parse.urlencode(params)}"
        return httpx.URL(url)

    async def __build_headers(
        self, additional_headers: Optional[Dict[str, str]] = None
    ) -> httpx.Headers:
        if not additional_headers:
            additional_headers: Dict[str, str] = {}

        try:
            auth_headers = await self.__auth_manager.build_authorization_headers()

            # Merge headers and give priority to authorization headers
            return {**additional_headers, **auth_headers}

        except AuthorizationError as ae:
            message = "Failed to retrieve authorization headers."
            logger.error(message)
            raise SpotifyApiHeaderError(message) from ae

    async def __send_request(
        self,
        method: __RequestMethod,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = 5,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """Handles a general API request with authorization and response parsing."""

        try:
            # Step 1: Build URL with query parameters if provided
            url = self.__build_url(endpoint, params)

            # Step 2: Build headers (authorization + custom headers)
            headers = await self.__build_headers(headers)

            # Step 3: Send the request and handle the response
            logger.debug(
                "Sending %s request to %s \nwith:\n\theaders: %s \n\tparams: %s \n\tbody:%s",
                method.value,
                url,
                headers,
                params,
                json_body,
            )

            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method.value,
                    url=url,
                    headers=headers,
                    timeout=timeout,
                    json=json_body,
                )
                response.raise_for_status()
                return response.json()

        except SpotifyApiHeaderError as e:
            logger.error(
                "Unable to provide headers for %s request to %s", method.value, endpoint
            )
            raise SpotifyApiError from e

        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error while attempting to %s %s: Received status %d. Response body: %s",
                method.value,
                endpoint,
                e.response.status_code,
                e.response.text,
            )
            return {}

        except httpx.RequestError as e:
            logger.error(
                "Request error while attempting to %s %s: %s",
                method.value,
                endpoint,
                str(e),
            )
            raise ConnectionError(
                f"Failed to connect to the Spotify API while trying to {method.value} {endpoint}."
            ) from e

        except Exception as e:
            logger.critical(
                "Unexpected error while attempting to %s %s: %s",
                method.value,
                endpoint,
                str(e),
            )
            raise  # Re-raise any unexpected exceptions

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> dict:
        return await self.__send_request(
            method=self.__RequestMethod.GET,
            endpoint=endpoint,
            params=params,
            headers=headers,
        )

    async def post(
        self,
        endpoint: str,
        json_body: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> dict:
        return await self.__send_request(
            method=self.__RequestMethod.POST,
            endpoint=endpoint,
            headers=headers,
            json_body=json_body,
        )

    async def put(
        self,
        endpoint: str,
        json_body: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> dict:
        return await self.__send_request(
            method=self.__RequestMethod.PUT,
            endpoint=endpoint,
            headers=headers,
            json_body=json_body,
        )

    async def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> dict:
        return await self.__send_request(
            method=self.__RequestMethod.DELETE,
            endpoint=endpoint,
            params=params,
            headers=headers,
        )
