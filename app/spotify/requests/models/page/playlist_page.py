from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional

from pydantic import HttpUrl

from app.configuration.config import Playlist
from app.spotify.requests.models.page.page import Page


@dataclass
class PlaylistsPage(Page[Playlist]):

    def __init__(
        self,
        href: HttpUrl,
        limit: int,
        next_: Optional[HttpUrl],
        offset: int,
        previous: Optional[HttpUrl],
        total: int,
        items: List[Playlist]
        ) -> None:
        super().__init__(href, limit, next_, offset, previous, total, items)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> PlaylistsPage:
        return super()._from_dict(data, Playlist)
