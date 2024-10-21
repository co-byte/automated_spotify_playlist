from typing import List, Dict

from app.spotify.requests.repository.api_client.api_client import ApiClient
from app.spotify.requests.models.search_response import SearchResponse
from app.spotify.requests.models.track.simplified_track import SimplifiedTrack
from app.spotify.requests.repository.base_handler import SpotifyRequestHandler
from app.logging.logger import get_logger


logger = get_logger(__name__)

class SearchHandler(SpotifyRequestHandler):
    """Handles Spotify API requests related to searches."""

    __ENDPOINT = "search"

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def __search(self, query: str, search_type: str, limit: int = 20, offset: int = 0) -> Dict[str, str]:
        params = {
            'q': query,
            'type': search_type,
            'limit': limit,
            'offset': offset
        }

        logger.debug("Performing search with query: '%s', type: '%s', limit: %d, offset: %d", query, search_type, limit, offset)

        try:
            response = await self._api_client.get(self.__ENDPOINT, params=params)
            logger.debug("Search successful for query: '%s', type: '%s'", query, search_type)
            return response
        except Exception as e:
            logger.error("Search failed for query: '%s', type: '%s': %s", query, search_type, str(e))
            raise

    async def search_track(self, track_name: str, artist_name: str) -> List[SimplifiedTrack]:
        query = f'track:{track_name} artist:{artist_name}'
        search_type = "track"
        result_limit = 1

        logger.debug(
            "Initiating track search for track: '%s' by artist: '%s'", 
            track_name, artist_name
            )

        try:
            response = await self.__search(query=query, search_type=search_type, limit=result_limit)
            search_response = SearchResponse.from_dict(response)
            tracks: List[SimplifiedTrack] = search_response.tracks.items

            if tracks:
                logger.info("Track search successful. Found track: '%s'", tracks[0].name)
            else:
                logger.info("Track search completed, but no tracks were found.")

            return tracks
        except Exception as e:
            logger.error(
                "Track search failed for track: '%s' by artist: '%s': %s", 
                track_name, artist_name, str(e)
                )
            raise
