from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TrackItem:
    """Represents a single track with a title and description."""

    title: Optional[str]
    description: Optional[str]


@dataclass
class TrackEdge:
    """Wraps a TrackItem as the 'node' of an edge in a paginated list."""

    node: TrackItem


@dataclass
class TrackList:
    """Represents a paginated list of track edges."""

    edges: List[TrackEdge]


@dataclass
class ComponentData:
    """Contains the main list of tracks within a component."""

    tracks: TrackList  # renamed from `paginatedItems` for clarity


@dataclass
class GraphQLResponse:
    """Top-level GraphQL response containing component data."""

    data: ComponentData
