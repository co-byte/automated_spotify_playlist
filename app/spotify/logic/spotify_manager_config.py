from dataclasses import dataclass

from app.spotify.environment.environment import Environment
from app.spotify.requests.repository.playlist_handler import PlaylistHandler
from app.spotify.requests.repository.search_handler import SearchHandler


@dataclass
class SpotifyManagerConfig:
    # Object to handle interactions with environment variables
    environment: Environment

    # Playlist variables
    managed_playlist_name: str
    managed_playlist_is_public: bool
    managed_playlist_description: str
    managed_playlist_is_collaborative: bool

    # Handlers for specific implementations
    playlist_handler: PlaylistHandler
    search_handler: SearchHandler
