from dataclasses import dataclass


@dataclass
class RequestConfig:
    base_address: str = "https://api.spotify.com"
    api_version: str = "v1"
