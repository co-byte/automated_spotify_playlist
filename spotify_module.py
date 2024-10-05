import requests
import base64
import datetime
from urllib.parse import urlencode
from pprint import pprint
import json
import os

date_val = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d")
time_val = datetime.datetime.strftime(datetime.datetime.now(),"%H:%M:%S") 


class SpotifyAPI():
    client_id = None
    client_secret = None
    response_type = None
    redirect_uri = None
    state = None
    scope = "ugc-image-upload+user-modify-playback-state+user-read-playback-state+\
                user-read-currently-playing+user-follow-modify+user-follow-read+user-read-recently-played+\
                user-read-playback-position+user-top-read+playlist-read-collaborative+playlist-modify-public+\
                playlist-read-private+playlist-modify-private+app-remote-control+streaming+user-read-email+\
                user-read-private+user-library-modify+user-library-read".replace(" ", "")
    access_token = None
    refresh_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    token_url = "https://accounts.spotify.com/api/token"
    api_version = 'v1'
    user_id = None
    user_data_path = os.path.realpath("spotify_user_data.json")
    
    def __init__(self, client_id, client_secret=None, response_type=None, redirect_uri=None, state=None, user_id=None, user_data_path = None,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state = state
        self.user_id = user_id if user_id != None else self.__load_json(self.user_data_path)["current_user_id"]
        self.refresh_token = self.__load_json(self.user_data_path)["refresh_token"]
        self.user_data_path = user_data_path

    # AUTHORIZATION HELP METHODS
    def __get_client_credentials(self):
        """
        Returns a base64 encode string
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("client_id or client_secret are not set")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def __handle_request_status(self, request):
        if request.status_code not in (200, 201, 204):
            raise Exception(f"{request.status_code=}")

    def __process_token_data(self, request):
        token_data = request.json()
        access_token = token_data["access_token"]
        expires_in = token_data["expires_in"]
        now = datetime.datetime.now()
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        if "refresh_token" in token_data.keys():
            refresh_token = token_data["refresh_token"]
            self.__write_json({"refresh_token": refresh_token},
                      self.user_data_path)
            self.refresh_token = refresh_token

    @staticmethod
    def __load_json(file_name):
        file = open(file_name)
        content = json.load(file)
        return content

    @staticmethod
    def __write_json(file_name, data):
        with open(file_name, "w") as target:
            target.write(json.dump(data))

    # AUTHORIZATION USING AUTENTICATION
    def request_authorization(self):
        base_authorization_url = "https://accounts.spotify.com/authorize"
        url_body = {"client_id": self.client_id,
                    "response_type": "code",
                    "redirect_uri": self.redirect_uri,
                    "scope": self.scope}
        url_encoded_body = urlencode(url_body).replace("%2B", "+")
        return f"{base_authorization_url}?{url_encoded_body}"

    def request_access_and_refresh_tokens(self, auth_code):
        base_url = "https://accounts.spotify.com/api/token"  # same
        client_creds_b64 = self.__get_client_credentials()
        headers = {"Authorization": f"Basic {client_creds_b64}",
                   "Content-Type": "application/x-www-form-urlencoded"
                   }
        data = {"grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": self.redirect_uri
                }
        request = requests.post(url=base_url, data=data, headers=headers)
        self.__handle_request_status(request)
        self.__process_token_data(request)

    def __refresh_access_token(self):
        base_url = "https://accounts.spotify.com/api/token"  # same
        client_creds_b64 = self.__get_client_credentials()
        headers = {"Authorization": f"Basic {client_creds_b64}",
                   "Content-Type": "application/x-www-form-urlencoded"
                   }
        url_body = {"grant_type": "refresh_token",
                    "refresh_token": self.__load_json(self.user_data_path)["refresh_token"]
                    }
        request = requests.post(url=base_url, data=url_body, headers=headers)
        self.__handle_request_status(request)
        self.__process_token_data(request)

    # AUTHORIZATION USING CLIENT CREDENTIALS
    def __get_token_headers(self):
        client_creds_b64 = self.__get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }

    def __get_token_data(self):
        return {
            "grant_type": "client_credentials"
        }

    def __perform_auth(self):
        token_url = self.token_url
        token_data = self.__get_token_data()
        token_headers = self.__get_token_headers()
        r = requests.post(token_url, token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
            raise Exception("Could not authenticate client.")
            # return False
        data = r.json()
        access_token = data["access_token"]
        expires_in = data["expires_in"]
        now = datetime.datetime.now()
        expires = now + datetime.timedelta(seconds=expires_in)

        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now

    def __get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if (token == None) or (expires < now):
            if self.refresh_token == None:
                self.__perform_auth()
                print(f"{self.refresh_token=}")
            else:
                self.__refresh_access_token()
            return self.__get_access_token()
        return token

    def __get_resource_header(self):
        access_token = self.__get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        return headers

    # BASE GET REQUEST
    def __get_request(self, url):
        headers = self.__get_resource_header()
        request = requests.get(url=url, headers=headers)
        self.__handle_request_status(request)
        return request.json()

    def __get_resource_request(self, endpoint='tracks', url_encoded_query=None):
        url = f"https://api.spotify.com/{self.api_version}/{endpoint}"
        if url_encoded_query != None:
            url += f"?{url_encoded_query}"
        return self.__get_request(url=url)

    # BASE POST REQUEST
    def __post_request(self, url, data=None):
        headers = self.__get_resource_header()
        request = requests.post(url=url, data=data, headers=headers)
        self.__handle_request_status(request)
        return request.json()

    # BASE PUT
    def __put_request(self, url_endpoint: str, data={}, return_json=True):
        url = f"https://api.spotify.com/{self.api_version}/{url_endpoint}"
        headers = self.__get_resource_header()
        request = requests.put(url=url, data=data, headers=headers)
        self.__handle_request_status(request)
        if return_json:
            return request.json()
        return request

    # SEARCHES
    def __base_search(self, query_params):
        endpoint = f"https://api.spotify.com/{self.api_version}/search"
        lookup_url = f"{endpoint}?{query_params}"
        return self.__get_request(url=lookup_url)

    def search(self, query: str, operator=None, operator_query=None, print_first_result=False, search_type="artist", result_limit=50) -> dict:
        if isinstance(query, dict):
            query = " ".join([f"{key}:{val}" for key, val in query.items()])
        if operator_query != None:
            if isinstance(operator_query, str):
                query = f"{query} {operator} {operator_query}"

        query_params = urlencode({"q": query,
                                  "type": search_type.lower(),
                                  "limit": result_limit
                                  })
        # print(query_params)
        result = self.__base_search(query_params=query_params)

        if print_first_result:  # TODO - rewrite and put in seperate method
            print("")
            print(
                f"{search_type} : {result[f'{search_type}s']['items'][0]['name']}")
            if search_type == "track":
                print(
                    f"artist : {result[f'{search_type}s']['items'][0]['artists'][0]['name']}")
            print(f"id : {result[f'{search_type}s']['items'][0]['id']}")
        return result

    def get_id(self, query=None, operator=None, operator_query=None, search_type="artist", print_first_result=False):
        assumed_track = self.search(query=query,
                                    operator=operator,
                                    operator_query=operator_query,
                                    search_type=search_type,
                                    print_first_result=print_first_result,
                                    result_limit=1,
                                    )
        try:
            # selects the id of the first item
            assumed_id = assumed_track[f"{search_type}s"]["items"][0]["id"]
        except IndexError:
            return None
        return assumed_id

    # TODO: complete method
    def get_query_track_ids(self, query_list: list[str]) -> set[str]:
        """ 
        Turns an externally acquired list of queries (strings of tracks names and artists) into a set of ids 
        """
        id_set = set(self.get_id(query=query, search_type="")
                      for query in query_list)
        return id_set

    # BASIC ITEM GETTERS
    def get_album(self, album_id):
        return self.__get_resource_request(endpoint=f'albums/{album_id}')

    def get_artist(self, artist_id):
        return self.__get_resource_request(endpoint=f'artists/{artist_id}')

    def get_track(self, track_id):
        return self.__get_resource_request(endpoint=f"tracks/{track_id}")

    def get_playlist(self, playlist_id):
        return self.__get_resource_request(endpoint=f"playlists/{playlist_id}")

    def get_users_playlistst(self, user_id="me", print_results_is_on=False, limit=50):
        if user_id != "me":
            user_id = f"users/{user_id}"
        query = urlencode({"limit": limit
                           })
        playlists = self.__get_resource_request(
            endpoint=f"{user_id}/playlists", url_encoded_query=query)
        if print_results_is_on:
            [print(playlist["name"]) for playlist in playlists["items"]]
        return playlists

    def get_user_profile(self, user_id):
        return self.__get_resource_request(endpoint=f"users/{user_id}")

    def get_current_user_profile(self, print_out_result=False):
        user_profile = self.__get_resource_request(endpoint="me")
        if print_out_result:
            pprint(user_profile)
        return user_profile

    def get_current_users_top_items(self, type="tracks"):
        top_items = self.__get_resource_request(endpoint=f"me/top/{type}")
        return top_items

    # TRACKS
    def play_track(self):   # TODO: complete method
        pass

    def enqueue_track(self):    # TODO: complete method
        pass

    def dequeue_track(self):    # TODO: complete method
        pass

    def get_track_audio_features(self, _id: str, print_features_is_on=False):
        features = self.__get_resource_request(
            endpoint=f"audio-features/{_id}")
        if print_features_is_on and len(features) > 3:
            pprint(features)
        return features

    # PLAYLISTS
    def create_new_playlist(self, name: str, user_id: str, is_public=True, description=None, is_collaborative=False):
        user_id = user_id if user_id != None else self.user_id
        data = json.dumps({"name": name,
                           "public": is_public,
                           "description": description,
                           "collaborative": is_collaborative
                           })

        url = f"https://api.spotify.com/{self.api_version}/users/{user_id}/playlists"
        response = self.__post_request(url=url, data=data)
        return response

    def get_playlist_id(self, playlist_name: str, user_id:str) -> str:
        user_playlists = self.get_users_playlistst(user_id)
        playlist_names_and_ids = {
            playlist["name"]: playlist["id"] for playlist in user_playlists["items"]}
        if playlist_name not in playlist_names_and_ids.keys():
            raise Exception(
                f"User '{user_id}' does not have any playlists called '{playlist_name}'")
        return playlist_names_and_ids[playlist_name]

    def get_playlist_description(self, playlist_id:str)->str:
        playlist_content = self.get_playlist(playlist_id)
        playlist_description = playlist_content["description"]
        return playlist_description
    
    def get_radio_station_from_playlist_description(self, playlist_id: str) -> str:
        playlist_description = self.get_playlist_description(playlist_id)
        # print(f"{playlist_description=}")
        start_idx = playlist_description.find(":")
        end_idx = playlist_description.find("-",start_idx)
        # print(f"{start_idx=}   {type(start_idx)}")
        # print(f"{end_idx=}   {type(end_idx)}")
        playlist_name = playlist_description[start_idx+1:end_idx].strip()
        return playlist_name

    def add_items_to_playlist(self, item_ids: list[str], playlist_id):
        if not isinstance(item_ids[0], str):
            raise Exception("item_ids must be a list containing only strings")
        item_ids = [f"spotify:track:{id}" for id in item_ids]

        data = json.dumps(item_ids)
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        self.__post_request(url=url, data=data)

    def get_playlist_items(self, playlist_id: str):
        return self.__get_resource_request(endpoint=f"playlists/{playlist_id}/tracks")

    def check_if_item_in_playlist(self, item_id: str, playlist_id: str):
        playlist_items = self.get_playlist_items()
        if item_id in playlist_items:
            return True
        return False

    def update_playlist_items(self, playlist_id: str, track_id_list: list[str]):
        tracks = [f"spotify:track:{id}" for id in track_id_list if id != None][-100:]   # takes the last 100 tracks (max defined by SpotifyAPI)
        url_endpoint = f"playlists/{playlist_id}/tracks?uris=" + ",".join(tracks)
        self.__put_request(url_endpoint=url_endpoint)

    def update_playlist_details(self, playlist_id: str, name=None, public=None, collaborative=None, description=None):
        url_endpoint = f"playlists/{playlist_id}"
        data = {"name": name,
                "public": public,
                "collaborative": collaborative,
                "description": description
                }
        data = json.dumps({key: val for (key, val) in data.items() if val != None})
        request = self.__put_request(
            url_endpoint=url_endpoint, data=data, return_json=False)
        return request

    # TODO: complete method
    def remove_items_from_playlist(self, item_ids, playlist_id):
        return

    def check_if_user_has_playlist(self, user_id=user_id, playlist_id=None, playlist_name=None):
        users_playlists = self.get_users_playlistst(user_id=user_id)
        if playlist_id != None:
            keyword = "id"
        elif playlist_name != None:
            keyword = "name"
        else:
            raise Exception(
                "Neither playlist_id nor playlist_name were given, at least one is needed.")
        playlists = set(playlist[keyword]
                        for playlist in users_playlists["items"])
        if (playlist_id in playlists) or (playlist_name in playlists):
            return True
            pprint(f"{playlist_name} -> {playlist_id}")
        return False

    def generate_playlist_from_query(self, track_ids: list[str], playlist_name=None, playlist_id=None, user_id= None,
                                     description=None, is_public=False, is_collaborative=False):
        """
        Takes a list of track ids as input and either creates a new playlist containing these tracks or adds them to an already existing playlist; returns the added tracks
        """
        user_id = user_id if user_id != None else self.user_id 
        if self.check_if_user_has_playlist(playlist_id=playlist_id, playlist_name=playlist_name, user_id=user_id) == True: 
            if playlist_id == None:
                playlist_id = self.get_playlist_id(playlist_name, user_id)
            self.update_playlist_items(playlist_id, track_ids)
            self.update_playlist_details(playlist_id,playlist_name,is_public,is_collaborative,description)
        else:
            new_playlist = self.create_new_playlist(playlist_name,user_id,is_public,description,is_collaborative)   # FIXME CODE 403
            new_playlist_id = new_playlist["id"]
            tracks = self.update_playlist_items(new_playlist_id,track_ids)