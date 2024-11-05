from __future__ import annotations
from dataclasses import dataclass
from typing import Annotated, Dict, List, Literal, Optional
import datetime

from pydantic import Field, HttpUrl

from app.spotify_service.models.artist.simplified_artist import SimplifiedArtist
from app.spotify_service.models.image import Image


@dataclass
class SimplifiedAlbum:
    name: Annotated[str, Field(min_length=1, max_length=255)]
    album_type: Literal["album", "single", "compilation"]
    total_tracks: Annotated[int, Field(ge=1)]
    available_markets: List[str]  # ISO 3166-1 alpha-2 country codes
    external_urls: Dict[str, HttpUrl]
    href: HttpUrl  # Link to the Web API endpoint for full details of the album
    id: str
    images: List[Image]
    release_date: datetime.date    
    release_date_precision: Literal["year", "month", "day"]
    restrictions: Optional[Dict[str, str]]
    uri: str
    artists: List[SimplifiedArtist]

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> SimplifiedAlbum:
        return cls(
            name=data['name'],
            album_type=data['album_type'],
            total_tracks=data['total_tracks'],
            available_markets=data['available_markets'],
            external_urls=data['external_urls'],
            href=data['href'],
            id=data['id'],
            images=[Image.from_dict(image) for image in data['images']],
            release_date=data['release_date'],
            release_date_precision=data['release_date_precision'],
            restrictions=data.get('restrictions'),
            uri=data['uri'],
            artists=[SimplifiedArtist.from_dict(artist) for artist in data['artists']],
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "album_type": self.album_type,
            "total_tracks": self.total_tracks,
            "available_markets": self.available_markets,
            "external_urls": self.external_urls,
            "href": self.href,
            "id": self.id,
            "images": [image.to_dict() for image in self.images],
            "release_date": self.release_date,
            "release_date_precision": self.release_date_precision,
            "restrictions": self.restrictions,
            "uri": self.uri,
            "artists": [artist.to_dict() for artist in self.artists],
        }
