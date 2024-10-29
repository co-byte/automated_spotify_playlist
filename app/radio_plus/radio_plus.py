from typing import Any, Dict, List, Set

import httpx

from app.logging.logger import get_logger
from app.models.external_track import ExternalTrack
from app.radio_plus.models.graphql_response import ComponentData, GraphQLResponse, TrackEdge, TrackItem, TrackList


logger = get_logger(__name__)

# Constants
FETCHED_TRACK_COUNT = 100
VRT_API_URL = "https://www.vrt.be/vrtnu-api/graphql/public/v1"
COMPONENT_ID = "#Y25pLWFsc3BnfG8lOHxzdHVkaW8tYnJ1c3NlbHxwbGF5bGlzdHxiJTF8YiUxJQ=="
HEADERS = {
    "x-vrt-client-name": "WEB"
}
QUERY = """
    query getSongs($componentId: ID!, $lazyItemCount: Int) {
        component(id: $componentId) {
            ... on ContainerNavigationItem {
                components {
                    ... on PaginatedTileList {
                        paginatedItems(first: $lazyItemCount) {
                            edges {
                                node {
                                    ... on SongTile {
                                        title
                                        description
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """

def __fetch_track_data() -> Dict[str, Any]:
    """Send a GraphQL request to the VRT API and return the JSON response."""
    payload = {
        "query": QUERY,
        "variables": {
            "componentId": COMPONENT_ID,
            "lazyItemCount": FETCHED_TRACK_COUNT,
        },
    }

    response = httpx.post(
        url=VRT_API_URL,
        headers=HEADERS,
        json=payload,
        timeout=10
        )
    response.raise_for_status()
    return response.json()

def __parse_tracks(data: Dict[str, Any]) -> Set[ExternalTrack]:
    response = GraphQLResponse(
        data=ComponentData(
            tracks=TrackList(
                edges=[
                    TrackEdge(
                        node=TrackItem(
                            title=edge.get("node", {}).get("title"),
                            description=edge.get("node", {}).get("description")
                        )
                    )
                    for edge
                    in (data
                        .get("data", {})
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
        for edge
        in response.data.tracks.edges
    )

    logger.debug("Succesfully processed the following tracks: %s", tracks)
    return tracks

def ingest_new_tracks() -> Set[ExternalTrack]:
    """Main function to fetch, parse, and log track data."""
    try:
        data = __fetch_track_data()
        tracks = __parse_tracks(data)

        logger.info("Successfully fetched %d unique tracks.", len(tracks))
        return tracks

    except httpx.HTTPStatusError as e:
        logger.error(
            "HTTP error occurred while fetching track data from %s: %s (Status Code: %d)", 
            VRT_API_URL, str(e), e.response.status_code
            )

    except httpx.RequestError as e:
        logger.error(
                "Request error occurred while trying to fetch track data from %s: %s",
                VRT_API_URL, str(e)
            )
