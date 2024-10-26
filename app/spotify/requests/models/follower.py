from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional

from pydantic import HttpUrl


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
