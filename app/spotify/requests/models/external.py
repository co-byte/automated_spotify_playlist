from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional

from pydantic import HttpUrl


@dataclass
class ExternalIds:
    isrc: Optional[str]  # International Standard Recording Code
    ean: Optional[str]   # International Article Number
    upc: Optional[str]   # Universal Product Code

    @classmethod
    def from_dict(cls, data: Dict[str, Optional[str]]) -> ExternalIds:
        return cls(
            isrc=data.get('isrc'),
            ean=data.get('ean'),
            upc=data.get('upc')
        )

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "isrc": self.isrc,
            "ean": self.ean,
            "upc": self.upc
        }

@dataclass
class ExternalUrls:
    spotify: HttpUrl  # Since it's always "spotify", we can simplify it

    @classmethod
    def from_dict(cls, data: Dict[str, HttpUrl]) -> ExternalUrls:
        return cls(
            spotify=data['spotify']
        )

    def to_dict(self) -> Dict[str, HttpUrl]:
        return {
            "spotify": self.spotify
        }
