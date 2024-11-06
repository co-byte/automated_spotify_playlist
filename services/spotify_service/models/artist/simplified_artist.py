from __future__ import annotations
from dataclasses import dataclass
from pydantic import HttpUrl
from typing import Dict, Literal


@dataclass
class SimplifiedArtist:
    external_urls: Dict[Literal["spotify"], HttpUrl]
    href: HttpUrl
    id: str
    name: str
    type: Literal["artist"]
    uri: HttpUrl

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> SimplifiedArtist:
        return cls(
            external_urls=data['external_urls'],
            href=data['href'],
            id=data['id'],
            name=data['name'],
            type=data['type'],
            uri=data['uri']
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "external_urls": self.external_urls,
            "href": self.href,
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "uri": self.uri
        }
