from dataclasses import dataclass


@dataclass
class ExternalTrack:
    """Interface used to declare a track between Spotify service and other services."""
    track_name: str
    artist: str

    # Define a hash function ExternalTracks can be uniquely stored in e.g. a set
    def __hash__(self):
        return hash((self.track_name, self.artist))

    def __str__(self):
        return f"'{self.track_name}' by '{self.artist}'"
