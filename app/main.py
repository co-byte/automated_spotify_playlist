import os
from datetime import datetime
from dotenv import load_dotenv

from radio_plus.radio_plus_module import RadioPlusAPI
from spotify.spotify_module import SpotifyAPI
import temp_secrets

# Load environment variables from .env file
load_dotenv()

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
client_refresh_token = os.getenv("SPOTIFY_CLIENT_REFRESH_TOKEN")
redirect_uri = "https://github.com/co-byte?tab=repositories"
user_id = temp_secrets.user_id
date_val = datetime.strftime(datetime.now(),"%Y-%m-%d")
time_val = datetime.strftime(datetime.now(),"%H:%M:%S") 
selected_playlist_name = "Todays generated playlist"


def update_playlist():
    spotify = SpotifyAPI(client_id=client_id,
                         client_secret=client_secret,
                         client_refresh_token=client_refresh_token,
                         redirect_uri=redirect_uri
                         )
    selected_playlist_id = spotify.get_playlist_id(playlist_name=selected_playlist_name,
                                                   user_id=user_id
                                                   )

    station_name = spotify.get_radio_station_from_playlist_description(selected_playlist_id)

    station_id = RadioPlusAPI.turn_station_name_into_id(station_name)
    RadioPlusAPI.get_daily_playlists(station_id=station_id, date=0)

    todays_query = RadioPlusAPI.export_daily_playlist(station_id=station_id)
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

    tryCount = 0
    while(tryCount < 3 and not played_tracks):
        played_tracks = update_playlist
        tryCount+=1
