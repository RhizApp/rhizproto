"""
Graph pathfinding service
Advanced pathfinding with A* algorithm, trust heuristics, and path diversity
"""

import heapq
import math
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.relationship import Relationship
from app.schemas.graph import GraphHop, GraphPathResponse
from app.services.cache_service import cache_service


class PathFinder:
    """Advanced graph pathfinding with A*, trust heuristics, and path diversity"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._graph_cache: Dict[str, Dict] = {}

    async def find_path(
        self,
        from_entity: str,
        to_entity: str,
        max_hops: int = 6,
        min_strength: float = 0.5,
        relationship_types: list[str] | None = None,
        exclude_entities: list[str] | None = None,
        algorithm: str = "astar",
    ) -> GraphPathResponse | None:
        """
        Find optimal trust-weighted path between entities with caching
        
        Args:
            algorithm: "astar" (default), "bfs", or "dijkstra"
        """
        # Handle direct connection
        if from_entity == to_entity:
            return None

        # Prepare query parameters for caching
        query_params = {
            "max_hops": max_hops,
            "min_strength": min_strength,
            "relationship_types": relationship_types or [],
            "exclude_entities": exclude_entities or [],
            "algorithm": algorithm
        }

        # Check cache first
        cached_result = await cache_service.get_cached_path(
            from_entity, to_entity, query_params
        )
        if cached_result:
            # Convert cached result back to GraphPathResponse
            return self._dict_to_graph_path_response(cached_result)

        # Build graph from database
        graph = await self._build_enhanced_graph(min_strength, relationship_types)

        # Choose pathfinding algorithm
        if algorithm == "astar":
            path = await self._astar_path(
                graph, from_entity, to_entity, max_hops, exclude_entities or []
            )
        elif algorithm == "dijkstra":
            path = await self._dijkstra_path(
                graph, from_entity, to_entity, max_hops, exclude_entities or []
            )
        else:  # Default to BFS for backwards compatibility
            path = self._bfs_path(
                graph, from_entity, to_entity, max_hops, exclude_entities or []
            )

        if not path:
            return None

        # Convert path to response format with enhanced strength calculation
        result = await self._path_to_response_enhanced(path, from_entity, to_entity)

        # Cache the result
        await cache_service.cache_path_result(
            from_entity, to_entity, self._graph_path_response_to_dict(result), query_params
        )

        return result

    async def _astar_path(
        self,
        graph: Dict[str, List[Dict]],
        start: str,
        end: str,
        max_hops: int,
        exclude: List[str],
    ) -> List[Dict[str, Any]] | None:
        """
        A* pathfinding with trust-based heuristics
        
        Uses trust scores as both edge weights and heuristic estimates
        """
        if start not in graph or end not in graph:
            return None

        # Priority queue: (f_score, g_score, current_node, path)
        open_set = [(0, 0, start, [])]
        closed_set: Set[str] = set()
        
        # Track best g_score for each node
        g_scores: Dict[str, float] = {start: 0}

        while open_set:
            f_score, g_score, current, path = heapq.heappop(open_set)

            if current in closed_set:
                continue
                
            closed_set.add(current)

            # Check hop limit
            if len(path) >= max_hops:
                continue

            # Found target
            if current == end:
                return path

            # Explore neighbors
            for neighbor_info in graph.get(current, []):
                neighbor = neighbor_info["to"]

                # Skip excluded entities and already processed
                if neighbor in exclude or neighbor in closed_set:
                    continue

                # Calculate actual cost (g_score)
                edge_cost = self._calculate_edge_cost(neighbor_info)
                tentative_g = g_score + edge_cost

                # Skip if we found a better path to this neighbor
                if neighbor in g_scores and tentative_g >= g_scores[neighbor]:
                    continue

                g_scores[neighbor] = tentative_g

                # Calculate heuristic (h_score) - estimate remaining cost
                h_score = await self._trust_heuristic(neighbor, end, graph)
                f_score = tentative_g + h_score

                new_path = path + [neighbor_info]
                heapq.heappush(open_set, (f_score, tentative_g, neighbor, new_path))

        return None

    async def _dijkstra_path(
        self,
        graph: Dict[str, List[Dict]],
        start: str,
        end: str,
        max_hops: int,
        exclude: List[str],
    ) -> List[Dict[str, Any]] | None:
        """Dijkstra's algorithm for trust-weighted shortest path"""
        if start not in graph:
            return None

        # Priority queue: (cost, current_node, path)
        pq = [(0, start, [])]
        visited: Set[str] = set()
        distances: Dict[str, float] = {start: 0}

        while pq:
            current_cost, current, path = heapq.heappop(pq)

            if current in visited:
                continue
                
            visited.add(current)

            # Check hop limit
            if len(path) >= max_hops:
                continue

            # Found target
            if current == end:
                return path

            # Explore neighbors
            for neighbor_info in graph.get(current, []):
                neighbor = neighbor_info["to"]

                if neighbor in exclude or neighbor in visited:
                    continue

                edge_cost = self._calculate_edge_cost(neighbor_info)
                new_cost = current_cost + edge_cost

                if neighbor not in distances or new_cost < distances[neighbor]:
                    distances[neighbor] = new_cost
                    new_path = path + [neighbor_info]
                    heapq.heappush(pq, (new_cost, neighbor, new_path))

        return None

    def _calculate_edge_cost(self, edge_info: Dict[str, Any]) -> float:
        """
        Calculate edge traversal cost (lower is better)
        
        Cost is inverse of trust - high trust = low cost
        """
        trust_score = edge_info.get("trust_score", 0.5)
        verification_score = edge_info.get("verification_score", 0.5)
        
        # Combined trust with verification bonus
        combined_trust = min(1.0, trust_score + 0.1 * verification_score)
        
        # Convert to cost (invert and scale)
        cost = (1.0 - combined_trust) * 10
        return max(0.1, cost)  # Minimum cost to avoid zero costs

    async def _trust_heuristic(
        self, 
        current: str, 
        target: str, 
        graph: Dict[str, List[Dict]]
    ) -> float:
        """
        Heuristic function for A* - estimates remaining cost to target
        
        Uses network distance and average trust scores as estimate
        """
        if current == target:
            return 0

        # Simple heuristic: assume remaining path will have average trust
        # In a full implementation, could use more sophisticated estimates
        
        # Calculate average trust score in local neighborhood
        neighbors = graph.get(current, [])
        if not neighbors:
            return 5.0  # High cost estimate if isolated
            
        avg_trust = sum(n.get("trust_score", 0.5) for n in neighbors) / len(neighbors)
        
        # Estimate remaining hops (simplified)
        # In practice, could use precomputed distances or embeddings
        estimated_hops = 2.0
        
        # Convert average trust to cost and multiply by estimated distance
        avg_cost = (1.0 - avg_trust) * 10
        return avg_cost * estimated_hops

    async def _build_enhanced_graph(
        self, min_strength: float, relationship_types: list[str] | None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Build enhanced adjacency list with trust scores and verification data"""
        # Query relationships with higher minimum threshold for pathfinding
        adjusted_min_strength = max(min_strength * 100, 30)  # Convert to 0-100 scale
        
        query = select(Relationship).where(Relationship.strength >= adjusted_min_strength)

        if relationship_types:
            query = query.where(Relationship.type.in_(relationship_types))

        result = await self.db.execute(query)
        relationships = result.scalars().all()

        # Build adjacency list (undirected graph) with enhanced metadata
        graph: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        for rel in relationships:
            # Calculate trust score with temporal decay
            trust_score = self._calculate_relationship_trust(rel)
            
            # Enhanced edge data for both directions
            edge_data = {
                "to": None,  # Will be set per direction
                "relationship_id": rel.id,
                "strength": rel.strength,
                "trust_score": trust_score,
                "verification_score": rel.consensus_score,
                "verifier_count": rel.verifier_count,
                "relationship_type": rel.type.value if hasattr(rel.type, 'value') else str(rel.type),
                "last_interaction": rel.last_interaction,
            }

            # Add both directions
            edge_a_to_b = edge_data.copy()
            edge_a_to_b["to"] = rel.entity_b_id
            graph[rel.entity_a_id].append(edge_a_to_b)

            edge_b_to_a = edge_data.copy()
            edge_b_to_a["to"] = rel.entity_a_id
            graph[rel.entity_b_id].append(edge_b_to_a)

        return dict(graph)

    def _calculate_relationship_trust(self, relationship: Relationship) -> float:
        """Calculate trust score for a relationship with temporal decay"""
        base_strength = relationship.strength / 100.0  # Convert to 0-1 scale
        
        # Apply temporal decay if last_interaction exists
        if relationship.last_interaction:
            from datetime import datetime, timedelta
            days_since = (datetime.utcnow() - relationship.last_interaction).days
            decay_factor = math.exp(-days_since / 365.25)  # 1-year half-life
            base_strength = max(0.1 * base_strength, base_strength * decay_factor)
        
        # Verification boost
        verification_boost = min(0.2, relationship.verifier_count / 50)
        
        return min(1.0, base_strength + verification_boost)

    async def _path_to_response_enhanced(
        self, path: List[Dict[str, Any]], from_entity: str, to_entity: str
    ) -> GraphPathResponse:
        """Convert path to GraphPathResponse with enhanced strength calculation"""
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

        # Calculate total strength using weighted harmonic mean (better for trust chains)
        trust_scores = [edge.get("trust_score", edge["strength"] / 100.0) for edge in path]
        total_strength = self._calculate_path_trust_strength(trust_scores)

        return GraphPathResponse(
            from_entity=from_entity,
            to_entity=to_entity,
            hops=hops,
            total_strength=total_strength,
            distance=len(hops),
        )

    def _calculate_path_trust_strength(self, trust_scores: List[float]) -> float:
        """
        Calculate path strength using weighted harmonic mean
        
        Harmonic mean is more conservative and better represents 
        the "weakest link" nature of trust chains
        """
        if not trust_scores:
            return 0.0
            
        # Filter out zero scores to avoid division by zero
        valid_scores = [s for s in trust_scores if s > 0]
        if not valid_scores:
            return 0.0
            
        n = len(valid_scores)
        harmonic_mean = n / sum(1/s for s in valid_scores)
        
        # Apply path length penalty (longer paths are less trustworthy)
        length_penalty = 0.9 ** (len(trust_scores) - 1)
        
        return min(1.0, harmonic_mean * length_penalty)

    def _graph_path_response_to_dict(self, response: GraphPathResponse) -> Dict[str, Any]:
        """Convert GraphPathResponse to dictionary for caching"""
        return {
            "from_entity": response.from_entity,
            "to_entity": response.to_entity,
            "hops": [
                {
                    "from_entity": hop.from_entity,
                    "to_entity": hop.to_entity,
                    "relationship_id": hop.relationship_id,
                    "strength": hop.strength
                }
                for hop in response.hops
            ],
            "total_strength": response.total_strength,
            "distance": response.distance
        }

    def _dict_to_graph_path_response(self, data: Dict[str, Any]) -> GraphPathResponse:
        """Convert dictionary to GraphPathResponse"""
        hops = [
            GraphHop(
                from_entity=hop["from_entity"],
                to_entity=hop["to_entity"],
                relationship_id=hop["relationship_id"],
                strength=hop["strength"]
            )
            for hop in data["hops"]
        ]
        
        return GraphPathResponse(
            from_entity=data["from_entity"],
            to_entity=data["to_entity"],
            hops=hops,
            total_strength=data["total_strength"],
            distance=data["distance"]
        )

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
        """Get direct neighbors of an entity with caching"""
        query_params = {"min_strength": min_strength}
        
        # Check cache first
        cached_neighbors = await cache_service.get_cached_neighbors(entity_id, query_params)
        if cached_neighbors:
            return cached_neighbors

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
                    "type": rel.type.value if hasattr(rel.type, 'value') else str(rel.type),
                }
            )

        # Cache the results
        await cache_service.cache_neighbors(entity_id, neighbors, query_params)

        return neighbors

