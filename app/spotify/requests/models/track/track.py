from __future__ import annotations
from dataclasses import dataclass
from typing import Annotated, Dict

from pydantic import Field

from app.spotify.requests.models.album.simplified_album import SimplifiedAlbum
from app.spotify.requests.models.external import ExternalIds
from app.spotify.requests.models.track.simplified_track import SimplifiedTrack


@dataclass
class Track(SimplifiedTrack):
    album: SimplifiedAlbum
    external_ids: ExternalIds
    popularity: Annotated[int, Field(ge=0, le=100)]

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> Track:
        # Call the superclass from_dict to populate the base class attributes
        base_attributes = SimplifiedTrack.from_dict(data)

        return cls(
            **base_attributes.__dict__,  # Unpack base attributes
            album=SimplifiedAlbum.from_dict(data['album']),
            external_ids=ExternalIds.from_dict(data['external_ids']),
            popularity=data['popularity']
        )

    def to_dict(self) -> Dict[str, any]:
        """Converts the Track object to a dictionary, including nested dataclasses."""
        return {
            **super().to_dict(),  # Include base class attributes
            "album": self.album.to_dict(),
            "external_ids": self.external_ids.to_dict(),
            "popularity": self.popularity
        }
