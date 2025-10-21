"""
Graph API operations
"""

from typing import Any, Optional

import httpx


class GraphAPI:
    """Graph API client"""

    def __init__(self, client: httpx.Client):
        self._client = client

    def find_path(
        self,
        from_entity: str,
        to_entity: str,
        max_hops: int = 6,
        min_strength: float = 0.5,
        relationship_types: Optional[list[str]] = None,
        exclude_entities: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Find shortest path between two entities

        Args:
            from_entity: Source entity ID
            to_entity: Target entity ID
            max_hops: Maximum number of hops (default: 6)
            min_strength: Minimum relationship strength (default: 0.5)
            relationship_types: Filter by relationship types
            exclude_entities: Entities to exclude from path

        Returns:
            Graph path response
        """
        payload = {
            "from": from_entity,
            "to": to_entity,
            "max_hops": max_hops,
            "min_strength": min_strength,
        }

        if relationship_types:
            payload["relationship_types"] = relationship_types
        if exclude_entities:
            payload["exclude_entities"] = exclude_entities

        response = self._client.post("/graph/find-path", json=payload)
        response.raise_for_status()
        return response.json()

    def get_neighbors(
        self, entity_id: str, min_strength: float = 0.0
    ) -> dict[str, Any]:
        """
        Get direct neighbors of an entity

        Args:
            entity_id: Entity ID
            min_strength: Minimum relationship strength (default: 0.0)

        Returns:
            Neighbors response
        """
        response = self._client.get(
            f"/graph/neighbors/{entity_id}",
            params={"min_strength": min_strength},
        )
        response.raise_for_status()
        return response.json()

