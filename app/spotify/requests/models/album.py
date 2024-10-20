from dataclasses import dataclass
from typing import Annotated, Dict, List, Literal, Optional
import datetime

from pydantic import Field, HttpUrl

from app.spotify.requests.models.artist import SimplifiedArtist
from app.spotify.requests.models.copyright import Copyright
from app.spotify.requests.models.external import ExternalIds
from app.spotify.requests.models.image import Image
from app.spotify.requests.models.simplified_track import SimplifiedTrack


@dataclass
class TrackPage:
    href: HttpUrl
    limit: Annotated[int, Field(ge=1)]
    next: Optional[HttpUrl]
    offset: Annotated[int, Field(ge=0)]
    previous: Optional[HttpUrl]
    total: Annotated[int, Field(ge=0)]
    items: List[SimplifiedTrack]

@dataclass
class Album:
    # 1. Basic Information
    name: Annotated[str, Field(min_length=1, max_length=255)]
    album_type: Literal["album", "single", "compilation"]
    artists: List[SimplifiedArtist]
    total_tracks: Annotated[int, Field(ge=1)]
    tracks: TrackPage   # Paginated track information

    # 2. Identifiers
    id: str
    uri: str
    external_urls: Dict[str, HttpUrl]
    external_ids: ExternalIds   # External identifiers like ISRC, EAN, etc.

    # 3. Release Information
    release_date: datetime.date # Date in YYYY, YYYY-MM, or YYYY-MM-DD format
    release_date_precision: Literal["year", "month", "day"]
    label: Annotated[str, Field(min_length=1, max_length=255)]  # Record label

    # 4. Availability & Restrictions
    available_markets: List[str]  # ISO 3166-1 alpha-2 country codes (e.g., "US", "CA")
    restrictions: Optional[Dict[str, str]]  # Content restrictions, if any

    # 5. Popularity & Genre
    genres: List[str]   # List of genres the album belongs to
    popularity: Annotated[int, Field(ge=0, le=100)] # Popularity score (0-100)

    # 6. Media
    images: List[Image] # Cover art in various sizes
    copyrights: List[Copyright]

    # 7. Spotify API Link
    href: HttpUrl   # Link to full album details in Spotify API
