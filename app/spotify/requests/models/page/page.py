from __future__ import annotations
from typing import Annotated, Dict, List, Optional, TypeVar, Generic
from abc import ABC, abstractmethod

from pydantic import Field, HttpUrl

# Define a type variable for the generic class
T = TypeVar('T')

# Abstract base class for pagination
class Page(ABC, Generic[T]):
    href: HttpUrl
    limit: Annotated[int, Field(ge=1)]
    next: Optional[HttpUrl]
    offset: Annotated[int, Field(ge=0)]
    previous: Optional[HttpUrl]
    total: Annotated[int, Field(ge=0)]
    items: List[T]

    @abstractmethod
    def __init__(self, href: HttpUrl, limit: int, next_: Optional[HttpUrl],
                 offset: int, previous: Optional[HttpUrl], total: int,
                 items: List[T]) -> None:
        self.href = href
        self.limit = limit
        self.next = next_
        self.offset = offset
        self.previous = previous
        self.total = total
        self.items = items

    @classmethod
    def _from_dict(cls, data: Dict[str, str], item_cls: type[T]) -> Page[T]:
        """Construct a Page from a dictionary using a specified item class."""
        return cls(
            href=data['href'],
            limit=data['limit'],
            next_=data.get('next'),
            offset=data['offset'],
            previous=data.get('previous'),
            total=data['total'],
            items=[item_cls.from_dict(item) for item in data['items']]
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "href": self.href,
            "limit": self.limit,
            "next": self.next,
            "offset": self.offset,
            "previous": self.previous,
            "total": self.total,
            "items": [item.to_dict() for item in self.items]
        }
