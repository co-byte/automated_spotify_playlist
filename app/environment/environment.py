from dataclasses import dataclass


@dataclass
class Environment:
    spotify_config_file: str

    # User data
    spotify_user_id: str
    spotify_playlist_id: str = None

    # Authentication data for the Spotify API
    spotify_client_id: str = None
    spotify_client_secret: str = None
    spotify_client_refresh_token: str = None
    spotify_temp_user_auth_code: str = None

    def __str__(self):
        # Mask sensitive information
        masked_client_secret = self.spotify_client_secret[:4] + "****"
        masked_refresh_token = self.spotify_client_refresh_token[:4] + "****"

        return (
            f"Environment:\n"
            f"  spotify_client_id: '{self.spotify_client_id}'\n"
            f"  spotify_playlist_id: '{self.spotify_playlist_id}'\n"
            f"  spotify_client_secret: '{masked_client_secret}'\n"
            f"  spotify_client_refresh_token: '{masked_refresh_token}'\n"
            f"  spotify_user_id: '{self.spotify_user_id}'\n"
            f"  spotify_config_file: '{self.spotify_config_file}'"
            )
