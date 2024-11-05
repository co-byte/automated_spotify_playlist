import asyncio
from typing import List, Dict, Optional

from app.spotify_service.logging.logger import get_logger
from app.spotify_service.models.external_track import ExternalTrack
from app.spotify_service.repository.api_client.api_client import ApiClient
from app.spotify_service.models.search_response import SearchResponse
from app.spotify_service.models.track.simplified_track import SimplifiedSpotifyTrack
from app.spotify_service.repository.base_handler import SpotifyRequestHandler


logger = get_logger(__name__)


class SearchHandler(SpotifyRequestHandler):
    """Handles Spotify API requests related to searches."""

    __ENDPOINT = "search"

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    # Fetch a SimplifiedSpotifyTrack based on track_name and artist
    async def __search(
        self, query: str, search_type: str, limit: int = 20, offset: int = 0
    ) -> Dict[str, str]:
        params = {"q": query, "type": search_type, "limit": limit, "offset": offset}

        logger.debug(
            "Performing search with query: '%s', type: '%s', limit: %d, offset: %d",
            query,
            search_type,
            limit,
            offset,
        )

        try:
            response = await self._api_client.get(self.__ENDPOINT, params=params)
            logger.debug(
                "Search successful for query: '%s', type: '%s'", query, search_type
            )
            return response
        except Exception as e:
            logger.error(
                "Search failed for query: '%s', type: '%s': %s",
                query,
                search_type,
                str(e),
            )
            raise

    async def _search_track(
        self, track_name: str, artist_name: str, result_limit: int = 1
    ) -> List[SimplifiedSpotifyTrack]:
        query = f"track:{track_name} artist:{artist_name}"
        search_type = "track"

        logger.debug(
            "Initiating track search for track: '%s' by artist: '%s'",
            track_name,
            artist_name,
        )

        try:
            response = await self.__search(
                query=query, search_type=search_type, limit=result_limit
            )
            search_response = SearchResponse.from_dict(response)
            tracks: List[SimplifiedSpotifyTrack] = search_response.tracks.items

            if tracks:
                logger.debug(
                    "Track search successful. Found track: '%s'", tracks[0].name
                )
            else:
                logger.debug("Track search completed, but no tracks were found.")

            return tracks
        except Exception as e:
            logger.error(
                "Track search failed for track: '%s' by artist: '%s': %s",
                track_name,
                artist_name,
                str(e),
            )
            raise

    # Fetch track URIs, based on external tracks
    async def _fetch_uri(self, track: ExternalTrack) -> Optional[str]:
        """
        Retrieves the Spotify track URIs for a list of external tracks.

        Currently, it only supports returning the URI for the first matching track.
        Future improvements may allow returning multiple results for each track.
        """
        result_limit = 1
        selected_track_index = 0

        try:
            logger.debug(
                "Searching for track: '%s' by artist: '%s'",
                track.track_name,
                track.artist,
            )
            found_tracks = await self._search_track(
                track.track_name, track.artist, result_limit=result_limit
            )

            if found_tracks and len(found_tracks) > 0:
                logger.info(
                    "Track found: '%s' by artist: '%s'",
                    found_tracks[0].name,
                    track.artist,
                )
                return found_tracks[selected_track_index].uri
            else:
                logger.warning(
                    "No track found for: '%s' by artist: '%s'",
                    track.track_name,
                    track.artist,
                )
                return None

        except Exception as e:
            logger.error(
                "Failed to fetch URI for track: '%s' by artist: '%s': %s",
                track.track_name,
                track.artist,
                str(e),
            )
            return None

    async def get_track_uris(self, external_tracks: List[ExternalTrack]) -> List[str]:
        uris = []

        try:
            logger.debug(
                "Starting to fetch track URIs for %d external tracks.",
                len(external_tracks),
            )

            # Concurrently search for all tracks to improve performance
            uris = await asyncio.gather(
                *[self._fetch_uri(track) for track in external_tracks]
            )
            logger.debug("Fetched URIs for %d tracks.", len(uris))

        except Exception as e:
            logger.error("An error occurred while fetching track URIs: %s", str(e))
            raise

        # Filter out None values from the list of URIs
        filtered_uris = [uri for uri in uris if uri is not None]

        if len(uris) > len(filtered_uris):
            logger.warning(
                "Unable to retrieve Spotify URIs for %d out of %d provided external tracks.",
                len(uris) - len(filtered_uris),
                len(uris),
            )

        else:
            logger.info(
                "All fetched Spotify URIs are valid. Total count: %d",
                len(filtered_uris),
            )

        return filtered_uris
