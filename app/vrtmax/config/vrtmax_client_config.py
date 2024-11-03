from dataclasses import dataclass, field
from typing import Annotated

import httpx
import pydantic
from app.vrtmax.config.constants import API_URL, COMPONENT_ID, FETCHED_TRACK_COUNT, HEADERS, GET_SONGS_AND_ARTISTS_QUERY


@dataclass
class VRTMaxClientConfig:
    api_url: pydantic.HttpUrl = API_URL
    component_id: str = COMPONENT_ID
    fetched_track_count: Annotated[int, pydantic.Field(ge=0)] = FETCHED_TRACK_COUNT
    headers: httpx.Headers = field(default_factory=lambda: httpx.Headers(HEADERS))
    query: str = GET_SONGS_AND_ARTISTS_QUERY
