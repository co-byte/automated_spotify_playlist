from __future__ import annotations
from typing import Dict

from spotify.models.artist.artist import Artist
from spotify.models.page.page import Page


class ArtistsPage(Page[Artist]):

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> ArtistsPage:
        return super()._from_dict(data, Artist)
