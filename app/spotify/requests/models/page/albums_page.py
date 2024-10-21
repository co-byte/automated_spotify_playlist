from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

from pydantic import HttpUrl

from app.spotify.requests.models.album.simplified_album import SimplifiedAlbum
from app.spotify.requests.models.page.page import Page


@dataclass
class AlbumsPage(Page[SimplifiedAlbum]):

    def __init__(
        self,
        href: HttpUrl,
        limit: int,
        next_: Optional[HttpUrl],
        offset: int,
        previous: Optional[HttpUrl],
        total: int,
        items: List[SimplifiedAlbum]
        ) -> None:
        super().__init__(href, limit, next_, offset, previous, total, items)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> AlbumsPage:
        return super()._from_dict(data, SimplifiedAlbum)
