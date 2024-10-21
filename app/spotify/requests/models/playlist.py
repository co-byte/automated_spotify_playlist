from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional

from app.spotify.requests.models.external import ExternalUrls
from app.spotify.requests.models.follower import Followers
from app.spotify.requests.models.image import Image
from app.spotify.requests.models.page.tracks_page import TracksPage
from app.spotify.requests.models.user import User


@dataclass
class Playlist:
    collaborative: bool
    description: Optional[str]
    external_urls: ExternalUrls
    followers: Optional[Followers]
    href: str
    id: str
    images: List[Image]
    name: str
    owner: User
    public: bool
    snapchot_id: str
    tracks: TracksPage
    type: Literal["playlist"]
    uri: str

    @classmethod
    def from_dict(cls, data: Dict) -> Playlist:
        return cls(
            collaborative=data['collaborative'],
            description=data.get('description'),
            external_urls=ExternalUrls.from_dict(data['external_urls']),
            followers=Followers.from_dict(data.get('followers')),
            href=data['href'],
            id=data['id'],
            images=[Image.from_dict(image_data) for image_data in data['images']],
            name=data['name'],
            owner=User.from_dict(data['owner']),
            public=data['public'],
            snapchot_id=data['snapshot_id'],
            tracks=TracksPage.from_dict(data['tracks']),
            type=data['type'],
            uri=data['uri']
        )

    def to_dict(self) -> Dict:
        return {
            "collaborative": self.collaborative,
            "description": self.description,
            "external_urls": self.external_urls.to_dict(),
            "followers": self.followers.to_dict(),
            "href": self.href,
            "id": self.id,
            "images": [image.to_dict() for image in self.images],
            "name": self.name,
            "owner": self.owner.to_dict(),
            "public": self.public,
            "snapshot_id": self.snapchot_id,
            "tracks": self.tracks.to_dict(),
            "type": self.type,
            "uri": self.uri
        }
