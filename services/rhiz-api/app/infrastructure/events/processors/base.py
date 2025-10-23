"""
Abstract base event processor
"""

from abc import ABC, abstractmethod
import logging

from ..types import ProtocolEvent

logger = logging.getLogger(__name__)


class EventProcessor(ABC):
    """
    Abstract event processor

    Subclasses implement specific processing logic for different event types
    """

    @abstractmethod
    async def process(self, event: ProtocolEvent) -> bool:
        """
        Process event

        Args:
            event: Event to process

        Returns:
            True if processing succeeded

        Raises:
            Exception if processing fails
        """
        pass

    @abstractmethod
    def can_process(self, event: ProtocolEvent) -> bool:
        """
        Check if this processor can handle the event

        Args:
            event: Event to check

        Returns:
            True if this processor can handle this event type
        """
        pass

    async def on_success(self, event: ProtocolEvent):
        """
        Called after successful processing

        Args:
            event: Successfully processed event
        """
        logger.info(f"Event {event.event_id} processed successfully by {self.__class__.__name__}")

    async def on_failure(self, event: ProtocolEvent, error: Exception):
        """
        Called after failed processing

        Args:
            event: Failed event
            error: Exception that caused failure
        """
        logger.error(
            f"Event {event.event_id} failed in {self.__class__.__name__}: {error}"
        )

