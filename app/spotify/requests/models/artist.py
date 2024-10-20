from dataclasses import dataclass
from typing import Annotated, Dict, List, Literal, Optional
from pydantic import Field, HttpUrl

from app.spotify.requests.models.image import Image


@dataclass
class Followers:
    # A link to the Web API endpoint providing full details of the followers
    href: Optional[HttpUrl]
    total: int

@dataclass
class SimplifiedArtist:
    external_urls: Dict[Literal["spotify"], HttpUrl]
    href: HttpUrl
    id: str
    name: str
    type: Literal["artist"]
    uri: HttpUrl

@dataclass
class Artist(SimplifiedArtist):
    followers: Followers
    popularity: Annotated[int, Field(ge=0, le=100)]
    genres: List[str]
    images: List[Image]  # Images of the artist in various sizes, ordered widest first
