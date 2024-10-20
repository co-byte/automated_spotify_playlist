from dataclasses import dataclass
from typing import Optional

from pydantic import HttpUrl


@dataclass
class ExternalIds:
    isrc: Optional[str]  # International Standard Recording Code
    ean: Optional[str]   # International Article Number
    upc: Optional[str]   # Universal Product Code

@dataclass
class ExternalUrls:
    """A reusable structure for external URLs (e.g., Spotify links)."""
    spotify: HttpUrl  # Since it's always "spotify", we can simplify it
