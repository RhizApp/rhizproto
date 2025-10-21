"""
Analytics API operations
"""

from typing import Any

import httpx


class AnalyticsAPI:
    """Analytics API client"""

    def __init__(self, client: httpx.Client):
        self._client = client

    def get_trust_health(self, entity_id: str) -> dict[str, Any]:
        """
        Get trust health metrics for an entity

        Args:
            entity_id: Entity ID

        Returns:
            Trust health response
        """
        response = self._client.get(f"/analytics/trust-health/{entity_id}")
        response.raise_for_status()
        return response.json()

    def get_trust_metrics(self, entity_id: str) -> dict[str, Any]:
        """
        Get detailed trust metrics for an entity

        Args:
            entity_id: Entity ID

        Returns:
            Trust metrics response
        """
        response = self._client.get(f"/analytics/trust-metrics/{entity_id}")
        response.raise_for_status()
        return response.json()

    def get_network_stats(self) -> dict[str, Any]:
        """
        Get overall network statistics

        Returns:
            Network stats response
        """
        response = self._client.get("/analytics/network-stats")
        response.raise_for_status()
        return response.json()

