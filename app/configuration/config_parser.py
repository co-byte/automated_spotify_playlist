from typing import Any

import yaml

from app.configuration.config import Api, Authorization, Config, Playlist, SpotifyConfig, RadioPlusConfig


class ConfigParser:
    def __init__(self, config_file: str):
        self.__config_file = config_file

    def load_config(self) -> Config:
        """Load and parse the configuration file."""
        try:
            with open(self.__config_file, 'r', encoding="utf-8") as file:
                config_data = yaml.safe_load(file)
            return self.__parse_config(config_data)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Configuration file {self.__config_file} not found.") from e
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file: {e}") from e

    def __parse_config(self, cfg: Any) -> Config:
        """Parse the loaded YAML data into the Config dataclass."""
        spotify_config = self.__parse_spotify_config(cfg)
        radioplus_config = self.__parse_radioplus_config(cfg)
        return Config(
            spotify_config=spotify_config, 
            radioplus_config=radioplus_config
        )

    def __parse_spotify_config(self, cfg: Any) -> SpotifyConfig:
        """Parse the Spotify configuration section from the YAML data."""
        try:
            playlist_config = cfg["spotify"]["playlist"]
            playlist = Playlist(
                name=playlist_config["name"],
                description=playlist_config["description"]
            )

            auth_config = cfg["spotify"]["api"]["authorization"]
            authorization = Authorization(
                url=auth_config["url"],
                redirect_url=auth_config["redirect_url"],
                permissions=auth_config["permissions"],
                token_url=auth_config["token_url"]
            )

            api = Api(
                version=cfg["spotify"]["api"]["version"],
                authorization=authorization
            )

            return SpotifyConfig(playlist=playlist, api=api)
        except KeyError as e:
            raise KeyError(f"Missing key in Spotify configuration data: {e}") from e

    def __parse_radioplus_config(self, cfg: Any) -> RadioPlusConfig:
        """Parse the RadioPlus configuration section from the YAML data."""
        try:
            return RadioPlusConfig(
                url=cfg["radio_plus"]["url"],
                channels=cfg["radio_plus"]["channels"]
            )
        except KeyError as e:
            raise KeyError(f"Missing key in RadioPlus configuration data: {e}") from e
