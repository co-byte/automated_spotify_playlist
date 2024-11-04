import argparse
import asyncio
import datetime
from typing import Optional, Tuple

from fastapi import FastAPI
import uvicorn

from app.spotify.environment.environment import Environment
from app.logging.logger import get_logger
from app.spotify.authorization.authorization_manager_config import AuthorizationManagerConfig
from app.spotify.authorization.authorization_server import AuthorizationServer
from app.spotify.configuration.config_parser import ConfigParser
from app.spotify.environment.environment_types import EnvironmentTypes
from app.spotify.logic.spotify_manager import SpotifyManager
from app.spotify.logic.spotify_manager_config import SpotifyManagerConfig
from app.spotify.requests.repository.api_client.api_client import ApiClient
from app.spotify.requests.repository.api_client.api_client_config import ApiClientConfig
from app.spotify.requests.repository.playlist_handler import PlaylistHandler
from app.spotify.requests.repository.search_handler import SearchHandler
from app.spotify.authorization.authorization_manager import AuthorizationManager
from app.vrtmax_service.vrtmax.vrtmax_client import VRTMaxClient
from app.vrtmax_service.config.vrtmax_client_config import VRTMaxClientConfig
from app.spotify.configuration.spotify_config import SpotifyConfig

logger = get_logger(__name__)


async def setup_spotify_authorization(
    spotify_config: SpotifyConfig,
    environment: Environment,
    user_authorization_timeout_seconds: int
) -> AuthorizationManager:

    auth_server_config = uvicorn.Config(
        FastAPI(),
        host="localhost",
        port=5000,
        log_level="critical"  # Minimize logging output for auth server
    )
    auth_server = AuthorizationServer(auth_server_config, user_authorization_timeout_seconds)
    logger.info("Successfully set up authorization server.")

    auth_config = AuthorizationManagerConfig(
        client_id=environment.spotify_client_id,
        client_secret=environment.spotify_client_secret,
        auth_url=spotify_config.api.authorization.auth_url,
        token_url=spotify_config.api.authorization.token_url,
        redirect_url=spotify_config.api.authorization.redirect_url,
        scope=spotify_config.api.authorization.permissions,
        authorization_server=auth_server,
        environment=environment
    )
    auth_manager = AuthorizationManager(auth_config)
    logger.info("Successfully set up authorization manager.")

    return auth_manager

async def setup_spotify_manager(
    auth_manager: AuthorizationManager,
    env: Environment,
    cfg: SpotifyConfig,
) -> SpotifyManager:

    api_client_config = ApiClientConfig()
    api_client = ApiClient(api_client_config, auth_manager)
    logger.info("Successfully set up Spotify API client.")

    playlist_handler = PlaylistHandler(api_client, env.spotify_user_id)
    search_handler = SearchHandler(api_client)
    logger.info("Successfully set up Spotify implementation handlers.")

    spotify_manager_config = SpotifyManagerConfig(
        environment=env,
        managed_playlist_name=cfg.playlist.name,
        managed_playlist_is_public=True,
        managed_playlist_description="Automatically managed playlist V2.",
        managed_playlist_is_collaborative=False,
        playlist_handler=playlist_handler,
        search_handler=search_handler,
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

    except Exception as e:
        logger.error("Unable to update the managed playlist: %s", str(e))

async def setup(environment: EnvironmentTypes) -> Tuple[SpotifyManager, VRTMaxClient]:
    env = Environment(environment)

    cfg_parser = ConfigParser(env.spotify_config_file)
    spotify_config = cfg_parser.parse()

    spotify_auth_manager = await setup_spotify_authorization(
        environment=env,
        spotify_config=spotify_config,
        user_authorization_timeout_seconds = spotify_config.api.authorization.user_auth_timemout_seconds
    )
    spotify_manager = await setup_spotify_manager(
        auth_manager=spotify_auth_manager, env=env, cfg=spotify_config
    )
    
    vrtmax_client_config = VRTMaxClientConfig()
    vrtmax_client = VRTMaxClient(vrtmax_client_config)
    logger.info("Successfully set up VRTMax client.")

    return (spotify_manager, vrtmax_client)

async def main() -> None:
    parser = argparse.ArgumentParser(description='Run the Spotify application.')
    parser.add_argument('--env', type=str, required=False, help="Environment to run the application ('development' or 'production')")

    # Retrieve the environment type
    env_arg: Optional[str] = parser.parse_args().env
    env_type = EnvironmentTypes(env_arg) if env_arg else EnvironmentTypes.DEVELOPMENT

    spotify_manager, vrtmax_client = await setup(env_type)

    # Update the managed playlist indefinitely once every day
    while True:
        await update_managed_playlist(
            spotify_manager=spotify_manager, vrtmax_client=vrtmax_client
        )
        await asyncio.sleep(datetime.timedelta(days=1).total_seconds())


if __name__ == "__main__":
    asyncio.run(main())
