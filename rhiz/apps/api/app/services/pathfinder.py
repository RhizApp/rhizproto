"""
Graph pathfinding service
Finds trust-weighted paths between entities
"""

from collections import defaultdict, deque
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.relationship import Relationship
from app.schemas.graph import GraphHop, GraphPathResponse


class PathFinder:
    """Graph pathfinding using BFS with trust weighting"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_path(
        self,
        from_entity: str,
        to_entity: str,
        max_hops: int = 6,
        min_strength: float = 0.5,
        relationship_types: list[str] | None = None,
        exclude_entities: list[str] | None = None,
    ) -> GraphPathResponse | None:
        """Find shortest trust-weighted path between two entities"""

        # Handle direct connection
        if from_entity == to_entity:
            return None

        # Build graph from database
        graph = await self._build_graph(min_strength, relationship_types)

        # BFS to find path
        path = self._bfs_path(
            graph, from_entity, to_entity, max_hops, exclude_entities or []
        )

        if not path:
            return None

        # Convert path to response format
        return await self._path_to_response(path, from_entity, to_entity)

    async def _build_graph(
        self, min_strength: float, relationship_types: list[str] | None
    ) -> dict[str, list[dict[str, Any]]]:
        """Build adjacency list from database"""
        # Query relationships
        query = select(Relationship).where(Relationship.strength >= min_strength)

        if relationship_types:
            query = query.where(Relationship.type.in_(relationship_types))

        result = await self.db.execute(query)
        relationships = result.scalars().all()

        # Build adjacency list (undirected graph)
        graph: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for rel in relationships:
            # Add both directions
            graph[rel.entity_a_id].append(
                {
                    "to": rel.entity_b_id,
                    "relationship_id": rel.id,
                    "strength": rel.strength,
                }
            )
            graph[rel.entity_b_id].append(
                {
                    "to": rel.entity_a_id,
                    "relationship_id": rel.id,
                    "strength": rel.strength,
                }
            )

        return dict(graph)

    def _bfs_path(
        self,
        graph: dict[str, list[dict[str, Any]]],
        start: str,
        end: str,
        max_hops: int,
        exclude: list[str],
    ) -> list[dict[str, Any]] | None:
        """BFS to find path, respecting max hops and exclusions"""
        if start not in graph or end not in graph:
            return None

        # BFS with path tracking
        queue: deque = deque([(start, [])])
        visited = {start}

        while queue:
            current, path = queue.popleft()

            # Check hop limit
            if len(path) >= max_hops:
                continue

            # Check neighbors
            for neighbor_info in graph.get(current, []):
                neighbor = neighbor_info["to"]

                # Skip excluded entities
                if neighbor in exclude:
                    continue

                # Found target
                if neighbor == end:
                    return path + [neighbor_info]

                # Continue search
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor_info]))

        return None

    async def _path_to_response(
        self, path: list[dict[str, Any]], from_entity: str, to_entity: str
    ) -> GraphPathResponse:
        """Convert path to GraphPathResponse"""
        hops = []
        current = from_entity

        for edge in path:
            hops.append(
                GraphHop(
                    from_entity=current,
                    to_entity=edge["to"],
                    relationship_id=edge["relationship_id"],
                    strength=edge["strength"],
                )
            )
            current = edge["to"]

        # Calculate total strength (geometric mean)
        strengths = [h.strength for h in hops]
        total_strength = (
            (sum(strengths) / len(strengths)) if strengths else 0.0
        )  # Simplified for speed

        return GraphPathResponse(
            from_entity=from_entity,
            to_entity=to_entity,
            hops=hops,
            total_strength=total_strength,
            distance=len(hops),
        )

    async def get_neighbors(
        self, entity_id: str, min_strength: float = 0.0
    ) -> list[dict[str, Any]]:
        """Get direct neighbors of an entity"""
        query = select(Relationship).where(
            or_(
                Relationship.entity_a_id == entity_id,
                Relationship.entity_b_id == entity_id,
            ),
            Relationship.strength >= min_strength,
        )

        result = await self.db.execute(query)
        relationships = result.scalars().all()

        neighbors = []
        for rel in relationships:
            neighbor_id = (
                rel.entity_b_id if rel.entity_a_id == entity_id else rel.entity_a_id
            )
            neighbors.append(
                {
                    "entity_id": neighbor_id,
                    "relationship_id": rel.id,
                    "strength": rel.strength,
                    "type": rel.type.value,
                }
            )

        return neighbors

