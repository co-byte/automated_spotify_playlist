from __future__ import annotations
from typing import Dict, List, Optional

from pydantic import HttpUrl

from app.spotify.requests.models.page.page import Page
from app.spotify.requests.models.track.simplified_track import SimplifiedTrack


class TracksPage(Page[SimplifiedTrack]):

    def __init__(
        self, href: HttpUrl, limit: int, next_: Optional[HttpUrl], offset: int,
        previous: Optional[HttpUrl], total: int, items: List[SimplifiedTrack]
        ) -> None:
        super().__init__(href, limit, next_, offset, previous, total, items)

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> TracksPage:
        return super()._from_dict(data, SimplifiedTrack)
