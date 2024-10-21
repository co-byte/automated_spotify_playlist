from app.spotify.requests.models.search_response import SearchResponse
from app.spotify.requests.models.track.simplified_track import SimplifiedTrack
from app.spotify.requests.models.track.track import Track
from app.spotify.requests.repository.base.request_handler import SpotifyRequestHandler
from typing import List, Optional, Dict


class SearchRequestHandler(SpotifyRequestHandler):
    """Handles Spotify API requests related to searches."""

    __ENDPOINT = "search"

    def __init__(self, api_client):
        """Initialize the search handler with an API client."""
        super().__init__(api_client, self.__ENDPOINT)

    async def __search(self, query: str, search_type: str, limit: int = 20, offset: int = 0) -> Dict[str, str]:
        params = {
            'q': query,
            'type': search_type,
            'limit': limit,
            'offset': offset
        }
        return await self._api_client.get(self.__ENDPOINT, params=params)

    async def search_track(self, track_name: str, artist_name: str) -> List[SimplifiedTrack]:
        # Construct the search query
        query = f'track:{track_name} artist:{artist_name}'
        search_type = "track"
        result_limit = 1

        response = await self.__search(query=query, search_type=search_type, limit=result_limit)
        search_response = SearchResponse.from_dict(response)
        tracks: List[SimplifiedTrack] = search_response.tracks.items

        return tracks
