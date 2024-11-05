from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.spotify_service.models.page.albums_page import AlbumsPage
from app.spotify_service.models.page.artists_page import ArtistsPage
from app.spotify_service.models.page.page import Page
from app.spotify_service.models.page.tracks_page import TracksPage


class UnusedPage:
    """A placeholder class for unused page objects."""


@dataclass
class SearchResponse:
    tracks: Optional[TracksPage]
    artists: Optional[ArtistsPage]
    albums: Optional[AlbumsPage]

    # These values are present in the response but are of no use within the current scope of this application
    _playlists: Optional[UnusedPage] = None
    _shows: Optional[UnusedPage] = None
    _episodes: Optional[UnusedPage] = None
    _audiobooks: Optional[UnusedPage] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResponse":
        def parse_page(page_class: Page, page_data: Dict[str, Any]):
            return page_class.from_dict(page_data) if page_data else None

        return cls(
            tracks=parse_page(TracksPage, data.get("tracks")),
            artists=parse_page(ArtistsPage, data.get("artists")),
            albums=parse_page(AlbumsPage, data.get("albums")),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tracks": self.tracks.to_dict() if self.tracks else None,
            "artists": self.artists.to_dict() if self.artists else None,
            "albums": self.albums.to_dict() if self.albums else None,
        }
