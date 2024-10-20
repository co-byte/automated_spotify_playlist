from dataclasses import dataclass
from typing import Annotated, Dict, List, Literal, Optional

from pydantic import Field, HttpUrl

from app.spotify.requests.models.artist import SimplifiedArtist
from app.spotify.requests.models.external import ExternalUrls


@dataclass
class LinkedFrom:
    external_urls: Dict[Literal["spotify"], HttpUrl]
    href: HttpUrl
    id: str
    type: Literal["track"]
    uri: str

@dataclass
class SimplifiedTrack:
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
    is_playable: bool
    is_local: bool
    restrictions: Optional[Dict[str, str]]

    # 4. Media Information
    disc_number: Annotated[int, Field(ge=1)]
    duration_ms: Annotated[int, Field(ge=0)]
    explicit: bool
    track_number: Annotated[int, Field(ge=1)]

    # 5. Linked Data
    linked_from: Optional[LinkedFrom]
