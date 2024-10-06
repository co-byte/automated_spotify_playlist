import os

from app.environment.environment import Environment

class EnvironmentManager:
    @staticmethod
    def load_from_env() -> Environment:
        """Load environment variables into the Environment dataclass."""
        return Environment(
            spotify_client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            spotify_client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            spotify_client_refresh_token=os.getenv("SPOTIFY_CLIENT_REFRESH_TOKEN"),
            spotify_user_id=os.getenv("SPOTIFY_USER_ID"),
            config_file=os.getenv("CONFIG_FILE")
        )

    @staticmethod
    def update_refresh_token(new_token_value: str) -> None:
        os.environ["SPOTIFY_CLIENT_REFRESH_TOKEN"] = new_token_value
