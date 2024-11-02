import asyncio
import datetime
from typing import Tuple

from fastapi import FastAPI
import uvicorn

from app.spotify.environment.environment import Environment
from app.spotify.environment.environment_manager import EnvironmentManager
from app.logging.logger import get_logger
from app.spotify.authorization.authorization_manager_config import AuthorizationManagerConfig
from app.spotify.authorization.authorization_server import AuthorizationServer
from app.spotify.configuration.config_parser import ConfigParser
from app.spotify.logic.spotify_manager import SpotifyManager
from app.spotify.logic.spotify_manager_config import SpotifyManagerConfig
from app.spotify.requests.repository.api_client.api_client import ApiClient
from app.spotify.requests.repository.api_client.api_client_config import ApiClientConfig
from app.spotify.requests.repository.playlist_handler import PlaylistHandler
from app.spotify.requests.repository.search_handler import SearchHandler
from app.spotify.authorization.authorization_manager import AuthorizationManager
from app.vrtmax.vrtmax_client import VRTMaxClient
from app.vrtmax.config.vrtmax_client_config import VRTMaxClientConfig
from app.spotify.configuration.spotify_config import SpotifyConfig

logger = get_logger(__name__)


async def setup_spotify_authorization(
    spotify_client_id: str, spotify_client_secret: str, spotify_config: SpotifyConfig
) -> AuthorizationManager:
    
    auth_server_config = uvicorn.Config(
        FastAPI(),
        host="localhost",
        port=5000,
        log_level="critical"  # Minimize logging output for auth server
    )
    auth_server = AuthorizationServer(auth_server_config)
    logger.info("Successfully set up authorization server.")

    auth_config = AuthorizationManagerConfig(
        spotify_client_id,
        spotify_client_secret,
        spotify_config.api.authorization.auth_url,
        spotify_config.api.authorization.token_url,
        spotify_config.api.authorization.redirect_url,
        spotify_config.api.authorization.permissions
    )
    auth_manager = AuthorizationManager(auth_config, auth_server)
    logger.info("Successfully set up authorization manager.")

    return auth_manager

async def setup_spotify_manager(
    auth_manager: AuthorizationManager,
    env: Environment,
    env_manager: EnvironmentManager,
    cfg: SpotifyConfig,
) -> SpotifyManager:

    api_client_config = ApiClientConfig()
    api_client = ApiClient(api_client_config, auth_manager)
    logger.info("Successfully set up Spotify API client.")

    playlist_handler = PlaylistHandler(api_client, env.spotify_user_id)
    search_handler = SearchHandler(api_client)
    logger.info("Successfully set up Spotify implementation handlers.")

    spotify_manager_config = SpotifyManagerConfig(
        playlist_handler=playlist_handler,
        search_handler=search_handler,
        managed_playlist_id=env.spotify_playlist_id,
        managed_playlist_name=cfg.playlist.name,
        managed_playlist_is_public=True,
        managed_playlist_is_collaborative=False,
        managed_playlist_description="Automatically managed playlist V2.",
        update_stored_automated_playlist_id=env_manager.update_managed_spotify_playlist_id
    )
    spotify_manager = SpotifyManager(spotify_manager_config)
    logger.info("Successfully set up Spotify logic manager.")

    return spotify_manager

async def update_managed_playlist(
    spotify_manager: SpotifyManager, vrtmax_client: VRTMaxClient
) -> None:
    try:
        new_tracks = vrtmax_client.ingest_new_tracks()
        await spotify_manager.update_managed_playlist(new_tracks)
        logger.info("Successfully updated the managed playlist.")

    except Exception:
        logger.error("Unable to update the managed playlist")


async def setup() -> Tuple[SpotifyManager, VRTMaxClient]:
    env_manager = EnvironmentManager()
    env = env_manager.load_from_env()

    cfg_parser = ConfigParser(env.spotify_config_file)
    spotify_config = cfg_parser.load_spotify_config()

    spotify_auth_manager = await setup_spotify_authorization(
        spotify_client_id=env.spotify_client_id,
        spotify_client_secret=env.spotify_client_secret,
        spotify_config=spotify_config
    )
    spotify_manager = await setup_spotify_manager(
        auth_manager=spotify_auth_manager, env=env, env_manager=env_manager, cfg=spotify_config
    )

    vrtmax_client_config = VRTMaxClientConfig()
    vrtmax_client = VRTMaxClient(vrtmax_client_config)
    logger.info("Successfully set up VRTMax client.")

    return (spotify_manager, vrtmax_client)

async def main() -> None:
    spotify_manager, vrtmax_client = await setup()

    # Update the managed playlist indefinitely once every day
    while True:
        await update_managed_playlist(
            spotify_manager=spotify_manager, vrtmax_client=vrtmax_client
        )
        await asyncio.sleep(datetime.timedelta(days=1).total_seconds())


if __name__ == "__main__":
    asyncio.run(main())
