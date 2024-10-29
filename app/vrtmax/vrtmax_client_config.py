from dataclasses import dataclass
from typing import Annotated

import httpx
import pydantic


@dataclass
class VRTMaxClientConfig:
    api_url: pydantic.HttpUrl
    component_id: str
    fetched_track_count: Annotated[int, pydantic.Field(ge=0)]
    headers: httpx.Headers
    query: str
