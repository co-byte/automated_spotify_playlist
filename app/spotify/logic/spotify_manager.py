from typing import List

from app.configuration.config import Playlist
from app.logging.logger import get_logger
from app.models.external_track import ExternalTrack
from app.spotify.logic.spotify_manager_config import SpotifyManagerConfig
from app.spotify.requests.models.page.playlist_page import PlaylistsPage


logger = get_logger(__name__)

_PLAYLIST_PAGE_SIZE = 50
_PLAYLIST_PAGE_START_INDEX = 0

class SpotifyManager:
    def __init__(self, config: SpotifyManagerConfig):
        self.__config = config

    # Recursive implementation (although debatable, it looks elegant -and is more fun-)
    async def __playlists_page_contains_managed_playlist(self, limit: int, offset: int) -> (bool):
        try:
            page: PlaylistsPage = await (
                self.__config.playlist_handler.get_current_user_playlists(limit=limit, offset=offset)
                )
            playlists: List[Playlist] = page.items

            if not self.__config.managed_playlist_id:
                logger.debug("No managed playlist ID provided. Assuming playlist does not exist.")
                return False

            # Check if managed_playlist is present in the current page
            for playlist in playlists:
                if playlist.id == self.__config.managed_playlist_id:
                    logger.debug("Existing automated playlist found (ID: %s).", playlist.id)
                    return True

            # Check if all playlists (pages) have been iterated
            if not page.next:
                logger.debug("Final page of playlists reached.")
                return False

            # Fetch the next playlists_page and repeat the process recursively
            # Note: the usage of recursive functions is debatable, but was preferred
            #       in this usecase as it proved to be more elegant (and fun)
            next_limit = limit + _PLAYLIST_PAGE_SIZE
            next_offset = offset + _PLAYLIST_PAGE_SIZE
            return self.__playlists_page_contains_managed_playlist(next_limit, next_offset)

        except ValueError as ve:
            logger.error("Validation error while fetching playlists: %s", str(ve))
            raise ve

        except Exception as e:
            logger.error("Unexpected error fetching playlists: %s", str(e))
            raise e

    async def __automated_playlist_exists(self) -> bool:
        try:
            initial_limit = _PLAYLIST_PAGE_SIZE
            initial_offset = _PLAYLIST_PAGE_START_INDEX
            playlist_exists = await self.__playlists_page_contains_managed_playlist(initial_limit, initial_offset)

            if playlist_exists:
                logger.info("Existing managed playlist found.")
            else:
                logger.info("No existing managed playlist found.")

            return playlist_exists

        except Exception as e:
            logger.error("Error while checking if the automated playlist exists: %s", str(e))
            raise e

    async def __update_playlist_with_tracks(self, tracks: List[ExternalTrack]) -> None:
        # Search for external tracks within Spotify and attempt to retrieve their (Spotify) URIs
        track_uris = await self.__config.search_handler.get_track_uris(tracks)

        self.__config.playlist_handler.update_playlist_items(
            playlist_id=self.__config.managed_playlist_id,
            item_uris=track_uris
        )

    async def update_managed_playlist(self, tracks: List[ExternalTrack]) -> None:
        try:
            if not await self.__automated_playlist_exists():
                logger.info("Managed playlist does not exist. Creating a new playlist.")

                await self.__config.playlist_handler.create_new_playlist(
                    name=self.__config.managed_playlist_name,
                    is_public=self.__config.managed_playlist_is_public,
                    description=self.__config.managed_playlist_description,
                    is_collaborative=self.__config.managed_playlist_is_collaborative
                )

            else:
                logger.info("Managed playlist found. Updating with new tracks.")

            await self.__update_playlist_with_tracks(tracks)

        except Exception as e:
            logger.error("Error updating the managed playlist: %s", str(e))
            raise # Simply propagate the error, it's up to the top caller to decide what should happen
