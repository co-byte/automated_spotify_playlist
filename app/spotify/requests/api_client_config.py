from dataclasses import dataclass


@dataclass
class ApiClientConfig:
    base_address: str = "https://api.spotify.com"
    api_version: str = "v1"
