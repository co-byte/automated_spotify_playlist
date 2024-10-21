from abc import ABC, abstractmethod
from app.spotify.requests.api_client import SpotifyApiClient


class SpotifyRequestHandler(ABC):
    """Base class for Spotify API request handlers."""

    @abstractmethod
    def __init__(self, spotify_api_client: SpotifyApiClient, endpoint: str):
        self._api_client = spotify_api_client
        self._endpoint = endpoint
