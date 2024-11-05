from typing import Dict, List

from app.spotify_service.logging.logger import get_logger
from app.spotify_service.repository.api_client.api_client import ApiClient
from app.spotify_service.models.track.track import SpotifyTrack
from app.spotify_service.repository.base_handler import SpotifyRequestHandler


logger = get_logger(__name__)


class TrackHandler(SpotifyRequestHandler):
    """Handles Spotify API requests related to tracks."""

    __ENDPOINT = "tracks"

    def __init__(self, api_client: ApiClient):
        super().__init__(api_client)

    async def get_track(self, track_id: str) -> SpotifyTrack:
        endpoint = f"{self.__ENDPOINT}/{track_id}"

        logger.debug("Fetching track data from endpoint: %s", endpoint)

        try:
            track_data = await self._api_client.get(endpoint)
            track = SpotifyTrack.from_dict(track_data)
            logger.info("Sucessfully retrieved track data for ID %s.", track_id)
            return track
        except Exception as e:
            logger.error("Failed to retrieve track with ID %s: %s", track_id, str(e))
            raise

    async def get_tracks(self, track_ids: List[str]) -> List[SpotifyTrack]:
        response_object_key = "tracks"
        url_params = {"ids": ",".join(track_ids)}  # Comma-separated IDs

        logger.debug(
            "Preparing to fetch tracks from endpoint: %s with parameters: %s",
            self.__ENDPOINT,
            url_params,
        )

        try:
            response: Dict[str, List[Dict[str, str]]] = await self._api_client.get(
                endpoint=self.__ENDPOINT, params=url_params
            )
            track_data = response[response_object_key]

            logger.info(
                "Successfully retrieved (%d/%d) tracks from IDs.",
                len(track_data),
                len(track_ids),
            )
            return [SpotifyTrack.from_dict(track) for track in track_data]
        except Exception as e:
            logger.error(
                "Failed to retrieve tracks with IDs %s: %s",
                ", ".join(track_ids),
                str(e),
            )
            raise
