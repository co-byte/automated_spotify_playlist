"""
This package provides tools and abstractions for an application that converts a list of tracks 
(track_name: str, artist: str) into Spotify track objects and uses them to update a chosen playlist.

Modules include support for authorization, configuration management, environment handling, 
logging, and interaction with external services like Spotify.
"""

from .authorization.authorization_manager import AuthorizationManager
from .authorization.authorization_manager_config import AuthorizationManagerConfig
from .authorization.authorization_server import AuthorizationServer

from .configuration.config_parser import ConfigParser
from .configuration.spotify_config import SpotifyConfig

from .environment.environment_types import EnvironmentTypes
from .environment.environment import Environment

from .log_utils.logger import get_logger

from .logic.spotify_manager import SpotifyManager
from .logic.spotify_manager_config import SpotifyManagerConfig

from .models.external_track import ExternalTrack

from .repository.api_client.api_client import ApiClient
from .repository.api_client.api_client_config import ApiClientConfig
from .repository.playlist_handler import PlaylistHandler
from .repository.search_handler import SearchHandler

__all__ = [
    # Authorization
    "AuthorizationManager",
    "AuthorizationManagerConfig",
    "AuthorizationServer",

    # Configuration
    "ConfigParser",
    "SpotifyConfig",

    # Environment
    "EnvironmentTypes",
    "Environment",

    # Logging
    "get_logger",

    # Logic
    "SpotifyManager",
    "SpotifyManagerConfig",

    # Models
    "ExternalTrack",

    # Repository
    "ApiClient",
    "ApiClientConfig",
    "PlaylistHandler",
    "SearchHandler",
]
