from typing import Any, Dict, Set

import httpx

from app.logging.logger import get_logger
from app.models.external_track import ExternalTrack
from app.vrtmax.models.graphql_response import ComponentData, GraphQLResponse, TrackEdge, TrackItem, TrackList
from app.vrtmax.vrtmax_client_config import VRTMaxClientConfig


logger = get_logger(__name__)

class VRTMaxClient:
    def __init__(self, config: VRTMaxClientConfig):
        self.__api_url = config.api_url
        self.__component_id = config.component_id
        self.__fetched_track_count = config.fetched_track_count
        self.__headers = config.headers
        self.__query = config.query

    def __fetch_track_data(self) -> Dict[str, Any]:
        """Send a GraphQL request to the VRT API and return the JSON response."""
        payload = {
            "query": self.__query,
            "variables": {
                "componentId": self.__component_id,
                "lazyItemCount": self.__fetched_track_count
            },
        }

        response = httpx.post(url=self.__api_url, headers=self.__headers, json=payload, timeout=10)
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

        logger.debug("Succesfully processed the following tracks: %s", tracks)
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
                self.__api_url,
                str(e),
                e.response.status_code,
            )

        except httpx.RequestError as e:
            logger.error(
                "Request error occurred while trying to fetch track data from %s: %s",
                self.__api_url,
                str(e),
            )