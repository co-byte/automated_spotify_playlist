from abc import ABC, abstractmethod

from spotify.repository.api_client.api_client import ApiClient


class SpotifyRequestHandler(ABC):
    """Base class for Spotify API request handlers."""

    @abstractmethod
    def __init__(self, spotify_api_client: ApiClient):
        self._api_client = spotify_api_client
