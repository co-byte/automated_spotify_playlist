from dataclasses import dataclass
from typing import Dict


@dataclass
class Playlist:
    name: str
    description: str

    def __str__(self):
        return (
            f"Playlist:\n"
            f"  name: '{self.name}'\n"
            f"  description: '{self.description}'"
        )


@dataclass
class Authorization:
    url: str
    redirect_url: str
    permissions: str
    token_url: str

    def __str__(self):
        return (
            f"Authorization:\n"
            f"  url: '{self.url}'\n"
            f"  redirect_url: '{self.redirect_url}'\n"
            f"  permissions: '{self.permissions}'\n"
            f"  token_url: '{self.token_url}'"
        )


@dataclass
class Api:
    version: str
    authorization: Authorization

    def __str__(self):
        return (
            f"Api:\n"
            f"  version: '{self.version}'\n"
            f"  authorization: {self.authorization}"
        )


@dataclass
class SpotifyConfig:
    playlist: Playlist
    api: Api

    def __str__(self):
        return (
            f"SpotifyConfig:\n"
            f"  playlist: {self.playlist}\n"
            f"  api: {self.api}"
        )


@dataclass
class RadioPlusConfig:
    url: str
    channels: Dict[str, int]

    def __str__(self):
        channels_str = "\n".join(f"  '{channel}': {number}" for channel, number in self.channels.items())
        return (
            f"RadioPlus:\n"
            f"  url: '{self.url}'\n"
            f"  channels:\n{channels_str}"
        )


@dataclass
class Config:
    spotify_config: SpotifyConfig
    radioplus_config: RadioPlusConfig

    def __str__(self):
        return (
            f"Config:\n"
            f"  spotify_config: '{self.spotify_config}'\n"
            f"  radioplus_config: '{self.radioplus_config}'"
        )
