from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Literal, Optional

from app.spotify.requests.models.external import ExternalUrls
from app.spotify.requests.models.follower import Followers


@dataclass
class User:
    external_urls: ExternalUrls
    followers: Followers
    href: str
    id: str
    type: Literal["user"]
    uri: str
    display_name: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict) -> User:
        return cls(
            external_urls=ExternalUrls.from_dict(data['external_urls']),
            followers=Followers.from_dict(data['followers']),
            href=data['href'],
            id=data['id'],
            type=data['type'],
            uri=data['uri'],
            display_name=data.get('display_name')
        )

    def to_dict(self) -> Dict:
        return {
            "external_urls": self.external_urls.to_dict(),
            "followers": self.followers.to_dict(),
            "href": self.href,
            "id": self.id,
            "type": self.type,
            "uri": self.uri,
            "display_name": self.display_name
        }
