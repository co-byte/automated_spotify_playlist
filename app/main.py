from datetime import datetime

from app.environment.environment_manager import EnvironmentManager
from app.configuration.config_parser import ConfigParser
from radio_plus.radio_plus_module import RadioPlusAPI
from spotify.spotify_module import SpotifyAPI


# Load environment variables and configurations
env = EnvironmentManager().load_from_env()
cfg = ConfigParser(env.config_file).load_config()

# Retrieve datetime of latest playlist update
date_val = datetime.strftime(datetime.now(),"%Y-%m-%d")
time_val = datetime.strftime(datetime.now(),"%H:%M:%S")

client_id = env.spotify_client_id
client_secret = env.spotify_client_secret
client_refresh_token = env.spotify_client_refresh_token
redirect_uri = cfg.spotify_config.api.authorization.redirect_url
user_id = env.spotify_user_id
token_url = cfg.spotify_config.api.authorization.token_url
selected_playlist_name = cfg.spotify_config.playlist.name
scope = cfg.spotify_config.api.authorization.permissions

def update_playlist():
    spotify = SpotifyAPI(client_id=client_id,
                         client_secret=client_secret,
                         redirect_uri=redirect_uri,
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

if __name__ == "__main__":
    played_tracks = update_playlist()

    try_count = 0
    while(try_count < 3 and not played_tracks):
        played_tracks = update_playlist
        try_count+=1
