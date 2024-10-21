from __future__ import annotations
from dataclasses import dataclass
from typing import Annotated, Dict, List, Optional
from pydantic import Field, HttpUrl

from app.spotify.requests.models.artist.simplified_artist import SimplifiedArtist
from app.spotify.requests.models.image import Image


@dataclass
class Followers:
    # A link to the Web API endpoint providing full details of the followers
    href: Optional[HttpUrl]
    total: int

    @classmethod
    def from_dict(cls, data: Dict[str, Optional[str]]) -> Followers:
        return cls(
            href=data.get('href'),
            total=data['total']
        )

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "href": self.href,
            "total": self.total
        }

@dataclass
class Artist(SimplifiedArtist):
    followers: Followers
    popularity: Annotated[int, Field(ge=0, le=100)]
    genres: List[str]
    images: List[Image]  # Images of the artist in various sizes, ordered widest first

    @classmethod
    def from_dict(cls, data: Dict) -> 'Artist':
        simplified_artist = super().from_dict(data) # Call the superclass from_dict and add additional fields
        return cls(
            **simplified_artist.__dict__,  # Use unpacking to include base fields
            followers=Followers.from_dict(data['followers']),
            popularity=data['popularity'],
            genres=data['genres'],
            images=[Image.from_dict(image) for image in data['images']]
        )

    def to_dict(self) -> Dict:
        # Use the superclass's to_dict method and add additional fields
        return {
            **super().to_dict(),  # Include base fields
            "followers": self.followers.to_dict(),
            "popularity": self.popularity,
            "genres": self.genres,
            "images": [image.to_dict() for image in self.images]
        }
