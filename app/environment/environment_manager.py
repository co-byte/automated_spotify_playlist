import os
from dotenv import load_dotenv

from app.environment.environment import Environment
from app.logging.logger import get_logger


logger = get_logger(__name__)

class EnvironmentManager:
    def __init__(self, dotenv_path: str = None):
        load_dotenv(dotenv_path)   # Ensures the variables described in the .env file are properly loaded in (default path = root)

    def load_from_env(self) -> Environment:
        """Load environment variables into the Environment dataclass."""
        return Environment(
            config_file=os.getenv("CONFIG_FILE"),
            spotify_user_id=os.getenv("SPOTIFY_USER_ID"),
            spotify_playlist_id=os.getenv("SPOTIFY_PLAYLIST_ID"),
            spotify_client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            spotify_client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            spotify_client_refresh_token=os.getenv("SPOTIFY_CLIENT_REFRESH_TOKEN"),
            spotify_temp_user_auth_code=os.getenv("TEMP_USER_AUTH_CODE")
        )

    def update_refresh_token(self, new_token_value: str) -> None:
        logger.debug("Updating Spotify playlist ID in environment to %s", new_token_value)
        os.putenv("SPOTIFY_CLIENT_REFRESH_TOKEN", new_token_value)

    def update_managed_spotify_playlist_id(self, new_id: str) -> str:
        if new_id == "":
            raise ValueError(
                "Provided Spotify playlist ID is empty. Update of environment is aborted."
                )

        logger.debug("Updating Spotify playlist ID to %s", new_id)
        os.putenv("SPOTIFY_PLAYLIST_ID", new_id)
