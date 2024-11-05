from __future__ import annotations
from typing import Dict

from app.spotify_service.models.page.page import Page
from app.spotify_service.models.playlist import Playlist


class PlaylistsPage(Page[Playlist]):

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> PlaylistsPage:
        return super()._from_dict(data, Playlist)
