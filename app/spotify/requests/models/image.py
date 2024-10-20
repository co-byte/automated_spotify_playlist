from dataclasses import dataclass
from typing import Annotated

from pydantic import Field, HttpUrl


@dataclass
class Image:
    url: HttpUrl
    height: Annotated[int, Field(ge=0)] # Height in pixels
    width: Annotated[int, Field(ge=0)]  # Width in pixels
