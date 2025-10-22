"""
Standardized exception hierarchy for Rhiz Protocol
Provides clear error classification and proper HTTP status mapping
"""

from typing import Any, Dict, Optional
from enum import Enum


class ErrorCode(Enum):
    """Standardized error codes for the Rhiz Protocol"""
    
    # Validation Errors (400-level)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_DID = "INVALID_DID"
    INVALID_URI = "INVALID_URI"
    MISSING_SIGNATURE = "MISSING_SIGNATURE"
    INVALID_RELATIONSHIP_TYPE = "INVALID_RELATIONSHIP_TYPE"
    
    # Authentication/Authorization Errors (401/403)
    UNAUTHORIZED = "UNAUTHORIZED"
    SIGNATURE_VERIFICATION_FAILED = "SIGNATURE_VERIFICATION_FAILED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Not Found Errors (404)
    ENTITY_NOT_FOUND = "ENTITY_NOT_FOUND"
    RELATIONSHIP_NOT_FOUND = "RELATIONSHIP_NOT_FOUND"
    PATH_NOT_FOUND = "PATH_NOT_FOUND"
    
    # Conflict Errors (409)
    ENTITY_ALREADY_EXISTS = "ENTITY_ALREADY_EXISTS"
    RELATIONSHIP_ALREADY_EXISTS = "RELATIONSHIP_ALREADY_EXISTS"
    
    # Business Logic Errors (422)
    TRUST_SCORE_CALCULATION_FAILED = "TRUST_SCORE_CALCULATION_FAILED"
    NETWORK_PROPAGATION_FAILED = "NETWORK_PROPAGATION_FAILED"
    ATTESTATION_CONFLICT = "ATTESTATION_CONFLICT"
    
    # External Service Errors (502/503)
    DID_RESOLUTION_FAILED = "DID_RESOLUTION_FAILED"
    CACHE_SERVICE_UNAVAILABLE = "CACHE_SERVICE_UNAVAILABLE"
    DATABASE_CONNECTION_FAILED = "DATABASE_CONNECTION_FAILED"
    
    # Internal Errors (500)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"


class RhizProtocolError(Exception):
    """
    Base exception for all Rhiz Protocol errors
    
    Provides structured error information with proper HTTP status mapping
    """
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.cause = cause
        
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        error_dict = {
            "error": self.error_code.value,
            "message": self.message,
            "status_code": self.status_code
        }
        
        if self.details:
            error_dict["details"] = self.details
            
        if self.cause:
            error_dict["cause"] = str(self.cause)
            
        return error_dict
    
    def __str__(self) -> str:
        return f"{self.error_code.value}: {self.message}"


class ValidationError(RhizProtocolError):
    """Input validation errors (400 Bad Request)"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if field:
            error_details["field"] = field
        if value is not None:
            error_details["value"] = str(value)
            
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=400,
            details=error_details
        )


class AuthenticationError(RhizProtocolError):
    """Authentication failures (401 Unauthorized)"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            error_code=ErrorCode.UNAUTHORIZED,
            status_code=401
        )


class SignatureVerificationError(RhizProtocolError):
    """Signature verification failures (401 Unauthorized)"""
    
    def __init__(
        self,
        message: str = "Signature verification failed",
        did: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if did:
            error_details["did"] = did
            
        super().__init__(
            message=message,
            error_code=ErrorCode.SIGNATURE_VERIFICATION_FAILED,
            status_code=401,
            details=error_details
        )


class AuthorizationError(RhizProtocolError):
    """Authorization failures (403 Forbidden)"""
    
    def __init__(
        self,
        message: str = "Insufficient permissions",
        required_permission: Optional[str] = None
    ):
        details = {}
        if required_permission:
            details["required_permission"] = required_permission
            
        super().__init__(
            message=message,
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            status_code=403,
            details=details
        )


class NotFoundError(RhizProtocolError):
    """Resource not found errors (404 Not Found)"""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        message: Optional[str] = None
    ):
        if not message:
            message = f"{resource_type} not found"
            
        super().__init__(
            message=message,
            error_code=getattr(ErrorCode, f"{resource_type.upper()}_NOT_FOUND", ErrorCode.ENTITY_NOT_FOUND),
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class ConflictError(RhizProtocolError):
    """Resource conflict errors (409 Conflict)"""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        message: Optional[str] = None
    ):
        if not message:
            message = f"{resource_type} already exists"
            
        super().__init__(
            message=message,
            error_code=getattr(ErrorCode, f"{resource_type.upper()}_ALREADY_EXISTS", ErrorCode.ENTITY_ALREADY_EXISTS),
            status_code=409,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class BusinessLogicError(RhizProtocolError):
    """Business logic errors (422 Unprocessable Entity)"""
    
    def __init__(
        self,
        message: str,
        operation: str,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        error_details["operation"] = operation
        
        super().__init__(
            message=message,
            error_code=ErrorCode.TRUST_SCORE_CALCULATION_FAILED,  # Default, can be overridden
            status_code=422,
            details=error_details
        )


class TrustCalculationError(BusinessLogicError):
    """Trust score calculation failures"""
    
    def __init__(
        self,
        message: str = "Trust score calculation failed",
        entity_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if entity_id:
            error_details["entity_id"] = entity_id
            
        super().__init__(
            message=message,
            operation="trust_calculation",
            details=error_details
        )
        self.error_code = ErrorCode.TRUST_SCORE_CALCULATION_FAILED


class PathfindingError(BusinessLogicError):
    """Pathfinding operation failures"""
    
    def __init__(
        self,
        message: str = "Path not found",
        from_entity: Optional[str] = None,
        to_entity: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        if from_entity:
            error_details["from_entity"] = from_entity
        if to_entity:
            error_details["to_entity"] = to_entity
            
        super().__init__(
            message=message,
            operation="pathfinding",
            details=error_details
        )
        self.error_code = ErrorCode.PATH_NOT_FOUND


class ExternalServiceError(RhizProtocolError):
    """External service failures (502/503)"""
    
    def __init__(
        self,
        service_name: str,
        message: str,
        status_code: int = 502,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        error_details["service"] = service_name
        
        super().__init__(
            message=f"{service_name}: {message}",
            error_code=ErrorCode.DID_RESOLUTION_FAILED,  # Default, can be overridden
            status_code=status_code,
            details=error_details
        )


class DIDResolutionError(ExternalServiceError):
    """DID resolution failures"""
    
    def __init__(
        self,
        did: str,
        message: str = "DID resolution failed",
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        error_details["did"] = did
        
        super().__init__(
            service_name="DID Resolution",
            message=message,
            status_code=502,
            details=error_details
        )
        self.error_code = ErrorCode.DID_RESOLUTION_FAILED


class CacheServiceError(ExternalServiceError):
    """Cache service failures"""
    
    def __init__(
        self,
        operation: str,
        message: str = "Cache service unavailable",
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        error_details["operation"] = operation
        
        super().__init__(
            service_name="Cache",
            message=message,
            status_code=503,
            details=error_details
        )
        self.error_code = ErrorCode.CACHE_SERVICE_UNAVAILABLE


class DatabaseError(RhizProtocolError):
    """Database operation failures"""
    
    def __init__(
        self,
        operation: str,
        message: str = "Database operation failed",
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = details or {}
        error_details["operation"] = operation
        
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_CONNECTION_FAILED,
            status_code=503,
            details=error_details
        )


# Convenience functions for common error scenarios

def entity_not_found(entity_type: str, entity_id: str) -> NotFoundError:
    """Create a standardized entity not found error"""
    return NotFoundError(entity_type, entity_id)


def relationship_not_found(relationship_id: str) -> NotFoundError:
    """Create a standardized relationship not found error"""
    return NotFoundError("relationship", relationship_id)


def invalid_did(did: str, reason: str = "Invalid DID format") -> ValidationError:
    """Create a standardized invalid DID error"""
    return ValidationError(
        message=reason,
        field="did",
        value=did,
        details={"error_code": ErrorCode.INVALID_DID.value}
    )


def signature_required(operation: str) -> SignatureVerificationError:
    """Create a standardized signature required error"""
    return SignatureVerificationError(
        message=f"Signature required for {operation}",
        details={"operation": operation}
    )


def trust_calculation_failed(entity_id: str, reason: str) -> TrustCalculationError:
    """Create a standardized trust calculation error"""
    return TrustCalculationError(
        message=f"Trust calculation failed: {reason}",
        entity_id=entity_id,
        details={"reason": reason}
    )