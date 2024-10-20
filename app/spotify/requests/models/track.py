from dataclasses import dataclass
from typing import Annotated

from pydantic import Field

from app.spotify.requests.models.album import Album
from app.spotify.requests.models.external import ExternalIds
from app.spotify.requests.models.simplified_track import SimplifiedTrack


@dataclass
class Track(SimplifiedTrack):
    album: Album
    external_ids: ExternalIds
    popularity: Annotated[int, Field(ge=0, le=100)]
