from dataclasses import dataclass
from typing import Optional

from app.spotify.requests.models.page.albums_page import AlbumsPage
from app.spotify.requests.models.page.artists_page import ArtistsPage
from app.spotify.requests.models.page.tracks_page import TracksPage


class UnusedPage: """A placeholder class for unused page objects."""


@dataclass
class SearchResponse:
    tracks: TracksPage
    artists: ArtistsPage
    albums: AlbumsPage
    playlists: Optional[UnusedPage]

    # These values are present in the response but are of no use within the current scope of this application
    shows: Optional[UnusedPage]
    episodes: Optional[UnusedPage]
    audiobooks: Optional[UnusedPage]
    