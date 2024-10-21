from typing import List
from app.spotify.requests.models.track import Track
from app.spotify.requests.repository.base.request import SpotifyRequestHandler


class TrackRequestHandler(SpotifyRequestHandler):
    """Handles Spotify API requests related to tracks."""

    ENDPOINT = "tracks"

    def __init__(self, api_client):
        super().__init__(api_client, self.ENDPOINT)

    async def get_track(self, track_id: str) -> Track:
        endpoint = f"{self.ENDPOINT}/{track_id}"
        return await self._api_client.get(endpoint)

    async def get_tracks(self, track_ids: List[str]) -> List[Track]:
        url_params = {"ids": ",".join(track_ids)}

        return await self._api_client.get(
            endpoint=self.ENDPOINT,
            params=url_params
        )
