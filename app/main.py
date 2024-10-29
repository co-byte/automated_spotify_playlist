import asyncio
from typing import Callable

from fastapi import FastAPI
import uvicorn

from app.configuration.config import SpotifyConfig
from app.configuration.config_parser import ConfigParser
from app.environment.environment_manager import EnvironmentManager
from app.logging.logger import get_logger
from app.radio_plus import radio_plus
from app.spotify.authorization.authorization_manager_config import AuthorizationManagerConfig
from app.spotify.authorization.authorization_server import AuthorizationServer
from app.spotify.logic.spotify_manager import SpotifyManager
from app.spotify.logic.spotify_manager_config import SpotifyManagerConfig
from app.spotify.requests.repository.api_client.api_client import ApiClient
from app.spotify.requests.repository.api_client.api_client_config import ApiClientConfig
from app.spotify.requests.repository.playlist_handler import PlaylistHandler
from app.spotify.requests.repository.search_handler import SearchHandler
from app.spotify.authorization.authorization_manager import AuthorizationManager


logger = get_logger(__name__)

async def _setup_spotify_authorization(spotify_client_id: str, spotify_client_secret: str, spotify_config: SpotifyConfig, get_auth_code_from_server: Callable[[str], str]) -> AuthorizationManager:
    auth_config = AuthorizationManagerConfig(
            spotify_client_id,
            spotify_client_secret,
            spotify_config.api.authorization.url,
            spotify_config.api.authorization.token_url,
            spotify_config.api.authorization.redirect_url,
            spotify_config.api.authorization.permissions
        )
    auth_manager = AuthorizationManager(
        auth_config,
        get_auth_code_from_server
        )
    return auth_manager

async def _update_managed_playlist(
    spotify_manager: SpotifyManager
    ) -> None:

    new_tracks = radio_plus.ingest_new_tracks()

    await spotify_manager.update_managed_playlist(new_tracks)
    logger.info("Succesfully updated the managed playlist")


async def main():
    env_manager = EnvironmentManager()
    env = env_manager.load_from_env()

    cfg_parser = ConfigParser(env.config_file)
    cfg = cfg_parser.load_config()

    auth_server_config = uvicorn.Config(
            FastAPI(),
            host="localhost",
            port=5000,
            log_level="critical"  # Don't use automatic logging
        )
    auth_server = AuthorizationServer(auth_server_config)
    logger.info("Succesfully setup authorization server.")

    auth_manager = await _setup_spotify_authorization(
        env.spotify_client_id,
        env.spotify_client_secret,
        cfg.spotify_config,
        auth_server.get_authorization_code
        )
    logger.info("Succesfully setup authorization manager.")

    api_client_config = ApiClientConfig()
    api_client = ApiClient(
        api_client_config,
        auth_manager.build_authorization_headers
        )
    logger.info("Succesfully setup Spotify API client.")

    playlist_handler = PlaylistHandler(api_client, env.spotify_user_id)
    search_handler = SearchHandler(api_client)
    logger.info("Succesfully setup Spotify implemtation handlers.")

    spotify_manager_config = SpotifyManagerConfig(
        playlist_handler=playlist_handler,
        search_handler=search_handler,
        managed_playlist_id=env.spotify_playlist_id,
        managed_playlist_name=cfg.spotify_config.playlist.name,
        managed_playlist_is_public=True,
        managed_playlist_is_collaborative=False,
        managed_playlist_description="Automatically managed playlist V2.",
        update_stored_automated_playlist_id=env_manager.update_managed_spotify_playlist_id
    )
    spotify_manager = SpotifyManager(spotify_manager_config)
    logger.info("Succesfully setup Spotify logic manager.")

    await _update_managed_playlist(spotify_manager=spotify_manager)
    logger.info("Succesfully updated the managed playlist.")

    logger.critical("End of program.")

if __name__ == "__main__":
    asyncio.run(main())
