from __future__ import annotations
from typing import Dict

from app.spotify_service.models.artist.artist import Artist
from app.spotify_service.models.page.page import Page


class ArtistsPage(Page[Artist]):

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> ArtistsPage:
        return super()._from_dict(data, Artist)