import os
from dotenv import load_dotenv

from app.environment.environment import Environment

class EnvironmentManager:
    def __init__(self, dotenv_path: str = None):
        load_dotenv(dotenv_path)   # Ensures the variables described in the .env file are properly loaded in (default path = root)

    def load_from_env(self) -> Environment:
        """Load environment variables into the Environment dataclass."""
        return Environment(
            spotify_client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            spotify_client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            spotify_client_refresh_token=os.getenv("SPOTIFY_CLIENT_REFRESH_TOKEN"),
            spotify_user_id=os.getenv("SPOTIFY_USER_ID"),
            config_file=os.getenv("CONFIG_FILE"),
            spotify_temp_user_auth_code=os.getenv("TEMP_USER_AUTH_CODE")
        )

    def update_refresh_token(self, new_token_value: str) -> None:
        os.environ["SPOTIFY_CLIENT_REFRESH_TOKEN"] = new_token_value
