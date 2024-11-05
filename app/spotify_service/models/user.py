from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Literal, Optional

from app.spotify_service.models.external import ExternalUrls
from app.spotify_service.models.follower import Followers


@dataclass
class User:
    display_name: Optional[str]
    external_urls: ExternalUrls
    href: str
    id: str
    type: Literal["user"]
    uri: str
    followers: Optional[Followers]

    @classmethod
    def from_dict(cls, data: Dict) -> User:
        return cls(
            display_name=data.get("display_name"),
            external_urls=ExternalUrls.from_dict(data["external_urls"]),
            href=data["href"],
            id=data["id"],
            type=data["type"],
            uri=data["uri"],
            followers=(
                Followers.from_dict(data["followers"])
                if data.get("followers")
                else None
            ),
        )

    def to_dict(self) -> Dict:
        return {
            "external_urls": self.external_urls.to_dict(),
            "followers": self.followers.to_dict(),
            "href": self.href,
            "id": self.id,
            "type": self.type,
            "uri": self.uri,
            "display_name": self.display_name,
        }
