from __future__ import annotations
from typing import Dict

from app.spotify.requests.models.page.page import Page
from app.spotify.requests.models.track.simplified_track import SimplifiedSpotifyTrack


class TracksPage(Page[SimplifiedSpotifyTrack]):

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> TracksPage:
        return super()._from_dict(data, SimplifiedSpotifyTrack)
