from __future__ import annotations
from dataclasses import dataclass
from typing import Annotated, Dict, List, Optional

from pydantic import Field, HttpUrl

from app.spotify.requests.models.album.simplified_album import SimplifiedAlbum
from app.spotify.requests.models.external import ExternalIds
from app.spotify.requests.models.track.simplified_track import SimplifiedTrack


@dataclass
class TrackPage:
    href: HttpUrl
    limit: Annotated[int, Field(ge=1)]
    next: Optional[HttpUrl]
    offset: Annotated[int, Field(ge=0)]
    previous: Optional[HttpUrl]
    total: Annotated[int, Field(ge=0)]
    items: List[SimplifiedTrack]

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> TrackPage:
        return cls(
            href=data['href'],
            limit=data['limit'],
            next=data.get('next'),
            offset=data['offset'],
            previous=data.get('previous'),
            total=data['total'],
            items=[SimplifiedTrack.from_dict(item) for item in data['items']]
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "href": self.href,
            "limit": self.limit,
            "next": self.next,
            "offset": self.offset,
            "previous": self.previous,
            "total": self.total,
            "items": [item.to_dict() for item in self.items]
        }

@dataclass
class Album(SimplifiedAlbum):
    tracks: TrackPage  # Paginated track information
    external_ids: ExternalIds   # External identifiers like ISRC, EAN, etc.
    label: Annotated[str, Field(min_length=1, max_length=255)]  # Record label
    popularity: Annotated[int, Field(ge=0, le=100)]  # Popularity score (0-100)
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> Album:
        # First call from_dict of SimplifiedAlbum to initialize common attributes
        simplified_album_data = SimplifiedAlbum.from_dict(data)
        
        return cls(
            **simplified_album_data.__dict__,  # Unpack the base album attributes
            tracks=TrackPage.from_dict(data['tracks']),
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
