from dataclasses import dataclass
from typing import Optional

from app.spotify.environment.environment import Environment
from app.spotify.requests.repository.playlist_handler import PlaylistHandler
from app.spotify.requests.repository.search_handler import SearchHandler


@dataclass
class SpotifyManagerConfig:
    # External objects to handle specific implementations
    playlist_handler: PlaylistHandler
    search_handler: SearchHandler

    # Configurable playlist data
    managed_playlist_id: Optional[str]
    managed_playlist_name: str
    managed_playlist_is_public: bool
    managed_playlist_description: str
    managed_playlist_is_collaborative: bool

    # Callback function to persistently store the automated playlist id
    environment: Environment
