"""
Main Rhiz SDK client
"""

from typing import Any, Optional

import httpx

from rhiz_sdk.api.graph import GraphAPI
from rhiz_sdk.api.entities import EntitiesAPI
from rhiz_sdk.api.analytics import AnalyticsAPI


class RhizError(Exception):
    """Rhiz API error"""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Any = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class RhizClient:
    """Rhiz Protocol API client"""

    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize Rhiz client

        Args:
            api_url: Base URL of Rhiz API
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self._client = httpx.Client(
            base_url=f"{api_url}/api/v1",
            headers=headers,
            timeout=timeout,
        )

        # Initialize API modules
        self.graph = GraphAPI(self._client)
        self.entities = EntitiesAPI(self._client)
        self.analytics = AnalyticsAPI(self._client)

    def __enter__(self) -> "RhizClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client"""
        self._client.close()

    @staticmethod
    def _handle_error(response: httpx.Response) -> None:
        """Handle HTTP errors"""
        if response.is_success:
            return

        try:
            error_data = response.json()
            message = error_data.get("detail", response.text)
        except Exception:
            message = response.text

        raise RhizError(
            message=message,
            status_code=response.status_code,
            details=error_data if "error_data" in locals() else None,
        )

