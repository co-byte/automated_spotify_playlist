from typing import Any, Dict

import pydantic
import yaml

from app.logging.logger import get_logger
from app.spotify.configuration.spotify_config import Api, Authorization, Playlist, SpotifyConfig


logger = get_logger(__name__)

_CONFIG_FILE_ENCODING = "UTF-8"

class ConfigParser:
    def __init__(self, spotify_config_file: pydantic.FilePath) -> None:
        self.__config = self.__load_spotify_config(spotify_config_file)

    def parse(self) -> SpotifyConfig:
        return self.__config

    def __load_spotify_config(self, config_file: pydantic.FilePath) -> SpotifyConfig:
        """Load and parse the Spotify configuration file."""
        try:
            logger.debug("Attempting to load Spotify configurations from config file.")
            with open(config_file, 'r', encoding=_CONFIG_FILE_ENCODING) as file:
                config_data = yaml.safe_load(file)

            if not isinstance(config_data, dict):
                raise ValueError("The configuration file must contain a valid YAML dictionary structure.")

            return self.__parse_spotify_config(config_data)

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Configuration file not found.") from e
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file: {e}") from e
        except ValueError as e:
            raise ValueError(f"Configuration file content error: {e}") from e

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
                token_url=auth_config["token_url"],
                user_auth_timemout_seconds=auth_config["user_auth_timemout_seconds"]
            )
            api = Api(
                authorization=authorization,
                version=cfg["api"]["version"]
            )

            spotify_config = SpotifyConfig(playlist=playlist, api=api)
            logger.debug("Parsed Spotify config: %s", spotify_config)
            return spotify_config

        except KeyError as e:
            raise KeyError(f"Missing key in Spotify configuration data: {e}") from e
