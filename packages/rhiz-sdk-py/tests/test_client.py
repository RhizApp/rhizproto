"""
Test Rhiz client
"""

import pytest

from rhiz_sdk import RhizClient, RhizError


def test_client_initialization():
    """Test client can be initialized"""
    client = RhizClient(api_url="http://localhost:8000")
    assert client is not None
    assert client.graph is not None
    assert client.entities is not None
    assert client.analytics is not None


def test_client_with_api_key():
    """Test client can be initialized with API key"""
    client = RhizClient(api_url="http://localhost:8000", api_key="test-key")
    assert client is not None


def test_client_context_manager():
    """Test client works as context manager"""
    with RhizClient(api_url="http://localhost:8000") as client:
        assert client is not None


def test_rhiz_error():
    """Test RhizError properties"""
    error = RhizError(
        message="Test error", status_code=404, details={"detail": "Not found"}
    )

    assert isinstance(error, Exception)
    assert error.message == "Test error"
    assert error.status_code == 404
    assert error.details == {"detail": "Not found"}

