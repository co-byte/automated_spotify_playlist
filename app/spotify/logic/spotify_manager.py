from typing import List

from app.logging.logger import get_logger
from app.models.external_track import ExternalTrack
from app.spotify.logic.spotify_manager_config import SpotifyManagerConfig
from app.spotify.requests.models.page.playlist_page import PlaylistsPage
from app.spotify.requests.models.playlist import Playlist


logger = get_logger(__name__)

_PLAYLIST_PAGE_SIZE = 50

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

            if not self.__config.managed_playlist_id or self.__config.managed_playlist_id == "":
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
            #       here since the number of needed recursive calls is probably zero to one
            # Assumption: users generally have way fewer than 50 playlists
            next_limit = limit + _PLAYLIST_PAGE_SIZE
            next_offset = offset + _PLAYLIST_PAGE_SIZE
            return self.__playlists_page_contains_managed_playlist(next_limit, next_offset)

        except ValueError as ve:
            logger.error("Validation error while fetching playlists: %s", str(ve))
            raise ve

        except Exception as e:
            raise e

    async def __automated_playlist_exists(self) -> bool:
        try:
            initial_limit = _PLAYLIST_PAGE_SIZE
            initial_offset = 0  # Start at index 0
            playlist_exists = await self.__playlists_page_contains_managed_playlist(initial_limit, initial_offset)

            if playlist_exists:
                logger.info("Existing managed playlist found.")
            else:
                logger.warning("No existing managed playlist found.")

            return playlist_exists

        except Exception as e:
            raise e

    async def __update_playlist_with_tracks(self, tracks: List[ExternalTrack]) -> None:
        # Search for external tracks within Spotify and attempt to retrieve their (Spotify) URIs
        track_uris = await self.__config.search_handler.get_track_uris(tracks)

        await self.__config.playlist_handler.update_playlist_items(
            playlist_id=self.__config.managed_playlist_id,
            item_uris=track_uris
        )

    async def update_managed_playlist(self, tracks: List[ExternalTrack]) -> None:
        try:
            if not await self.__automated_playlist_exists():
                logger.info("Managed playlist does not exist. Creating a new playlist.")

                new_playlist = await self.__config.playlist_handler.create_new_playlist(
                    name=self.__config.managed_playlist_name,
                    is_public=self.__config.managed_playlist_is_public,
                    description=self.__config.managed_playlist_description,
                    is_collaborative=self.__config.managed_playlist_is_collaborative
                )

                # Update both local and environment variables
                self.__config.managed_playlist_id = new_playlist.id
                self.__config.managed_playlist_id = new_playlist.id
            else:
                logger.info("Managed playlist found. Updating with new tracks.")

            await self.__update_playlist_with_tracks(tracks)

        except Exception as e:
            raise e
