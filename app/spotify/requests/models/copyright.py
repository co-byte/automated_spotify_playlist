from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Literal


@dataclass
class Copyright:
    text: str
    type: Literal["C", "P"] # C = the copyright, P = the sound recording (performance) copyright

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> Copyright:
        return cls(
            text=data['text'],
            type=data['type']
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "text": self.text,
            "type": self.type
        }
