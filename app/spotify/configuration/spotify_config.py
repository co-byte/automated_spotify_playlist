from dataclasses import dataclass, asdict
import json


@dataclass
class Playlist:
    name: str
    description: str

    def __str__(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class Authorization:
    auth_url: str
    redirect_url: str
    permissions: str
    token_url: str
    user_auth_timemout_seconds: int

    def __str__(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class Api:
    version: str
    authorization: Authorization

    def __str__(self):
        return json.dumps(asdict(self), indent=2)


@dataclass
class SpotifyConfig:
    playlist: Playlist
    api: Api

    def __str__(self):
        return json.dumps(asdict(self), indent=2)
