from enum import Enum
import urllib
import urllib.parse
import httpx
from typing import Coroutine, Optional, Dict, Any

from app.logging.logger import get_logger
from app.spotify.requests.repository.api_client.api_client_config import ApiClientConfig


logger = get_logger(__name__)

class ApiClient:
    """Provides CRUD operations for the Spotify API with authorization support."""

    class __RequestMethod(Enum):
        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"

    def __init__(self, config: ApiClientConfig, get_authorization_headers: Coroutine[Any, Any, httpx.Headers]):
        self.__base_url = f"{config.base_address}/{config.api_version}"
        self.__get_authorization_headers = get_authorization_headers

    def __build_url(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> httpx.URL:
        url = f"{self.__base_url}/{endpoint}"
        if params:
            url += f"?{urllib.parse.urlencode(params)}"
        return httpx.URL(url)

    async def __build_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> httpx.Headers:
        if not additional_headers:
            additional_headers: Dict[str, str] = {}

        auth_headers = await self.__get_authorization_headers()

        # Merge headers and give priority to authorization headers
        return {**additional_headers, **auth_headers}

    async def __send_request(
        self,
        method: __RequestMethod,
        url: httpx.URL,
        headers: Dict[str, str],
        timeout: Optional[int] = 5,
        json_body: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method.value,
                url=url,
                headers=headers,
                timeout=timeout,
                json=json_body
            )
            response.raise_for_status()  # Raises HTTPStatusError if the response is not 2xx
            return response

    async def __request(
        self,
        method: __RequestMethod,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = 5,
        json_body: Optional[Dict[str, Any]] = None
    ) -> dict:
        """Handles a general API request with authorization and response parsing."""

        # Step 1: Build URL with query parameters if provided
        url = self.__build_url(endpoint, params)

        # Step 2: Build headers (authorization + custom headers)
        headers = await self.__build_headers(headers)

        # Step 3: Send the request and handle the response
        try:
            logger.debug(
                "Sending %s request to %s with:\nheaders: %s \nparams: %s \nbody:%s", 
                method.value, url, headers, params, json_body
                )
            response = await self.__send_request(
                method=method,
                url=url,
                headers=headers,
                timeout=timeout,
                json_body=json_body
            )

            # Step 4: Return the JSON response
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error while attempting to %s %s: Received status %d. Response body: %s",
                method.value,
                endpoint,
                e.response.status_code,
                e.response.text
            )
            return {}

        except httpx.RequestError as e:
            logger.error(
                "Request error while attempting to %s %s: %s",
                method.value,
                endpoint,
                str(e)
            )
            raise ConnectionError(
                f"Failed to connect to the Spotify API while trying to {method.value} {endpoint}."
            ) from e

        except Exception as e:
            logger.error(
                "Unexpected error while attempting to %s %s: %s",
                method.value,
                endpoint,
                str(e)
            )
            raise  # Re-raise any unexpected exceptions

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> dict:
        return await self.__request(
            method=self.__RequestMethod.GET,
            endpoint=endpoint,
            params=params,
            headers=headers
        )

    async def post(self, endpoint: str, json_body: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> dict:
        return await self.__request(
            method=self.__RequestMethod.POST,
            endpoint=endpoint,
            headers=headers,
            json_body=json_body
        )

    async def put(self, endpoint: str, json_body: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> dict:
        return await self.__request(
            method=self.__RequestMethod.PUT,
            endpoint=endpoint,
            headers=headers,
            json_body=json_body
        )

    async def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> dict:
        return await self.__request(
            method=self.__RequestMethod.DELETE,
            endpoint=endpoint,
            params=params,
            headers=headers
        )
