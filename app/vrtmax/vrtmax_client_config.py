from dataclasses import dataclass
from typing import Annotated

import httpx
import pydantic

from app.vrtmax.query import GET_SONGS_AND_ARTISTS_QUERY


@dataclass
class VRTMaxClientConfig:
    api_url: pydantic.HttpUrl
    component_id: str
    fetched_track_count: Annotated[int, pydantic.Field(ge=0)]
    headers: httpx.Headers
    query: str = GET_SONGS_AND_ARTISTS_QUERY
