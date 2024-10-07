from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Tokens:
    access_token: AccessToken
    refresh_token: str

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> Tokens:
        return cls(
            access_token = AccessToken.from_dict(data),
            refresh_token = data["refresh_token"]
        )

    def update(self, new_tokens: Tokens) -> None:
        if new_tokens.refresh_token:  # Only update if a new refresh_token is provided
            self.refresh_token = new_tokens.refresh_token
        self.access_token = new_tokens.access_token

@dataclass
class AccessToken:
    token_value: str
    scope: str # Space-separated list of scopes the access token is valid for
    token_type: str
    expires_in: int

    @property
    def is_expired(self) -> bool:
        return self.expires_in <= 0

    @classmethod
    def from_dict(cls, data: dict[str,any]) -> AccessToken:
        return cls(
            token_value=data["access_token"],
            scope=data["scope"],
            token_type=data["token_type"],
            expires_in=data["expires_in"],
        )

    def validate(self):
        """Validates the token response fields."""
        if not self.token_value:
            raise ValueError("Access token must not be empty.")
        if self.expires_in <= 0:
            raise ValueError("Expires_in must be greater than zero.")

    def __str__(self) -> str:
        return self.token_value
