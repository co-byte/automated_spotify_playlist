import asyncio
from typing import Dict
import websockets
import json


class RadioPlusAPI:
    playlist_data = None
    todays_programs = None

    def __init__(self, url: str, channel_mapping: Dict[str, int]) -> None:
        self.__url = url
        self.__channels = channel_mapping
        self.playlist_data = dict()

    async def extract_data(self, data) -> bool:
        data = "[" + data[5:-2] + "]"
        self.playlist_data = json.loads(data)     # consists of a list of dicts
        return True

    def turn_station_name_into_id(self, station_name :str) -> int:
        station_name = station_name.lower().replace(" ","")
        if station_name in self.__channels:
            return  self.__channels[station_name]
        print("no id could be found")
        return 0

    async def get_socket_data(self, station_id,date:int):
        async with websockets.connect(self.__url) as websocket:
            await websocket.recv()

            # TODO: PUT IN SEPERATE METHOD
            await websocket.send("40")
            response = await websocket.recv()
            if response == "2":
                await websocket.send("3")

            # TODO: PUT IN SEPERATE METHOD
            request_playlist_data = '420["getProgramguide",{"id":' +  f"{station_id}" +', "date": ' + f"{date}" +'}]'
            await websocket.send(request_playlist_data)

            received_data = await websocket.recv()
            while received_data[:3] != "430":
                received_data = await websocket.recv()

            export_data = asyncio.create_task(self.extract_data(received_data))
            await export_data
            return True

    def get_daily_playlists(self, station_id = "41",date=0):
        asyncio.run(self.get_socket_data(station_id,date=date))

    def export_daily_playlist(self, station_id = "41"):
        query = []
        todays_programs = []
        for program in self.playlist_data:
            todays_programs.append(program["name"])
            if "playlist" in program.keys():
                for track in program["playlist"]:
                    name = track['title'].replace("'","")
                    artist = track['artist']
                    query.append(f"{name} {artist}")
        return query
       