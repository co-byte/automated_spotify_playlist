import asyncio
import websockets
import json


class RadioPlusAPI(object):
    url = "wss://web-sock.radioplus.be/socket.io/?EIO=4&transport=websocket"
    channel_name_and_id = {
        "radio1": "11",
        "radio2": "22",
        "stubru": "41",
        "klara": "31",
        "stubrudetijdloze": "44",
        "mnm": "55",
        "mnm r&beats": "57",
        "stubruhooray": "140",
        "stubrubruut": "141",
        "stubruuntz": "142"
        }
    playlist_data = None
    todays_programs = None

    @staticmethod
    async def extract_data(data):  
        data = "[" + data[5:-2] + "]"
        RadioPlusAPI.playlist_data = json.loads(data)     # consists of a list of dicts
        return True
    
    @staticmethod
    def turn_station_name_into_id(station_name:str):
        #TODO Create a "handler"-function to check en fix given station names
        station_name = station_name.lower().replace(" ","")
        if station_name in RadioPlusAPI.channel_name_and_id:
            id = RadioPlusAPI.channel_name_and_id[station_name]
            # print(f"{id=}")
            return id
        print("no id could be found")
        return 0

    @staticmethod
    async def get_socket_data(station_id,date:int):
        async with websockets.connect(RadioPlusAPI.url) as websocket:
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

            export_data = asyncio.create_task(RadioPlusAPI.extract_data(received_data))
            await export_data
            return True
    
    @staticmethod
    def get_daily_playlists(station_id = "41",date=0):
        asyncio.run(RadioPlusAPI.get_socket_data(station_id,date=date))

    @staticmethod
    def export_daily_playlist(station_id = "41"):
        query = []
        RadioPlusAPI.todays_programs = []
        for program in RadioPlusAPI.playlist_data:
            RadioPlusAPI.todays_programs.append(program["name"])
            if "playlist" in program.keys():
                for track in program["playlist"]:
                    name = track['title'].replace("'","")
                    artist = track['artist']
                    query.append(f"{name} {track['artist']}")
        return query

       