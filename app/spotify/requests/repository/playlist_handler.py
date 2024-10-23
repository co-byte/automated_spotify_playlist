from typing import List

from app.spotify.requests.repository.api_client.api_client import ApiClient
from app.spotify.requests.models.page.playlist_page import PlaylistsPage
from app.spotify.requests.models.playlist import Playlist
from app.spotify.requests.repository.base_handler import SpotifyRequestHandler
from app.logging.logger import get_logger


logger = get_logger(__name__)

class PlaylistHandler(SpotifyRequestHandler):
    """Handles Spotify API requests related to playlists."""

    __CURRENT_USER_PLAYLISTS = "me/playlists"

    def __init__(self, api_client: ApiClient, user_id: str) -> None:
        super().__init__(api_client)
        self.__user_id = user_id

    def __validate_pagination_params(self, limit: int, offset: int) -> None:
        if not (1 <= limit <= 50):
            logger.error("Invalid limit value: %d. Must be between 1 and 50.", limit)
            raise ValueError("Limit must be between 1 and 50.")

        if not (0 <= offset <= 100000):
            logger.error("Invalid offset value: %d. Must be between 1 and 100000.", offset)
            raise ValueError("Offset must be between 1 and 100000.")

    async def get_current_user_playlists(self, limit: int, offset: int) -> PlaylistsPage:
        """
        Fetches the current user's playlists with pagination.
        Ensure limit is [1,50] and offset is [1,100000].
        """
        logger.debug(
            "Fetching playlists for user: %s with limit: %d, offset: %d", 
            self.__user_id, limit, offset
            )

        self.__validate_pagination_params(limit, offset)

        endpoint = self.__CURRENT_USER_PLAYLISTS
        params = {
            'limit': limit,
            'offset': offset
            }

        try:
            playlist_page_data = await self._api_client.get(endpoint, params=params)
            playlist_page = PlaylistsPage.from_dict(playlist_page_data)

            logger.info("Successfully fetched (%d) user playlists", len(playlist_page.items))
            return playlist_page

        except Exception as e:
            logger.error("Failed to fetch playlists for user %s: %s", self.__user_id, str(e))
            raise e

    async def create_new_playlist(
        self,
        name: str,
        is_public: bool,
        description: str,
        is_collaborative: bool
        ) -> Playlist:
        """Creates a new playlist for the current user."""

        logger.debug(
            "Creating new playlist for user: %s with name: '%s', public: %s, collaborative: %s", 
            self.__user_id, name, is_public, is_collaborative
            )

        endpoint = f"users/{self.__user_id}/playlists"
        body = {
            'name': name,
            'public': is_public,
            'collaborative': is_collaborative,
            'description': description
            }

        try:
            playlist_data = await self._api_client.post(endpoint, json_body=body)
            playlist = Playlist.from_dict(playlist_data)

            logger.info("Successfully created playlist '%s' for user %s.", name, self.__user_id)
            return playlist

        except Exception as e:
            logger.error("Failed to create playlist for user %s: %s", self.__user_id, str(e))
            raise

    async def update_playlist_items(
        self,
        playlist_id: str,
        item_uris: List[str]
        ) -> str:
        """Update a playlist by reordening or replacing tracks. Returns the snapshot id."""

        logger.debug("Updating playlist %s with (%d) items.", playlist_id, len(item_uris))

        endpoint = f"playlists/{playlist_id}/tracks"
        body = {
            "uris": item_uris
            }

        try:
            new_snapshot = await self._api_client.put(endpoint, json_body=body)
            logger.info(
                "Successfully updated playlist %s. New snapshot ID: %s", 
                playlist_id, new_snapshot
                )
            return new_snapshot

        except Exception as e:
            logger.error("Failed to update playlist %s: %s", playlist_id, str(e))
            raise
