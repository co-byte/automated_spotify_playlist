import asyncio
from datetime import datetime
from typing import Callable

from fastapi import FastAPI
import uvicorn

from app.configuration.config import SpotifyConfig
from app.environment.environment_manager import EnvironmentManager
from app.configuration.config_parser import ConfigParser
from app.radio_plus.radio_plus_module import RadioPlusAPI
from app.spotify.authorization.authorization_manager_config import AuthorizationManagerConfig
from app.spotify.authorization.authorization_server import AuthorizationServer
from app.spotify.spotify_module import SpotifyAPI
from app.spotify.authorization.authorization_manager import AuthorizationManager
from app.logging.logger import get_logger


logger = get_logger(__name__)

async def setup_spotify_authorization(spotify_client_id: str, spotify_client_secret: str, spotify_config: SpotifyConfig, get_auth_code_from_server: Callable[[str], str]) -> AuthorizationManager:
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

async def update_playlist(user_id: str,
                          spotify_playlist_name: str,
                          radioplus_url: str,
                          radioplus_channels: str,
                          get_access_token: Callable[[], str]
                          ) -> list[any]:
    # Retrieve datetime of latest playlist update
    date_val = datetime.strftime(datetime.now(),"%Y-%m-%d")
    time_val = datetime.strftime(datetime.now(),"%H:%M:%S")

    spotify = SpotifyAPI(
        user_id=user_id,
        get_access_token=get_access_token
        )

    radioplus = RadioPlusAPI(
        url=radioplus_url,
        channel_mapping=radioplus_channels
    )

    selected_playlist_id = spotify.get_playlist_id(playlist_name=spotify_playlist_name,
                                                   user_id=user_id
                                                   )

    station_name = spotify.get_radio_station_from_playlist_description(selected_playlist_id)

    station_id = radioplus.turn_station_name_into_id(station_name)
    radioplus.get_daily_playlists(station_id=station_id, date=0)

    todays_query = radioplus.export_daily_playlist(station_id=station_id)
    todays_tracks_ids = spotify.get_query_track_ids(query_list=todays_query)
    spotify.generate_playlist_from_query(track_ids=todays_tracks_ids,
                                                  playlist_name=spotify_playlist_name,
                                                  is_public=True,
                                                  description=f"Queued station: {station_name} - Latest update: {date_val} @ {time_val} (GMT+2)",
                                                  is_collaborative=False)
    print(f"{todays_query=}")
    return todays_query

async def main():
    env_manager = EnvironmentManager()
    env = env_manager.load_from_env()
    cfg = ConfigParser(env.config_file).load_config()

    auth_server_config = uvicorn.Config(
            FastAPI(),
            host="localhost",
            port=5000,
            log_level="critical"  # Don't use automatic logging
        )
    auth_server = AuthorizationServer(auth_server_config)
    auth_manager = await setup_spotify_authorization(
        env.spotify_client_id,
        env.spotify_client_secret,
        cfg.spotify_config,
        auth_server.get_authorization_code
        )

    # played_tracks = await update_playlist(
    #     env.spotify_user_id,
    #     cfg.spotify_config.playlist.name,
    #     cfg.radioplus_config.url,
    #     cfg.radioplus_config.channels,
    #     auth_manager.get_access_token
    #     )

    await auth_manager.get_access_token()
    
if __name__ == "__main__":
    asyncio.run(main())
