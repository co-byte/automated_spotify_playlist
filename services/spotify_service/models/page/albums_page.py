from __future__ import annotations
from typing import Dict

from services.spotify_service.models.album.simplified_album import SimplifiedAlbum
from services.spotify_service.models.page.page import Page


class AlbumsPage(Page[SimplifiedAlbum]):

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> AlbumsPage:
        return super()._from_dict(data, SimplifiedAlbum)
