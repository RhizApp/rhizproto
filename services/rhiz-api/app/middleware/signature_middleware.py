"""
Signature verification middleware
Automatically verifies signatures on relationship operations
"""

from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.signature_verification import SignatureVerificationService


class SignatureVerificationMiddleware:
    """Middleware to verify cryptographic signatures on sensitive operations"""
    
    def __init__(self):
        self.verification_service = SignatureVerificationService()
        self.security = HTTPBearer(auto_error=False)
    
    async def __call__(self, request: Request, call_next: Callable):
        """Process request and verify signatures when required"""
        
        # Check if this endpoint requires signature verification
        if self._requires_signature_verification(request):
            await self._verify_request_signature(request)
        
        # Process the request
        response = await call_next(request)
        
        # Add signature verification headers to response
        if hasattr(request.state, "signature_verified"):
            response.headers["X-Signature-Verified"] = str(request.state.signature_verified)
        
        return response
    
    def _requires_signature_verification(self, request: Request) -> bool:
        """Determine if the request requires signature verification"""
        path = request.url.path
        method = request.method
        
        # Require signatures for relationship creation/modification
        signature_required_patterns = [
            ("/api/v1/relationships", "POST"),
            ("/api/v1/relationships", "PUT"),
            ("/api/v1/relationships", "PATCH"),
            ("/api/v1/entities", "POST"),  # Entity creation
        ]
        
        for pattern_path, pattern_method in signature_required_patterns:
            if path.startswith(pattern_path) and method == pattern_method:
                return True
                
        return False
    
    async def _verify_request_signature(self, request: Request):
        """Verify signature in request"""
        try:
            # Extract signature from Authorization header
            credentials: HTTPAuthorizationCredentials = await self.security(request)
            if not credentials:
                raise HTTPException(
                    status_code=401,
                    detail="Signature required for this operation"
                )
            
            # Parse signature data from token
            signature_data = self._parse_signature_token(credentials.credentials)
            
            # Get request body for verification
            body = await request.body()
            
            # Verify signature
            is_valid = await self._verify_signature_against_body(signature_data, body)
            
            if not is_valid:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid signature"
                )
            
            # Store verification result in request state
            request.state.signature_verified = True
            request.state.signer_did = signature_data.get("did")
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Signature verification failed: {str(e)}"
            )
    
    def _parse_signature_token(self, token: str) -> dict:
        """Parse signature information from authorization token"""
        import json
        import base64
        
        try:
            # Decode base64 token
            decoded = base64.b64decode(token).decode('utf-8')
            signature_data = json.loads(decoded)
            
            required_fields = ["did", "signature", "timestamp"]
            if not all(field in signature_data for field in required_fields):
                raise ValueError("Missing required signature fields")
            
            return signature_data
            
        except Exception as e:
            raise ValueError(f"Invalid signature token format: {e}")
    
    async def _verify_signature_against_body(
        self, 
        signature_data: dict, 
        body: bytes
    ) -> bool:
        """Verify signature against request body"""
        try:
            # Create verification service instance
            verifier = SignatureVerificationService()
            
            # Verify the signature
            result = await verifier._verify_single_signature(body, signature_data)
            
            return result["valid"]
            
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False


async def verify_relationship_signatures_endpoint(
    relationship_data: dict,
    signatures: list
) -> dict:
    """
    Standalone endpoint for signature verification
    Can be called directly by clients to verify signatures
    """
    verification_service = SignatureVerificationService()
    
    # Mock relationship object for verification
    # In practice, would create proper Relationship instance
    class MockRelationship:
        def __init__(self, data):
            self.participants = data["participants"]
            self.type = data["type"]
            self.strength = data["strength"]
            self.context = data["context"]
            self.temporal = data.get("temporal", {})
            self.last_interaction = data.get("last_interaction")
            self.privacy = data.get("privacy", {})
    
    relationship = MockRelationship(relationship_data)
    
    # Verify signatures
    verification_result = await verification_service.verify_relationship_signatures(
        relationship, signatures
    )
    
    return verification_result