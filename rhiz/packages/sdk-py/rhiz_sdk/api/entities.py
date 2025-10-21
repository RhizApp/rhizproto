"""
Entities API operations
"""

from typing import Any, Optional

import httpx


class EntitiesAPI:
    """Entities API client"""

    def __init__(self, client: httpx.Client):
        self._client = client

    def create(
        self,
        id: str,
        type: str,
        name: str,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None,
        did: Optional[str] = None,
        handle: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Create a new entity

        Args:
            id: Entity ID
            type: Entity type (person, organization, agent)
            name: Entity name
            bio: Optional bio
            avatar_url: Optional avatar URL
            did: Optional AT Protocol DID
            handle: Optional AT Protocol handle

        Returns:
            Created entity
        """
        payload = {"id": id, "type": type, "name": name}

        if bio:
            payload["bio"] = bio
        if avatar_url:
            payload["avatar_url"] = avatar_url
        if did:
            payload["did"] = did
        if handle:
            payload["handle"] = handle

        response = self._client.post("/entities/", json=payload)
        response.raise_for_status()
        return response.json()

    def get(self, entity_id: str) -> dict[str, Any]:
        """
        Get an entity by ID

        Args:
            entity_id: Entity ID

        Returns:
            Entity data
        """
        response = self._client.get(f"/entities/{entity_id}")
        response.raise_for_status()
        return response.json()

    def update(
        self,
        entity_id: str,
        name: Optional[str] = None,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None,
        handle: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Update an entity

        Args:
            entity_id: Entity ID
            name: Optional new name
            bio: Optional new bio
            avatar_url: Optional new avatar URL
            handle: Optional new handle

        Returns:
            Updated entity
        """
        payload = {}
        if name:
            payload["name"] = name
        if bio:
            payload["bio"] = bio
        if avatar_url:
            payload["avatar_url"] = avatar_url
        if handle:
            payload["handle"] = handle

        response = self._client.patch(f"/entities/{entity_id}", json=payload)
        response.raise_for_status()
        return response.json()

    def delete(self, entity_id: str) -> None:
        """
        Delete an entity

        Args:
            entity_id: Entity ID
        """
        response = self._client.delete(f"/entities/{entity_id}")
        response.raise_for_status()

