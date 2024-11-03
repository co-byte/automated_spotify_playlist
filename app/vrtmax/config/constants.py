"""
Defines constants and GraphQL query for the VRTMax client configuration to keep settings separated
from client logic while avoiding the overhead of YAML (or other file format) parsing.
"""

API_URL = "https://www.vrt.be/vrtnu-api/graphql/public/v1"
COMPONENT_ID = "#Y25pLWFsc3BnfG8lOHxzdHVkaW8tYnJ1c3NlbHxwbGF5bGlzdHxiJTF8YiUxJQ=="
FETCHED_TRACK_COUNT = 100
HEADERS = {"x-vrt-client-name": "WEB"}

GET_SONGS_AND_ARTISTS_QUERY = """
query getSongsAndArtists($componentId: ID!, $lazyItemCount: Int!) {
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
