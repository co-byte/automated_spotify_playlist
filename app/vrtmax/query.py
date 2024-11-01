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
