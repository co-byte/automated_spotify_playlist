from dataclasses import dataclass


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
    auth_url: str
    redirect_url: str
    permissions: str
    token_url: str

    def __str__(self):
        return (
            f"Authorization:\n"
            f"  url: '{self.auth_url}'\n"
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
