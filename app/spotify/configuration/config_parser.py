from typing import Any, Dict

import pydantic
import yaml

from app.logging.logger import get_logger
from app.spotify.configuration.spotify_config import Api, Authorization, Playlist, SpotifyConfig


logger = get_logger(__name__)

_ENCODING = "utf-8"

class ConfigParser:
    def __init__(self, spotify_config_file: pydantic.FilePath):
        self.__spotify_config_file = spotify_config_file

    def load_spotify_config(self) -> SpotifyConfig:
        """Load and parse the Spotify configuration file."""

        try:
            with open(self.__spotify_config_file, 'r', encoding=_ENCODING) as file:
                config_data = yaml.safe_load(file)
            return self.__parse_spotify_config(config_data)

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Configuration file {self.__spotify_config_file} not found.") from e
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file: {e}") from e

    def __parse_spotify_config(self, cfg: Dict[str, Any]) -> SpotifyConfig:
        try:
            playlist = Playlist(
                name=cfg["playlist"]["name"],
                description=cfg["playlist"]["description"]
            )

            auth_config = cfg["api"]["authorization"]
            authorization = Authorization(
                auth_url=auth_config["auth_url"],
                redirect_url=auth_config["redirect_url"],
                permissions=auth_config["permissions"],
                token_url=auth_config["token_url"]
            )

            api = Api(
                version=cfg["api"]["version"],
                authorization=authorization
            )

            return SpotifyConfig(playlist=playlist, api=api)

        except KeyError as e:
            raise KeyError(f"Missing key in Spotify configuration data: {e}") from e
