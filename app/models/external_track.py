from dataclasses import dataclass


@dataclass
class ExternalTrack:
    """Interface used to declare a track between Spotify service and other services."""
    track_name: str
    artist: str
