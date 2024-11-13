from __future__ import annotations
from dataclasses import dataclass
from pydantic import Field, HttpUrl
from typing import Annotated, Dict, List, Literal, Optional

from spotify.models.artist.simplified_artist import SimplifiedArtist
from spotify.models.external import ExternalUrls


@dataclass
class LinkedFrom:
    external_urls: Dict[Literal["spotify"], HttpUrl]
    href: HttpUrl
    id: str
    type: Literal["track"]
    uri: str

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "LinkedFrom":
        return cls(
            external_urls=data["external_urls"],
            href=data["href"],
            id=data["id"],
            type=data["type"],
            uri=data["uri"],
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "external_urls": self.external_urls,
            "href": self.href,
            "id": self.id,
            "type": self.type,
            "uri": self.uri,
        }


@dataclass
class SimplifiedSpotifyTrack:
    # 1. Identifiers & Basic Info
    id: str
    name: str
    uri: str
    href: HttpUrl
    type: Literal["track"]

    # 2. Artists & External Information
    artists: List[SimplifiedArtist]
    external_urls: ExternalUrls
    preview_url: Optional[HttpUrl]

    # 3. Availability & Market Info
    available_markets: List[str]  # ISO 3166-1 alpha-2 country codes (e.g., "US", "CA")
    is_playable: Optional[bool]
    is_local: bool
    restrictions: Optional[Dict[str, str]]

    # 4. Media Information
    disc_number: Annotated[int, Field(ge=1)]
    duration_ms: Annotated[int, Field(ge=0)]
    explicit: bool
    track_number: Annotated[int, Field(ge=1)]

    # 5. Linked Data
    linked_from: Optional[LinkedFrom]

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> SimplifiedSpotifyTrack:
        return cls(
            id=data["id"],
            name=data["name"],
            uri=data["uri"],
            href=data["href"],
            type=data["type"],
            artists=[SimplifiedArtist.from_dict(artist) for artist in data["artists"]],
            external_urls=data["external_urls"],
            preview_url=data.get("preview_url"),
            available_markets=data["available_markets"],
            is_playable=data.get("is_playable"),
            is_local=data["is_local"],
            restrictions=data.get("restrictions"),
            disc_number=data["disc_number"],
            duration_ms=data["duration_ms"],
            explicit=data["explicit"],
            track_number=data["track_number"],
            linked_from=(
                LinkedFrom.from_dict(data["linked_from"])
                if data.get("linked_from")
                else None
            ),
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "uri": self.uri,
            "href": self.href,
            "type": self.type,
            "artists": [artist.to_dict() for artist in self.artists],
            "external_urls": self.external_urls,
            "preview_url": self.preview_url,
            "available_markets": self.available_markets,
            "is_playable": self.is_playable,
            "is_local": self.is_local,
            "restrictions": self.restrictions,
            "disc_number": self.disc_number,
            "duration_ms": self.duration_ms,
            "explicit": self.explicit,
            "track_number": self.track_number,
            "linked_from": self.linked_from.to_dict() if self.linked_from else None,
        }
