import json
import os
from dotenv import load_dotenv
from typing import Optional

from app.spotify_service.logging.logger import get_logger
from app.spotify_service.environment.environment_types import EnvironmentTypes


logger = get_logger(__name__)

_DEV_ENV_PATH = "app\\spotify_service\\environment\\.env"
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
    def __init__(self, environment: EnvironmentTypes) -> None:
        # Only manually load the .env file variables in development.
        # For the production environment, the secrets get injected via Github Environments.
        self.__env = environment
        logger.debug("Initializing handler for (%s) environment.", environment)

        if self.__env == EnvironmentTypes.DEVELOPMENT:
            self.__env_file_path: str = _DEV_ENV_PATH

            logger.info("Loading environment variables from local .env file '%s'.", _DEV_ENV_PATH)
            success = load_dotenv(_DEV_ENV_PATH)

            if success:
                logger.info("Environment variables loaded successfully.")
            else:
                logger.warning("Unable to load environment from provided .env file.")

    def __get_env_var(self, key: str) -> Optional[str]:
        """Retrieve an environment variable and optionally mask its value in logs."""
        value = os.getenv(key)
        if not value:
            logger.warning("Environment variable '%s' is missing or not set.", key)
            return

        # Only log at most 3 characters followed by '****'
        visible_char_count = max(0, min(3, len(value)-3))
        masked_value = value[:visible_char_count] + "****"
        logger.debug("Environment variable '%s' retrieved: %s", key, masked_value)

        return value

    @property
    def spotify_config_file(self) -> Optional[str]:
        return self.__get_env_var(_SPOTIFY_CONFIG_FILE)

    @property
    def spotify_user_id(self) -> Optional[str]:
        return self.__get_env_var(_SPOTIFY_USER_ID)

    @property
    def spotify_playlist_id(self) -> Optional[str]:
        return self.__get_env_var(_SPOTIFY_PLAYLIST_ID)

    @spotify_playlist_id.setter
    def spotify_playlist_id(self, value: str) -> None:
        if not value:
            raise ValueError("Provided Spotify playlist ID is empty.")

        logger.info("Setting Spotify playlist ID to '%s'.", value)
        os.putenv(_SPOTIFY_PLAYLIST_ID, value)

        if self.__env == EnvironmentTypes.DEVELOPMENT:
            self.__update_env_file(_SPOTIFY_PLAYLIST_ID, value)

    @property
    def spotify_client_id(self) -> Optional[str]:
        return self.__get_env_var(_SPOTIFY_CLIENT_ID)

    @property
    def spotify_client_secret(self) -> Optional[str]:
        return self.__get_env_var(_SPOTIFY_CLIENT_SECRET)

    @property
    def spotify_client_refresh_token(self) -> Optional[str]:
        return self.__get_env_var(_SPOTIFY_CLIENT_REFRESH_TOKEN)

    @spotify_client_refresh_token.setter
    def spotify_client_refresh_token(self, value: str) -> None:
        if not value:
            raise ValueError("Provided Spotify client refresh token is empty.")

        logger.info("Setting Spotify client refresh token.")
        os.putenv(_SPOTIFY_CLIENT_REFRESH_TOKEN, value)

        if self.__env == EnvironmentTypes.DEVELOPMENT:
            self.__update_env_file(_SPOTIFY_CLIENT_REFRESH_TOKEN, value)

    @property
    def spotify_temp_user_auth_code(self) -> Optional[str]:
        return self.__get_env_var(_SPOTIFY_TEMP_USER_AUTH_CODE)

    def __update_env_file(self, key: str, value: str) -> None:
        """Update the .env file with a new key-value pair."""
        if not os.path.exists(self.__env_file_path):
            logger.error("The .env file path '%s' does not exist.", _DEV_ENV_PATH)
            return

        try:
            logger.info("Updating .env file: setting %s to %s", key, value)

            lines = []
            with open(self.__env_file_path, 'r', encoding=_ENV_FILE_ENCODING) as env_file:
                found = False
                for line in env_file:
                    if line.startswith(key + "="):
                        line = f"{key}={value}\n"
                        found = True
                    lines.append(line)
                
                if not found:
                    lines.append(f"{key}={value}\n")

            with open(self.__env_file_path, 'w', encoding=_ENV_FILE_ENCODING) as env_file:
                env_file.writelines(lines)
            logger.info("Environment variable '%s' set successfully in .env file.", key)

        except IOError as e:
            logger.error("Failed to update .env file '%s': %s", _DEV_ENV_PATH, str(e))

    def __str__(self) -> str:
        """Display the environment variables in JSON format."""
        env_dict = {
            "spotify_client_id": self.spotify_client_id,
            "spotify_playlist_id": self.spotify_playlist_id,
            "spotify_client_secret": self.spotify_client_secret,
            "spotify_client_refresh_token": self.spotify_client_refresh_token,
            "spotify_user_id": self.spotify_user_id,
            "spotify_config_file": self.spotify_config_file,
        }
        return json.dumps(env_dict, indent=2)