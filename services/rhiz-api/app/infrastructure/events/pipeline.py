"""
Real-time event processing pipeline

Handles protocol events with priority queues, worker pool, and backpressure
"""

import asyncio
import logging
import time
from collections import defaultdict
from typing import Dict, List, Optional

from .processors.base import EventProcessor
from .types import EventPriority, PipelineMetrics, ProtocolEvent

logger = logging.getLogger(__name__)


class EventPipeline:
    """
    Real-time event processing pipeline

    Features:
    - Priority queues (critical events processed first)
    - Worker pool (configurable concurrency)
    - Backpressure (reject events when queue full)
    - Retry logic (exponential backoff)
    - Dead letter queue (failed events after max retries)
    - Metrics tracking (throughput, latency, errors)
    """

    def __init__(
        self, max_queue_size: int = 10000, num_workers: int = 10, backpressure_threshold: float = 0.8
    ):
        """
        Initialize event pipeline

        Args:
            max_queue_size: Maximum total events in all queues
            num_workers: Number of worker tasks
            backpressure_threshold: Fraction of queue size to trigger backpressure (0.0-1.0)
        """
        # Priority queues (one per priority level)
        self._queues: Dict[EventPriority, asyncio.Queue] = {
            priority: asyncio.Queue(maxsize=max_queue_size // 4) for priority in EventPriority
        }

        self._num_workers = num_workers
        self._backpressure_threshold = backpressure_threshold
        self._max_queue_size = max_queue_size

        # Event processors (registered dynamically)
        self._processors: List[EventProcessor] = []

        # Worker management
        self._workers: List[asyncio.Task] = []
        self._running = False

        # Dead letter queue (events that failed after max retries)
        self._dead_letter: List[ProtocolEvent] = []

        # Metrics
        self._metrics = PipelineMetrics()
        self._processing_times: List[float] = []

        # Metrics calculation task
        self._metrics_task: Optional[asyncio.Task] = None

        logger.info(
            f"Event pipeline initialized: max_queue={max_queue_size}, workers={num_workers}"
        )

    def register_processor(self, processor: EventProcessor):
        """
        Register an event processor

        Args:
            processor: Event processor to register
        """
        self._processors.append(processor)
        logger.info(f"Registered processor: {processor.__class__.__name__}")

    async def enqueue(self, event: ProtocolEvent) -> bool:
        """
        Enqueue event for processing

        Args:
            event: Event to enqueue

        Returns:
            True if enqueued, False if backpressure active
        """
        queue = self._queues[event.priority]

        # Check backpressure
        total_events = sum(q.qsize() for q in self._queues.values())
        if total_events >= self._max_queue_size * self._backpressure_threshold:
            logger.warning(f"Backpressure active: {total_events} events in queue")
            self._metrics.backpressure_active = True
            return False
        else:
            self._metrics.backpressure_active = False

        try:
            queue.put_nowait(event)
            self._metrics.events_in_queue += 1
            return True

        except asyncio.QueueFull:
            logger.error(f"Queue full for priority {event.priority}")
            self._metrics.backpressure_active = True
            return False

    async def start(self):
        """Start the pipeline and worker pool"""
        if self._running:
            raise RuntimeError("Pipeline already running")

        self._running = True
        logger.info(f"Starting event pipeline with {self._num_workers} workers")

        # Start workers
        for i in range(self._num_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(worker)

        # Start metrics calculation
        self._metrics_task = asyncio.create_task(self._calculate_metrics())

        logger.info("Event pipeline started")

    async def stop(self):
        """Stop the pipeline gracefully"""
        if not self._running:
            return

        logger.info("Stopping event pipeline...")
        self._running = False

        # Wait for workers to finish current events
        if self._workers:
            try:
                await asyncio.wait_for(asyncio.gather(*self._workers, return_exceptions=True), timeout=10.0)
            except asyncio.TimeoutError:
                logger.warning("Workers did not finish within timeout, forcing shutdown")

        # Stop metrics task
        if self._metrics_task:
            self._metrics_task.cancel()

        logger.info("Event pipeline stopped")

    async def _worker(self, name: str):
        """
        Worker task that processes events from queues

        Args:
            name: Worker name for logging
        """
        logger.info(f"Worker {name} started")

        while self._running:
            event = await self._get_next_event()
            if event is None:
                await asyncio.sleep(0.1)  # No events, brief sleep
                continue

            # Process event and track time
            start_time = time.time()
            success = await self._process_event(event)
            processing_time_ms = (time.time() - start_time) * 1000

            self._processing_times.append(processing_time_ms)
            self._metrics.events_in_queue -= 1

            if success:
                self._metrics.events_processed += 1
            else:
                self._metrics.events_failed += 1

                # Add to dead letter queue if max retries exceeded
                if event.retry_count >= 3:
                    self._dead_letter.append(event)
                    logger.error(
                        f"Event {event.event_id} moved to dead letter queue after {event.retry_count} retries"
                    )

        logger.info(f"Worker {name} stopped")

    async def _get_next_event(self) -> Optional[ProtocolEvent]:
        """
        Get next event from queues (priority order)

        Returns:
            Next event or None if all queues empty
        """
        # Process in priority order (CRITICAL → HIGH → NORMAL → LOW)
        for priority in sorted(EventPriority, key=lambda p: p.value, reverse=True):
            queue = self._queues[priority]
            if not queue.empty():
                try:
                    return await asyncio.wait_for(queue.get(), timeout=0.1)
                except asyncio.TimeoutError:
                    continue

        return None

    async def _process_event(self, event: ProtocolEvent) -> bool:
        """
        Process event through registered processors

        Args:
            event: Event to process

        Returns:
            True if processing succeeded
        """
        for processor in self._processors:
            if processor.can_process(event):
                try:
                    success = await processor.process(event)

                    if success:
                        await processor.on_success(event)
                        return True
                    else:
                        await processor.on_failure(event, Exception("Processing returned False"))

                except Exception as e:
                    logger.error(f"Processor failed for event {event.event_id}: {e}")
                    await processor.on_failure(event, e)

                    # Retry logic with exponential backoff
                    if event.retry_count < 3:
                        event.retry_count += 1
                        backoff_seconds = 2**event.retry_count  # 2, 4, 8 seconds
                        logger.info(f"Retrying event {event.event_id} in {backoff_seconds}s")

                        await asyncio.sleep(backoff_seconds)
                        await self.enqueue(event)

                    return False

        logger.warning(f"No processor for event type: {event.event_type}")
        return False

    async def _calculate_metrics(self):
        """Calculate and update pipeline metrics every second"""
        last_processed = 0

        while self._running:
            await asyncio.sleep(1.0)

            # Throughput (events per second)
            current_processed = self._metrics.events_processed
            self._metrics.throughput_per_second = current_processed - last_processed
            last_processed = current_processed

            # Average processing time
            if self._processing_times:
                self._metrics.avg_processing_time_ms = sum(self._processing_times) / len(
                    self._processing_times
                )
                self._processing_times.clear()

            # Worker utilization
            total_events = sum(q.qsize() for q in self._queues.values())
            self._metrics.events_in_queue = total_events
            self._metrics.worker_utilization = min(total_events / self._num_workers, 1.0)

    def get_metrics(self) -> PipelineMetrics:
        """
        Get current pipeline metrics

        Returns:
            PipelineMetrics with current stats
        """
        return self._metrics

    def get_dead_letter_queue(self) -> List[ProtocolEvent]:
        """
        Get events in dead letter queue

        Returns:
            List of events that failed after max retries
        """
        return self._dead_letter.copy()

    def is_running(self) -> bool:
        """
        Check if pipeline is running

        Returns:
            True if running
        """
        return self._running

