from __future__ import annotations
import json
from dataclasses import dataclass

from app.spotify.authorization.authorization_server import AuthorizationServer
from app.spotify.environment.environment import Environment


@dataclass
class AuthorizationManagerConfig:
    # Client credentials
    client_id: str
    client_secret: str

    # Initial authorization
    auth_url: str
    redirect_url: str
    scope: str

    # Tokens
    token_url: str

    # External objects
    authorization_server: AuthorizationServer
    environment: Environment

    @classmethod
    def from_dict(cls, config_data: dict[str, str]) -> AuthorizationManagerConfig:
        """Creates an AuthorizationManagerConfig instance from a dictionary."""
        return cls(
            client_id=config_data.get("client_id", ""),
            client_secret=config_data.get("client_secret", ""),
            auth_url=config_data.get("auth_url", ""),
            token_url=config_data.get("token_url", ""),
            redirect_url=config_data.get("redirect_url", ""),
            scope=config_data.get("scope", ""),
            authorization_server=config_data.get("authorization_server", ""),
            environment=config_data.get("environment", "")
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
        data = self.to_dict()
        data["client_secret"] = f"{self.client_secret[:4]}****" if self.client_secret else ""
        return json.dumps(data, indent=4)
