from dataclasses import dataclass


@dataclass
class ExternalTrack:
    """Interface used to declare a track between Spotify service and other services."""
    track_name: str
    artist: str

    # Define __hash__ and __eq__ functions, so ExternalTracks can be uniquely stored in e.g. a set
    def __hash__(self):
        return hash((self.track_name, self.artist))

    def __eq__(self, other):
        if not isinstance(other, ExternalTrack):
            raise ValueError(f"{other} is not an instance of {ExternalTrack.__name__}")
        return self.track_name == other.track_name and self.artist == other.artist

    def __str__(self):
        return f"'{self.track_name}' by '{self.artist}'"
