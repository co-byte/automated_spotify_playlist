import asyncio
from datetime import datetime

from app.environment.environment import Environment
from app.environment.environment_manager import EnvironmentManager
from app.configuration.config_parser import ConfigParser
from app.radio_plus.radio_plus_module import RadioPlusAPI
from app.spotify.authorization.authorization_manager_config import AuthorizationManagerConfig
from app.spotify.spotify_module import SpotifyAPI
from app.spotify.authorization.authorization_manager import AuthorizationManager


async def setup_authorization(spotify_client_id: str, spotify_client_secret: str, config_manager: ConfigParser) -> AuthorizationManager:
    auth_config = AuthorizationManagerConfig(
            spotify_client_id,
            spotify_client_secret,
            config_manager.spotify_config.api.authorization.url,
            config_manager.spotify_config.api.authorization.token_url,
            config_manager.spotify_config.api.authorization.redirect_url,
            config_manager.spotify_config.api.authorization.permissions
        )
    auth_manager = AuthorizationManager(auth_config)
    return auth_manager

async def update_playlist(env: Environment, cfg: ConfigParser):
    # Retrieve datetime of latest playlist update
    date_val = datetime.strftime(datetime.now(),"%Y-%m-%d")
    time_val = datetime.strftime(datetime.now(),"%H:%M:%S")

    client_id = env.spotify_client_id
    client_secret = env.spotify_client_secret
    client_refresh_token = env.spotify_client_refresh_token
    redirect_uri = cfg.spotify_config.api.authorization.redirect_url
    api_version = cfg.spotify_config.api.version
    user_id = env.spotify_user_id
    token_url = cfg.spotify_config.api.authorization.token_url
    selected_playlist_name = cfg.spotify_config.playlist.name
    scope = cfg.spotify_config.api.authorization.permissions

    spotify = SpotifyAPI(client_id=client_id,
                         client_secret=client_secret,
                         redirect_uri=redirect_uri,
                         api_version=api_version,
                         scope=scope,
                         user_id=user_id,
                         token_url=token_url,
                         client_refresh_token=client_refresh_token,
                         save_refresh_token_callback=EnvironmentManager.update_refresh_token
                         )

    radioplus = RadioPlusAPI(
        url=cfg.radioplus_config.url,
        channel_mapping=cfg.radioplus_config.channels
    )

    selected_playlist_id = spotify.get_playlist_id(playlist_name=selected_playlist_name,
                                                   user_id=user_id
                                                   )

    station_name = spotify.get_radio_station_from_playlist_description(selected_playlist_id)

    station_id = radioplus.turn_station_name_into_id(station_name)
    radioplus.get_daily_playlists(station_id=station_id, date=0)

    todays_query = radioplus.export_daily_playlist(station_id=station_id)
    todays_tracks_ids = spotify.get_query_track_ids(query_list=todays_query)
    spotify.generate_playlist_from_query(track_ids=todays_tracks_ids,
                                                  playlist_name=selected_playlist_name,
                                                  is_public=True,
                                                  description=f"Queued station: {station_name} - Latest update: {date_val} @ {time_val} (GMT+2)",
                                                  is_collaborative=False)
    print(f"{todays_query=}")
    return todays_query

async def main():
    # Load environment variables and configurations
    env_manager = EnvironmentManager()
    env = env_manager.load_from_env()
    cfg = ConfigParser(env.config_file).load_config()
    auth_manager = await setup_authorization(
        env.spotify_client_id,
        env.spotify_client_secret,
        cfg
        )
    print(f"main - Access_token: {await auth_manager.access_token}")
    # played_tracks = await update_playlist(env, cfg)

if __name__ == "__main__":
    asyncio.run(main())