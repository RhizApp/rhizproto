"""
Comprehensive validation framework for Rhiz Protocol
Provides input validation, schema validation, and business rule validation
"""

import re
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator, ValidationError as PydanticValidationError

from app.core.exceptions import ValidationError, invalid_did


class ValidationType(Enum):
    """Types of validation"""
    FORMAT = "format"
    BUSINESS_RULE = "business_rule"
    SCHEMA = "schema"
    SECURITY = "security"


class ValidationResult:
    """Result of validation operation"""
    
    def __init__(self):
        self.is_valid = True
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
    
    def add_error(
        self, 
        field: str, 
        message: str, 
        validation_type: ValidationType = ValidationType.FORMAT,
        value: Any = None
    ):
        """Add validation error"""
        self.is_valid = False
        self.errors.append({
            "field": field,
            "message": message,
            "type": validation_type.value,
            "value": str(value) if value is not None else None
        })
    
    def add_warning(self, field: str, message: str, value: Any = None):
        """Add validation warning"""
        self.warnings.append({
            "field": field,
            "message": message,
            "value": str(value) if value is not None else None
        })
    
    def merge(self, other: 'ValidationResult'):
        """Merge another validation result"""
        if not other.is_valid:
            self.is_valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
    
    def to_exception(self) -> ValidationError:
        """Convert to validation exception"""
        if self.is_valid:
            raise ValueError("Cannot create exception from valid result")
        
        primary_error = self.errors[0] if self.errors else {"message": "Validation failed"}
        
        return ValidationError(
            message=primary_error["message"],
            field=primary_error.get("field"),
            value=primary_error.get("value"),
            details={
                "errors": self.errors,
                "warnings": self.warnings
            }
        )


class BaseValidator:
    """Base class for validators"""
    
    def __init__(self, strict: bool = True):
        self.strict = strict
    
    def validate(self, value: Any, field_name: str = "value") -> ValidationResult:
        """Validate a value"""
        result = ValidationResult()
        self._validate_impl(value, field_name, result)
        return result
    
    def _validate_impl(self, value: Any, field_name: str, result: ValidationResult):
        """Implementation of validation logic"""
        raise NotImplementedError()
    
    def __call__(self, value: Any, field_name: str = "value") -> ValidationResult:
        """Make validator callable"""
        return self.validate(value, field_name)


class DIDValidator(BaseValidator):
    """Validator for DID format and structure"""
    
    ALLOWED_METHODS = ["plc", "web", "key", "peer"]
    DID_PATTERN = re.compile(r"^did:([a-z0-9]+):([a-zA-Z0-9._-]+)$")
    
    def __init__(self, allowed_methods: Optional[List[str]] = None, strict: bool = True):
        super().__init__(strict)
        self.allowed_methods = allowed_methods or self.ALLOWED_METHODS
    
    def _validate_impl(self, value: Any, field_name: str, result: ValidationResult):
        """Validate DID format"""
        if not isinstance(value, str):
            result.add_error(field_name, "DID must be a string", value=value)
            return
        
        # Check basic format
        match = self.DID_PATTERN.match(value)
        if not match:
            result.add_error(
                field_name, 
                "Invalid DID format. Must be 'did:method:identifier'",
                value=value
            )
            return
        
        method, identifier = match.groups()
        
        # Check allowed methods
        if method not in self.allowed_methods:
            result.add_error(
                field_name,
                f"DID method '{method}' not allowed. Allowed: {self.allowed_methods}",
                value=value
            )
            return
        
        # Method-specific validation
        if method == "plc":
            self._validate_plc_did(identifier, field_name, result)
        elif method == "web":
            self._validate_web_did(identifier, field_name, result)
    
    def _validate_plc_did(self, identifier: str, field_name: str, result: ValidationResult):
        """Validate PLC DID identifier"""
        if len(identifier) < 24:
            result.add_error(
                field_name,
                "PLC DID identifier too short (minimum 24 characters)",
                value=identifier
            )
        
        # Check for valid base32 characters (simplified)
        if not re.match(r"^[a-z2-7]+$", identifier):
            result.add_error(
                field_name,
                "PLC DID identifier contains invalid characters",
                value=identifier
            )
    
    def _validate_web_did(self, identifier: str, field_name: str, result: ValidationResult):
        """Validate Web DID identifier"""
        # Basic domain validation
        domain_pattern = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$")
        
        domain = identifier.split(":")[0] if ":" in identifier else identifier
        
        if not domain_pattern.match(domain):
            result.add_error(
                field_name,
                "Invalid domain in Web DID",
                value=identifier
            )


class ATURIValidator(BaseValidator):
    """Validator for AT Protocol URI format"""
    
    AT_URI_PATTERN = re.compile(r"^at://([^/]+)/([^/]+)/([^/]+)/?([^/]+)?$")
    
    def _validate_impl(self, value: Any, field_name: str, result: ValidationResult):
        """Validate AT URI format"""
        if not isinstance(value, str):
            result.add_error(field_name, "AT URI must be a string", value=value)
            return
        
        if not value.startswith("at://"):
            result.add_error(
                field_name,
                "AT URI must start with 'at://'",
                value=value
            )
            return
        
        match = self.AT_URI_PATTERN.match(value)
        if not match:
            result.add_error(
                field_name,
                "Invalid AT URI format. Expected: at://did/collection/rkey[/cid]",
                value=value
            )
            return
        
        did, collection, rkey, cid = match.groups()
        
        # Validate DID component
        did_validator = DIDValidator()
        did_result = did_validator.validate(did, f"{field_name}.did")
        result.merge(did_result)
        
        # Validate collection format
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9]*(\.[a-zA-Z][a-zA-Z0-9]*)*$", collection):
            result.add_error(
                f"{field_name}.collection",
                "Invalid collection format",
                value=collection
            )
        
        # Validate record key
        if not re.match(r"^[a-zA-Z0-9._-]+$", rkey):
            result.add_error(
                f"{field_name}.rkey",
                "Invalid record key format",
                value=rkey
            )


class RelationshipStrengthValidator(BaseValidator):
    """Validator for relationship strength values"""
    
    def _validate_impl(self, value: Any, field_name: str, result: ValidationResult):
        """Validate relationship strength"""
        if not isinstance(value, (int, float)):
            result.add_error(
                field_name,
                "Relationship strength must be a number",
                value=value
            )
            return
        
        if not 0 <= value <= 100:
            result.add_error(
                field_name,
                "Relationship strength must be between 0 and 100",
                value=value
            )
        
        # Warning for unusual values
        if value == 0:
            result.add_warning(
                field_name,
                "Relationship strength of 0 indicates no trust",
                value=value
            )
        elif value == 100:
            result.add_warning(
                field_name,
                "Relationship strength of 100 indicates perfect trust",
                value=value
            )


class TimestampValidator(BaseValidator):
    """Validator for ISO 8601 timestamps"""
    
    def _validate_impl(self, value: Any, field_name: str, result: ValidationResult):
        """Validate timestamp format"""
        if not isinstance(value, str):
            result.add_error(
                field_name,
                "Timestamp must be a string",
                value=value
            )
            return
        
        try:
            # Try parsing as ISO 8601
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            
            # Check if timestamp is reasonable (not too far in future/past)
            now = datetime.utcnow()
            if dt.year < 1970:
                result.add_error(
                    field_name,
                    "Timestamp is too far in the past",
                    value=value
                )
            elif dt.year > now.year + 10:
                result.add_error(
                    field_name,
                    "Timestamp is too far in the future",
                    value=value
                )
                
        except ValueError as e:
            result.add_error(
                field_name,
                f"Invalid timestamp format: {e}",
                value=value
            )


class RelationshipValidator(BaseValidator):
    """Comprehensive validator for relationship records"""
    
    def __init__(self, strict: bool = True):
        super().__init__(strict)
        self.did_validator = DIDValidator()
        self.strength_validator = RelationshipStrengthValidator()
        self.timestamp_validator = TimestampValidator()
    
    def _validate_impl(self, value: Any, field_name: str, result: ValidationResult):
        """Validate relationship record"""
        if not isinstance(value, dict):
            result.add_error(
                field_name,
                "Relationship must be an object",
                value=type(value).__name__
            )
            return
        
        # Validate required fields
        required_fields = ["participants", "type", "strength", "context"]
        for field in required_fields:
            if field not in value:
                result.add_error(
                    f"{field_name}.{field}",
                    f"Missing required field: {field}"
                )
        
        # Validate participants
        if "participants" in value:
            self._validate_participants(value["participants"], f"{field_name}.participants", result)
        
        # Validate strength
        if "strength" in value:
            strength_result = self.strength_validator.validate(
                value["strength"], 
                f"{field_name}.strength"
            )
            result.merge(strength_result)
        
        # Validate relationship type
        if "type" in value:
            self._validate_relationship_type(value["type"], f"{field_name}.type", result)
        
        # Validate context
        if "context" in value:
            self._validate_context(value["context"], f"{field_name}.context", result)
        
        # Validate temporal data
        if "temporal" in value:
            self._validate_temporal(value["temporal"], f"{field_name}.temporal", result)
        
        # Validate verification data
        if "verification" in value:
            self._validate_verification(value["verification"], f"{field_name}.verification", result)
    
    def _validate_participants(self, participants: Any, field_name: str, result: ValidationResult):
        """Validate relationship participants"""
        if not isinstance(participants, list):
            result.add_error(
                field_name,
                "Participants must be a list",
                value=type(participants).__name__
            )
            return
        
        if len(participants) != 2:
            result.add_error(
                field_name,
                "Relationship must have exactly 2 participants",
                value=len(participants)
            )
            return
        
        # Validate each participant DID
        for i, participant in enumerate(participants):
            did_result = self.did_validator.validate(
                participant, 
                f"{field_name}[{i}]"
            )
            result.merge(did_result)
        
        # Check for self-relationships
        if participants[0] == participants[1]:
            result.add_error(
                field_name,
                "Self-relationships are not allowed",
                value=participants
            )
    
    def _validate_relationship_type(self, rel_type: Any, field_name: str, result: ValidationResult):
        """Validate relationship type"""
        valid_types = [
            "professional", "personal", "family", 
            "social", "civic", "educational"
        ]
        
        if not isinstance(rel_type, str):
            result.add_error(
                field_name,
                "Relationship type must be a string",
                value=type(rel_type).__name__
            )
            return
        
        if rel_type not in valid_types:
            result.add_error(
                field_name,
                f"Invalid relationship type. Must be one of: {valid_types}",
                value=rel_type
            )
    
    def _validate_context(self, context: Any, field_name: str, result: ValidationResult):
        """Validate relationship context"""
        if not isinstance(context, str):
            result.add_error(
                field_name,
                "Context must be a string",
                value=type(context).__name__
            )
            return
        
        if len(context.strip()) == 0:
            result.add_error(
                field_name,
                "Context cannot be empty",
                value=context
            )
        
        if len(context) > 500:
            result.add_error(
                field_name,
                "Context is too long (maximum 500 characters)",
                value=len(context)
            )
    
    def _validate_temporal(self, temporal: Any, field_name: str, result: ValidationResult):
        """Validate temporal relationship data"""
        if not isinstance(temporal, dict):
            result.add_error(
                field_name,
                "Temporal data must be an object",
                value=type(temporal).__name__
            )
            return
        
        # Validate timestamps
        for timestamp_field in ["start", "lastInteraction"]:
            if timestamp_field in temporal:
                timestamp_result = self.timestamp_validator.validate(
                    temporal[timestamp_field],
                    f"{field_name}.{timestamp_field}"
                )
                result.merge(timestamp_result)
        
        # Validate temporal logic
        if "start" in temporal and "lastInteraction" in temporal:
            try:
                start = datetime.fromisoformat(temporal["start"].replace("Z", "+00:00"))
                last = datetime.fromisoformat(temporal["lastInteraction"].replace("Z", "+00:00"))
                
                if last < start:
                    result.add_error(
                        f"{field_name}.lastInteraction",
                        "Last interaction cannot be before relationship start",
                        value=temporal["lastInteraction"]
                    )
            except ValueError:
                # Timestamp validation will catch format errors
                pass
    
    def _validate_verification(self, verification: Any, field_name: str, result: ValidationResult):
        """Validate verification data"""
        if not isinstance(verification, dict):
            result.add_error(
                field_name,
                "Verification data must be an object",
                value=type(verification).__name__
            )
            return
        
        # Validate consensus score
        if "consensusScore" in verification:
            score = verification["consensusScore"]
            if not isinstance(score, (int, float)) or not 0 <= score <= 100:
                result.add_error(
                    f"{field_name}.consensusScore",
                    "Consensus score must be between 0 and 100",
                    value=score
                )
        
        # Validate attestation counts
        count_fields = ["attestationCount", "verifyCount", "disputeCount"]
        for count_field in count_fields:
            if count_field in verification:
                count = verification[count_field]
                if not isinstance(count, int) or count < 0:
                    result.add_error(
                        f"{field_name}.{count_field}",
                        f"{count_field} must be a non-negative integer",
                        value=count
                    )


class CompositeValidator:
    """Validator that combines multiple validators"""
    
    def __init__(self, validators: List[BaseValidator]):
        self.validators = validators
    
    def validate(self, value: Any, field_name: str = "value") -> ValidationResult:
        """Run all validators and combine results"""
        result = ValidationResult()
        
        for validator in self.validators:
            validator_result = validator.validate(value, field_name)
            result.merge(validator_result)
        
        return result


class SchemaValidator:
    """Validator for Pydantic schema validation"""
    
    def __init__(self, schema_class: BaseModel):
        self.schema_class = schema_class
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate data against schema"""
        result = ValidationResult()
        
        try:
            self.schema_class(**data)
        except PydanticValidationError as e:
            for error in e.errors():
                field_path = ".".join(str(loc) for loc in error["loc"])
                result.add_error(
                    field_path,
                    error["msg"],
                    ValidationationType.SCHEMA,
                    error.get("input")
                )
        
        return result


# Validation decorators

def validate_input(validator: BaseValidator, field_name: str = "value"):
    """Decorator for input validation"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get the value to validate (first argument after self)
            if args and len(args) > 1:
                value = args[1]
                validation_result = validator.validate(value, field_name)
                
                if not validation_result.is_valid:
                    raise validation_result.to_exception()
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def validate_relationship_data(func):
    """Decorator for relationship data validation"""
    validator = RelationshipValidator()
    
    async def wrapper(*args, **kwargs):
        # Look for relationship data in arguments
        for arg in args:
            if isinstance(arg, dict) and "participants" in arg:
                validation_result = validator.validate(arg, "relationship")
                if not validation_result.is_valid:
                    raise validation_result.to_exception()
        
        return await func(*args, **kwargs)
    
    return wrapper


# Validation utilities

def validate_did_format(did: str) -> bool:
    """Quick DID format validation"""
    validator = DIDValidator()
    result = validator.validate(did)
    return result.is_valid


def validate_at_uri_format(uri: str) -> bool:
    """Quick AT URI format validation"""
    validator = ATURIValidator()
    result = validator.validate(uri)
    return result.is_valid


def create_relationship_validator(strict: bool = True) -> RelationshipValidator:
    """Factory for relationship validator"""
    return RelationshipValidator(strict=strict)


def create_custom_validator(
    validation_func: Callable[[Any], bool],
    error_message: str
) -> BaseValidator:
    """Create custom validator from function"""
    
    class CustomValidator(BaseValidator):
        def _validate_impl(self, value: Any, field_name: str, result: ValidationResult):
            if not validation_func(value):
                result.add_error(field_name, error_message, value=value)
    
    return CustomValidator()