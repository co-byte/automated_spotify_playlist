from __future__ import annotations
from dataclasses import dataclass
from pydantic import Field, HttpUrl
from typing import Annotated, Dict


@dataclass
class Image:
    url: HttpUrl
    height: Annotated[int, Field(ge=0)]  # Height in pixels
    width: Annotated[int, Field(ge=0)]  # Width in pixels

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> Image:
        return cls(url=data["url"], height=data["height"], width=data["width"])

    def to_dict(self) -> Dict[str, str]:
        return {"url": self.url, "height": self.height, "width": self.width}
