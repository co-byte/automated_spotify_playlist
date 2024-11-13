import argparse
import asyncio
import datetime
from typing import List, Optional

import uvicorn
from fastapi import FastAPI

import spotify

logger = spotify.get_logger(__name__)


async def setup_spotify_authorization(
    spotify_config: spotify.SpotifyConfig,
    environment: spotify.Environment,
    user_authorization_timeout_seconds: int,
) -> spotify.AuthorizationManager:

    auth_server_config = uvicorn.Config(
        FastAPI(),
        host="localhost",
        port=5000,
        log_level="critical",  # Minimize logging output for auth server
    )
    auth_server = spotify.AuthorizationServer(
        auth_server_config, user_authorization_timeout_seconds
    )
    logger.info("Successfully set up authorization server.")

    auth_config = spotify.AuthorizationManagerConfig(
        client_id=environment.spotify_client_id,
        client_secret=environment.spotify_client_secret,
        auth_url=spotify_config.api.authorization.auth_url,
        token_url=spotify_config.api.authorization.token_url,
        redirect_url=spotify_config.api.authorization.redirect_url,
        scope=spotify_config.api.authorization.permissions,
        authorization_server=auth_server,
        environment=environment,
    )
    auth_manager = spotify.AuthorizationManager(auth_config)
    logger.info("Successfully set up authorization manager.")

    return auth_manager


async def setup_spotify_manager(
    auth_manager: spotify.AuthorizationManager,
    env: spotify.Environment,
    cfg: spotify.SpotifyConfig,
) -> spotify.SpotifyManager:

    api_client_config = spotify.ApiClientConfig()
    api_client = spotify.ApiClient(api_client_config, auth_manager)
    logger.info("Successfully set up Spotify API client.")

    playlist_handler = spotify.PlaylistHandler(api_client, env.spotify_user_id)
    search_handler = spotify.SearchHandler(api_client)
    logger.info("Successfully set up Spotify implementation handlers.")

    spotify_manager_config = spotify.SpotifyManagerConfig(
        environment=env,
        managed_playlist_name=cfg.playlist.name,
        managed_playlist_is_public=True,
        managed_playlist_description="Automatically managed playlist V2.",
        managed_playlist_is_collaborative=False,
        playlist_handler=playlist_handler,
        search_handler=search_handler,
    )
    spotify_manager = spotify.SpotifyManager(spotify_manager_config)
    logger.info("Successfully set up Spotify logic manager.")

    return spotify_manager


async def update_managed_playlist(
    spotify_manager: spotify.SpotifyManager, new_tracks: List[spotify.ExternalTrack]
) -> None:
    try:
        await spotify_manager.update_managed_playlist(new_tracks)
        logger.info("Successfully updated the managed playlist.")

    except Exception as e:
        logger.error("Unable to update the managed playlist: %s", str(e))


async def setup(environment: spotify.EnvironmentTypes) -> spotify.SpotifyManager:
    env = spotify.Environment(environment)

    cfg_parser = spotify.ConfigParser(env.spotify_config_file)
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
    env_type = spotify.EnvironmentTypes(env_arg) if env_arg else spotify.EnvironmentTypes.DEVELOPMENT

    spotify_manager = await setup(env_type)

    hardcoded_tracks = [
        spotify.ExternalTrack("Bonkers (live)", "Bizkit Park"),
        spotify.ExternalTrack("No Stress", "Laurent Wolf"),
        spotify.ExternalTrack("You Know I'm No Good", "Arctic Monkeys"),
        spotify.ExternalTrack("Sun In Her Eyes", "Tom Helsen"),
        spotify.ExternalTrack("First It Giveth", "Queens Of The Stone Age"),
        spotify.ExternalTrack("Nieuws Studio Brussel", None),
        spotify.ExternalTrack("Squeeze Me", "Kraak & Smaak Ft Ben Westbeech"),
    ]

    # Update the managed playlist indefinitely once every day
    while True:
        await update_managed_playlist(
            spotify_manager=spotify_manager, new_tracks=hardcoded_tracks
        )
        await asyncio.sleep(datetime.timedelta(days=1).total_seconds())


if __name__ == "__main__":
    asyncio.run(main())
