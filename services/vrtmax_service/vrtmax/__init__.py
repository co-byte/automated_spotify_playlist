"""
This package provides components to retrieve and publish the playlist of radio stations 
featured on VRTMax. Using GraphQL, it extracts played tracks and returns a list of tracks 
in the format: Track(track_name: str, artist: str).
"""

from .log_utils.logger import get_logger
from .client.vrtmax_client import VRTMaxClient, VRTMaxClientError
from .config.vrtmax_client_config import VRTMaxClientConfig
