import argparse
import asyncio
import datetime
from typing import List, Optional

from fastapi import FastAPI
import uvicorn

from services.spotify_service.models.external_track import ExternalTrack
from services.spotify_service.environment.environment import Environment
from services.spotify_service.logging.logger import get_logger
from services.spotify_service.authorization.authorization_manager_config import (
    AuthorizationManagerConfig,
)
from services.spotify_service.authorization.authorization_server import AuthorizationServer
from services.spotify_service.configuration.config_parser import ConfigParser
from services.spotify_service.environment.environment_types import EnvironmentTypes
from services.spotify_service.logic.spotify_manager import SpotifyManager
from services.spotify_service.logic.spotify_manager_config import SpotifyManagerConfig
from services.spotify_service.repository.api_client.api_client import ApiClient
from services.spotify_service.repository.api_client.api_client_config import ApiClientConfig
from services.spotify_service.repository.playlist_handler import PlaylistHandler
from services.spotify_service.repository.search_handler import SearchHandler
from services.spotify_service.authorization.authorization_manager import AuthorizationManager
from services.spotify_service.configuration.spotify_config import SpotifyConfig


logger = get_logger(__name__)


async def setup_spotify_authorization(
    spotify_config: SpotifyConfig,
    environment: Environment,
    user_authorization_timeout_seconds: int,
) -> AuthorizationManager:

    auth_server_config = uvicorn.Config(
        FastAPI(),
        host="localhost",
        port=5000,
        log_level="critical",  # Minimize logging output for auth server
    )
    auth_server = AuthorizationServer(
        auth_server_config, user_authorization_timeout_seconds
    )
    logger.info("Successfully set up authorization server.")

    auth_config = AuthorizationManagerConfig(
        client_id=environment.spotify_client_id,
        client_secret=environment.spotify_client_secret,
        auth_url=spotify_config.api.authorization.auth_url,
        token_url=spotify_config.api.authorization.token_url,
        redirect_url=spotify_config.api.authorization.redirect_url,
        scope=spotify_config.api.authorization.permissions,
        authorization_server=auth_server,
        environment=environment,
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
    spotify_manager: SpotifyManager, new_tracks: List[ExternalTrack]
) -> None:
    try:
        await spotify_manager.update_managed_playlist(new_tracks)
        logger.info("Successfully updated the managed playlist.")

    except Exception as e:
        logger.error("Unable to update the managed playlist: %s", str(e))


async def setup(environment: EnvironmentTypes) -> SpotifyManager:
    env = Environment(environment)

    cfg_parser = ConfigParser(env.spotify_config_file)
    spotify_config = cfg_parser.parse()

    spotify_auth_manager = await setup_spotify_authorization(
        environment=env,
        spotify_config=spotify_config,
        user_authorization_timeout_seconds=spotify_config.api.authorization.user_auth_timemout_seconds,
    )
    spotify_manager = await setup_spotify_manager(
        auth_manager=spotify_auth_manager, env=env, cfg=spotify_config
    )

    return spotify_manager


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Spotify application.")
    parser.add_argument(
        "--env",
        type=str,
        required=False,
        help="Environment to run the application ('development' or 'production')",
    )

    # Retrieve the environment type
    env_arg: Optional[str] = parser.parse_args().env
    env_type = EnvironmentTypes(env_arg) if env_arg else EnvironmentTypes.DEVELOPMENT

    spotify_manager = await setup(env_type)

    hardcoded_tracks = [
        ExternalTrack("Bonkers (live)", "Bizkit Park"),
        ExternalTrack("No Stress", "Laurent Wolf"),
        ExternalTrack("You Know I'm No Good", "Arctic Monkeys"),
        ExternalTrack("Sun In Her Eyes", "Tom Helsen"),
        ExternalTrack("First It Giveth", "Queens Of The Stone Age"),
        ExternalTrack("Nieuws Studio Brussel", None),
        ExternalTrack("Squeeze Me", "Kraak & Smaak Ft Ben Westbeech"),
    ]

    # Update the managed playlist indefinitely once every day
    while True:
        await update_managed_playlist(
            spotify_manager=spotify_manager, new_tracks=hardcoded_tracks
        )
        await asyncio.sleep(datetime.timedelta(days=1).total_seconds())


if __name__ == "__main__":
    asyncio.run(main())
