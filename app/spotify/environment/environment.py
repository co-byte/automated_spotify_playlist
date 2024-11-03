import json
import os
import pydantic
from dotenv import load_dotenv
from typing import Optional
from app.logging.logger import get_logger


logger = get_logger(__name__)

_DEFAULT_ENV_PATH = "app\\spotify\\environment\\.env"
_ENV_FILE_ENCODING = "UTF-8"

# Values declared in the .env file
_SPOTIFY_CONFIG_FILE = "SPOTIFY_CONFIG_FILE"
_SPOTIFY_USER_ID = "SPOTIFY_USER_ID"
_SPOTIFY_PLAYLIST_ID = "SPOTIFY_PLAYLIST_ID"
_SPOTIFY_CLIENT_ID = "SPOTIFY_CLIENT_ID"
_SPOTIFY_CLIENT_SECRET = "SPOTIFY_CLIENT_SECRET"
_SPOTIFY_CLIENT_REFRESH_TOKEN = "SPOTIFY_CLIENT_REFRESH_TOKEN"
_SPOTIFY_TEMP_USER_AUTH_CODE = "TEMP_USER_AUTH_CODE"


class Environment:
    def __init__(self, dotenv_path: pydantic.FilePath = _DEFAULT_ENV_PATH) -> None:
        self.__env_file_path: str = dotenv_path

        logger.info("Loading environment variables from '%s'.", dotenv_path)

        success = load_dotenv(dotenv_path)
        if not success:
            logger.warning("Unable to load environment from provided .env file.")

    @property
    def spotify_config_file(self) -> Optional[str]:
        return os.getenv(_SPOTIFY_CONFIG_FILE)

    @property
    def spotify_user_id(self) -> Optional[str]:
        return os.getenv(_SPOTIFY_USER_ID)

    @property
    def spotify_playlist_id(self) -> Optional[str]:
        return os.getenv(_SPOTIFY_PLAYLIST_ID)

    @spotify_playlist_id.setter
    def spotify_playlist_id(self, value: str) -> None:
        if not value:
            raise ValueError("Provided Spotify playlist ID is empty.")

        logger.info("Setting Spotify playlist ID to '%s'.", value)

        os.putenv(_SPOTIFY_PLAYLIST_ID, value)
        self.__update_env_file(_SPOTIFY_PLAYLIST_ID, value)

    @property
    def spotify_client_id(self) -> Optional[str]:
        return os.getenv(_SPOTIFY_CLIENT_ID)

    @property
    def spotify_client_secret(self) -> Optional[str]:
        return os.getenv(_SPOTIFY_CLIENT_SECRET)

    @property
    def spotify_client_refresh_token(self) -> Optional[str]:
        return os.getenv(_SPOTIFY_CLIENT_REFRESH_TOKEN)

    @spotify_client_refresh_token.setter
    def spotify_client_refresh_token(self, value: str) -> None:
        if not value:
            raise ValueError("Provided Spotify client refresh token is empty.")

        logger.info("Setting Spotify client refresh token to '%s'.", value[:5]+"****")

        os.putenv(_SPOTIFY_CLIENT_REFRESH_TOKEN, value)
        self.__update_env_file(_SPOTIFY_CLIENT_REFRESH_TOKEN, value)

    @property
    def spotify_temp_user_auth_code(self) -> Optional[str]:
        return os.getenv(_SPOTIFY_TEMP_USER_AUTH_CODE)

    def __update_env_file(self, key: str, value: str) -> None:
        if not self.__env_file_path:
            raise ValueError(f"The .env file path '{_DEFAULT_ENV_PATH}' does not exist.")

        logger.info("Updating .env file: setting %s to %s", key, value)

        # Read the existing content of the .env file
        lines = []
        with open(self.__env_file_path, 'r', encoding=_ENV_FILE_ENCODING) as env_file:
            for line in env_file:
                if line.startswith(key):
                    line = f"{key}={value}\n"
                lines.append(line)

        # Write the updated content back to the .env file
        with open(self.__env_file_path, 'w', encoding=_ENV_FILE_ENCODING) as env_file:
            env_file.writelines(lines)

    def __str__(self) -> str:
        """Displays the environment variables in JSON format."""
        env_dict = {
            "spotify_client_id": self.spotify_client_id,
            "spotify_playlist_id": self.spotify_playlist_id,
            "spotify_client_secret": (
                self.spotify_client_secret[:4] + "****" if self.spotify_client_secret else None
            ),
            "spotify_client_refresh_token": (
                self.spotify_client_refresh_token[:4] + "****" if self.spotify_client_refresh_token else None
            ),
            "spotify_user_id": self.spotify_user_id,
            "spotify_config_file": self.spotify_config_file
        }
        return json.dumps(env_dict, indent=2)
