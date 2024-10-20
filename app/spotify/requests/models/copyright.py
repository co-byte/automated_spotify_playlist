from dataclasses import dataclass
from typing import Literal


@dataclass
class Copyright:
    text: str
    type: Literal["C", "P"] # C = the copyright, P = the sound recording (performance) copyright
