"""
Cryptographic signature verification for relationship records
Ensures relationship authenticity through DID-based signatures
"""

import json
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import aiohttp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature

from app.models.relationship import Relationship


class SignatureVerificationService:
    """
    Service for verifying cryptographic signatures on relationship records
    
    Integrates with AT Protocol DID resolution for public key verification
    """
    
    def __init__(self):
        self._did_cache: Dict[str, Dict] = {}
        self._cache_ttl = 3600  # 1 hour cache for DID documents
    
    async def verify_relationship_signatures(
        self, 
        relationship: Relationship,
        signatures: List[Dict[str, str]]
    ) -> Dict[str, any]:
        """
        Verify all signatures on a relationship record
        
        Args:
            relationship: The relationship record to verify
            signatures: List of signature objects with DID and signature data
            
        Returns:
            Verification result with per-signature status and overall validity
        """
        verification_results = {
            "valid": False,
            "signature_count": len(signatures),
            "verified_signatures": 0,
            "participant_coverage": False,
            "signatures": [],
            "errors": []
        }
        
        # Get canonical relationship data for verification
        canonical_data = self._get_canonical_relationship_data(relationship)
        
        # Verify each signature
        for signature_data in signatures:
            sig_result = await self._verify_single_signature(
                canonical_data, signature_data
            )
            verification_results["signatures"].append(sig_result)
            
            if sig_result["valid"]:
                verification_results["verified_signatures"] += 1
            else:
                verification_results["errors"].extend(sig_result["errors"])
        
        # Check if both participants have signed
        participant_dids = set(relationship.participants)
        signed_dids = set(
            sig["did"] for sig in verification_results["signatures"] 
            if sig["valid"]
        )
        
        verification_results["participant_coverage"] = participant_dids.issubset(signed_dids)
        verification_results["valid"] = (
            verification_results["verified_signatures"] >= 2 and
            verification_results["participant_coverage"]
        )
        
        return verification_results
    
    async def _verify_single_signature(
        self, 
        canonical_data: bytes, 
        signature_data: Dict[str, str]
    ) -> Dict[str, any]:
        """Verify a single signature against canonical relationship data"""
        result = {
            "did": signature_data.get("did"),
            "valid": False,
            "timestamp": signature_data.get("timestamp"),
            "errors": []
        }
        
        try:
            # Resolve DID to get public key
            did_document = await self._resolve_did(signature_data["did"])
            if not did_document:
                result["errors"].append(f"Failed to resolve DID: {signature_data['did']}")
                return result
            
            # Extract public key from DID document
            public_key = self._extract_verification_key(did_document)
            if not public_key:
                result["errors"].append("No verification key found in DID document")
                return result
            
            # Decode and verify signature
            signature_bytes = self._decode_signature(signature_data["signature"])
            if not signature_bytes:
                result["errors"].append("Invalid signature encoding")
                return result
            
            # Perform cryptographic verification
            is_valid = await self._verify_signature(
                public_key, canonical_data, signature_bytes
            )
            
            result["valid"] = is_valid
            if not is_valid:
                result["errors"].append("Signature verification failed")
                
        except Exception as e:
            result["errors"].append(f"Verification error: {str(e)}")
        
        return result
    
    def _get_canonical_relationship_data(self, relationship: Relationship) -> bytes:
        """
        Generate canonical representation of relationship data for signing
        
        Creates deterministic byte representation that both parties can reproduce
        """
        # Create ordered dictionary with essential relationship data
        canonical_dict = {
            "participants": sorted(relationship.participants),  # Ensure consistent ordering
            "type": relationship.type.value if hasattr(relationship.type, 'value') else str(relationship.type),
            "strength": relationship.strength,
            "context": relationship.context,
            "temporal": {
                "start": relationship.temporal.get("start", "").isoformat() if relationship.temporal else "",
                "last_interaction": relationship.last_interaction.isoformat() if relationship.last_interaction else ""
            },
            "privacy": {
                "visibility": relationship.privacy.get("visibility", "") if relationship.privacy else "",
                "consent": relationship.privacy.get("consent", "") if relationship.privacy else ""
            }
        }
        
        # Convert to canonical JSON (sorted keys, no whitespace)
        canonical_json = json.dumps(canonical_dict, sort_keys=True, separators=(',', ':'))
        
        # Hash the canonical representation
        return hashlib.sha256(canonical_json.encode('utf-8')).digest()
    
    async def _resolve_did(self, did: str) -> Optional[Dict]:
        """
        Resolve DID to get DID document with caching
        
        Integrates with AT Protocol PLC directory
        """
        # Check cache first
        cache_key = f"did:{did}"
        cached_doc = self._did_cache.get(cache_key)
        
        if cached_doc and (datetime.utcnow() - cached_doc["cached_at"]).seconds < self._cache_ttl:
            return cached_doc["document"]
        
        try:
            # Resolve DID through AT Protocol infrastructure
            if did.startswith("did:plc:"):
                url = f"https://plc.directory/{did}"
            elif did.startswith("did:web:"):
                # Handle did:web resolution
                domain = did.replace("did:web:", "")
                url = f"https://{domain}/.well-known/did.json"
            else:
                return None
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        did_document = await response.json()
                        
                        # Cache the result
                        self._did_cache[cache_key] = {
                            "document": did_document,
                            "cached_at": datetime.utcnow()
                        }
                        
                        return did_document
                        
        except Exception as e:
            print(f"DID resolution failed for {did}: {e}")
        
        return None
    
    def _extract_verification_key(self, did_document: Dict) -> Optional[rsa.RSAPublicKey]:
        """
        Extract verification public key from DID document
        
        Looks for keys with 'authentication' or 'assertionMethod' capabilities
        """
        try:
            verification_methods = did_document.get("verificationMethod", [])
            
            for method in verification_methods:
                # Look for RSA keys used for authentication
                if (method.get("type") == "RsaVerificationKey2018" or
                    method.get("type") == "JsonWebKey2020"):
                    
                    # Extract public key material
                    if "publicKeyPem" in method:
                        pem_data = method["publicKeyPem"]
                        public_key = serialization.load_pem_public_key(
                            pem_data.encode('utf-8')
                        )
                        return public_key
                    
                    elif "publicKeyJwk" in method:
                        # Handle JWK format
                        jwk = method["publicKeyJwk"]
                        if jwk.get("kty") == "RSA":
                            # Convert JWK to RSA public key
                            # Implementation would depend on specific JWK structure
                            pass
            
        except Exception as e:
            print(f"Key extraction failed: {e}")
        
        return None
    
    def _decode_signature(self, signature_b64: str) -> Optional[bytes]:
        """Decode base64-encoded signature"""
        try:
            import base64
            return base64.b64decode(signature_b64)
        except Exception:
            return None
    
    async def _verify_signature(
        self, 
        public_key: rsa.RSAPublicKey, 
        data: bytes, 
        signature: bytes
    ) -> bool:
        """Perform RSA signature verification"""
        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False
    
    async def create_signature_challenge(
        self, 
        relationship_data: Dict,
        participant_did: str
    ) -> Dict[str, str]:
        """
        Create a signature challenge for a relationship participant
        
        Returns challenge data that the participant must sign
        """
        # Create canonical data representation
        canonical_data = self._create_canonical_challenge_data(relationship_data)
        
        # Generate challenge
        challenge = {
            "challenge_id": hashlib.sha256(
                f"{participant_did}:{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:16],
            "participant_did": participant_did,
            "canonical_data": canonical_data.hex(),
            "instructions": "Sign the canonical_data with your DID's private key",
            "expires_at": (datetime.utcnow().timestamp() + 300),  # 5 minute expiry
            "signature_format": "base64(rsa_pss_sha256(canonical_data))"
        }
        
        return challenge
    
    def _create_canonical_challenge_data(self, relationship_data: Dict) -> bytes:
        """Create canonical data for signature challenge"""
        # Similar to relationship canonicalization but for challenges
        canonical_dict = {
            "participants": sorted(relationship_data.get("participants", [])),
            "type": relationship_data.get("type", ""),
            "strength": relationship_data.get("strength", 0),
            "context": relationship_data.get("context", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        canonical_json = json.dumps(canonical_dict, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical_json.encode('utf-8')).digest()
    
    async def batch_verify_signatures(
        self, 
        relationships_with_signatures: List[Tuple[Relationship, List[Dict]]]
    ) -> List[Dict]:
        """
        Efficiently verify signatures for multiple relationships
        
        Uses concurrent processing and DID document caching
        """
        import asyncio
        
        # Create verification tasks
        tasks = []
        for relationship, signatures in relationships_with_signatures:
            task = self.verify_relationship_signatures(relationship, signatures)
            tasks.append(task)
        
        # Execute verifications concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        verification_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                verification_results.append({
                    "relationship_id": relationships_with_signatures[i][0].id,
                    "valid": False,
                    "error": str(result)
                })
            else:
                result["relationship_id"] = relationships_with_signatures[i][0].id
                verification_results.append(result)
        
        return verification_results
    
    def get_verification_statistics(self, verification_results: List[Dict]) -> Dict:
        """Generate statistics from batch verification results"""
        total = len(verification_results)
        valid = sum(1 for r in verification_results if r.get("valid", False))
        
        return {
            "total_relationships": total,
            "valid_relationships": valid,
            "invalid_relationships": total - valid,
            "verification_rate": valid / total if total > 0 else 0,
            "average_signatures_per_relationship": sum(
                r.get("signature_count", 0) for r in verification_results
            ) / total if total > 0 else 0
        }