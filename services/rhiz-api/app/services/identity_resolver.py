"""
AT Protocol Identity Resolution for Rhiz API
Resolves DIDs and handles to full identity information
"""

import httpx
from typing import Optional, Dict, Any
from functools import lru_cache


class ResolvedIdentity:
    """Resolved identity information"""

    def __init__(
        self,
        did: str,
        handle: Optional[str] = None,
        pds: Optional[str] = None,
        signing_key: Optional[str] = None,
    ):
        self.did = did
        self.handle = handle
        self.pds = pds
        self.signing_key = signing_key


class RhizIdentityResolver:
    """
    Identity resolver for Rhiz Protocol entities
    Resolves DIDs and handles to full identity information
    """

    def __init__(self, pds_url: str = "https://bsky.social"):
        self.pds_url = pds_url
        self.client = httpx.AsyncClient(timeout=10.0)

    async def resolve(self, did_or_handle: str) -> ResolvedIdentity:
        """
        Resolve a DID or handle to full identity information

        Args:
            did_or_handle: DID (did:plc:...) or handle (alice.bsky.social)

        Returns:
            ResolvedIdentity with DID, handle, PDS, and signing key

        Raises:
            ValueError: If resolution fails
        """
        if did_or_handle.startswith("did:"):
            return await self._resolve_did(did_or_handle)
        else:
            return await self._resolve_handle(did_or_handle)

    async def _resolve_handle(self, handle: str) -> ResolvedIdentity:
        """Resolve a handle to DID, then get full identity"""
        try:
            # Call AT Protocol handle resolution
            response = await self.client.get(
                f"{self.pds_url}/xrpc/com.atproto.identity.resolveHandle",
                params={"handle": handle},
            )
            response.raise_for_status()
            data = response.json()
            did = data.get("did")

            if not did:
                raise ValueError(f"Could not resolve handle: {handle}")

            # Now resolve the DID for full info
            return await self._resolve_did(did)

        except httpx.HTTPError as e:
            raise ValueError(f"Failed to resolve handle {handle}: {e}")

    async def _resolve_did(self, did: str) -> ResolvedIdentity:
        """Resolve a DID to full identity information"""
        try:
            # Get DID document
            did_doc = await self._get_did_document(did)

            # Extract key information
            handle = await self._get_handle_from_did_doc(did_doc)
            pds = self._get_pds_from_did_doc(did_doc)
            signing_key = self._get_signing_key_from_did_doc(did_doc)

            return ResolvedIdentity(
                did=did, handle=handle, pds=pds, signing_key=signing_key
            )

        except Exception as e:
            raise ValueError(f"Failed to resolve DID {did}: {e}")

    async def _get_did_document(self, did: str) -> Dict[str, Any]:
        """Fetch DID document"""
        if did.startswith("did:plc:"):
            # PLC directory
            plc_url = "https://plc.directory"
            response = await self.client.get(f"{plc_url}/{did}")
            response.raise_for_status()
            return response.json()
        elif did.startswith("did:web:"):
            # Web DID
            domain = did.replace("did:web:", "")
            response = await self.client.get(f"https://{domain}/.well-known/did.json")
            response.raise_for_status()
            return response.json()
        else:
            raise ValueError(f"Unsupported DID method: {did}")

    async def _get_handle_from_did_doc(self, did_doc: Dict[str, Any]) -> Optional[str]:
        """Extract handle from DID document"""
        # Look for alsoKnownAs field
        also_known_as = did_doc.get("alsoKnownAs", [])
        for aka in also_known_as:
            if aka.startswith("at://"):
                return aka.replace("at://", "")
        return None

    def _get_pds_from_did_doc(self, did_doc: Dict[str, Any]) -> Optional[str]:
        """Extract PDS URL from DID document"""
        services = did_doc.get("service", [])
        for service in services:
            if service.get("type") == "AtprotoPersonalDataServer":
                return service.get("serviceEndpoint")
        return None

    def _get_signing_key_from_did_doc(self, did_doc: Dict[str, Any]) -> Optional[str]:
        """Extract signing key from DID document"""
        verification_methods = did_doc.get("verificationMethod", [])
        for vm in verification_methods:
            if "#atproto" in vm.get("id", ""):
                return vm.get("publicKeyMultibase")
        return None

    @lru_cache(maxsize=1000)
    async def resolve_did_cached(self, did: str) -> ResolvedIdentity:
        """Cached version of resolve for DIDs"""
        return await self.resolve(did)

    async def validate(self, did: str) -> bool:
        """
        Validate that a DID is properly formatted and resolvable

        Args:
            did: DID to validate

        Returns:
            True if valid and resolvable, False otherwise
        """
        try:
            await self.resolve(did)
            return True
        except Exception:
            return False

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Singleton instance
_resolver: Optional[RhizIdentityResolver] = None


def get_identity_resolver() -> RhizIdentityResolver:
    """Get the singleton identity resolver instance"""
    global _resolver
    if _resolver is None:
        _resolver = RhizIdentityResolver()
    return _resolver

