from __future__ import annotations
from dataclasses import dataclass
from typing import Annotated, Dict

from pydantic import Field

from app.spotify.requests.models.album.simplified_album import SimplifiedAlbum
from app.spotify.requests.models.external import ExternalIds
from app.spotify.requests.models.page.tracks_page import TracksPage


@dataclass
class Album(SimplifiedAlbum):
    tracks: TracksPage  # Paginated track information
    external_ids: ExternalIds   # External identifiers like ISRC, EAN, etc.
    label: Annotated[str, Field(min_length=1, max_length=255)]  # Record label
    popularity: Annotated[int, Field(ge=0, le=100)]  # Popularity score (0-100)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> Album:
        # First call from_dict of SimplifiedAlbum to initialize common attributes
        simplified_album_data = SimplifiedAlbum.from_dict(data)

        return cls(
            **simplified_album_data.__dict__,  # Unpack the base album attributes
            tracks=TracksPage.from_dict(data['tracks']),
            external_ids=ExternalIds.from_dict(data['external_ids']),
            label=data['label'],
            popularity=data['popularity'],
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            **super().to_dict(),  # Call to_dict of SimplifiedAlbum
            "tracks": self.tracks.to_dict(),
            "external_ids": self.external_ids.to_dict(),
            "label": self.label,
            "popularity": self.popularity,
        }
