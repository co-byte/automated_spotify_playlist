from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class AuthorizationManagerConfig:
    client_id: str
    client_secret: str
    auth_url: str
    token_url: str
    redirect_url: str
    scope: str

    @classmethod
    def from_dict(cls, config_data: dict[str, str]) -> AuthorizationManagerConfig:
        """Creates an AuthorizationManagerConfig instance from a dictionary."""
        return cls(
            client_id=config_data.get("client_id"),
            client_secret=config_data.get("client_secret"),
            auth_url=config_data.get("auth_url"),
            token_url=config_data.get("token_url"),
            redirect_url=config_data.get("redirect_url"),
            scope=config_data.get("scope"),
        )

    def to_dict(self) -> dict[str, str]:
        """Serializes the config to a dictionary."""
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "auth_url": self.auth_url,
            "token_url": self.token_url,
            "redirect_url": self.redirect_url,
            "scope": self.scope,
        }

def __str__(self) -> str:
    masked_secret = f"{self.client_secret[:4]}****" if self.client_secret else ""
    return (
        f"AuthorizationManagerConfig(\n"
        f"  client_id: {self.client_id},\n"
        f"  client_secret: {masked_secret},\n"
        f"  auth_url: {self.auth_url},\n"
        f"  token_url: {self.token_url},\n"
        f"  redirect_url: {self.redirect_url},\n"
        f"  scope: {self.scope}\n"
        ")"
    )
