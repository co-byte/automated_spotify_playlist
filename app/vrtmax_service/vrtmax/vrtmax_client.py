from typing import Any, Dict, Set

import httpx

from app.vrtmax_service.logging.logger import get_logger
from app.vrtmax_service.models.external_track import ExternalTrack
from app.vrtmax_service.config.vrtmax_client_config import VRTMaxClientConfig
from app.vrtmax_service.models.graphql_response import (
    ComponentData,
    GraphQLResponse,
    TrackEdge,
    TrackItem,
    TrackList,
)


logger = get_logger(__name__)


class VRTMaxClientError(Exception):
    """Custom exception for handling VRTMaxClient failures."""


class VRTMaxClient:
    def __init__(self, config: VRTMaxClientConfig):
        self.__config = config

    def __fetch_track_data(self) -> Dict[str, Any]:
        """Send a GraphQL request to the VRT API and return the JSON response."""
        payload = {
            "query": self.__config.query,
            "variables": {
                "componentId": self.__config.component_id,
                "lazyItemCount": self.__config.fetched_track_count
            },
        }

        response = httpx.post(
            url=self.__config.api_url,
            headers=self.__config.headers,
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def __parse_tracks(data: Dict[str, Any]) -> Set[ExternalTrack]:
        response = GraphQLResponse(
            data=ComponentData(
                tracks=TrackList(
                    edges=[
                        TrackEdge(
                            node=TrackItem(
                                title=edge.get("node", {}).get("title"),
                                description=edge.get("node", {}).get("description"),
                            )
                        )
                        for edge in (
                            data.get("data", {})
                            .get("component", {})
                            .get("components", [])[0]
                            .get("paginatedItems", {})
                            .get("edges", [])
                        )
                    ]
                )
            )
        )

        tracks = set(
            ExternalTrack(edge.node.title, edge.node.description)
            for edge in response.data.tracks.edges
        )

        # Log the first 5 tracks completely and display the remaining track count
        display_tracks = list(tracks)[:5]
        tracks_json = "\n".join(str(track) for track in display_tracks)
        logger.debug(
            "Successfully processed the following tracks:\n%s\n%s",
            tracks_json,
            f"and {len(tracks) - 5} more" if len(tracks) > 5 else "",
        )

        return tracks

    def ingest_new_tracks(self) -> Set[ExternalTrack]:
        """Main function to fetch, parse, and log track data."""
        try:
            data = self.__fetch_track_data()
            tracks = self.__parse_tracks(data)

            logger.info("Successfully fetched %d unique tracks.", len(tracks))
            return tracks

        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error occurred while fetching track data from %s: %s (Status Code: %d)",
                self.__config.api_url,
                str(e),
                e.response.status_code,
            )
            raise VRTMaxClientError("Unable to ingest new tracks.") from e

        except httpx.RequestError as e:
            logger.error(
                "Request error occurred while trying to fetch track data from %s: %s",
                self.__config.api_url,
                str(e),
            )
            raise VRTMaxClientError("Unable to ingest new tracks.") from e
