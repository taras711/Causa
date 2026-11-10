"""Structured telemetry tracking for workflow execution and agent calls."""

from __future__ import annotations

import time
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable


@dataclass
class StepMetric:
    """Metrics for a single workflow step execution."""
    step_name: str
    case_id: str
    status: str  # "running", "completed", "failed"
    started_at: str
    completed_at: Optional[str] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None
    result_size: int = 0
    input_size: int = 0


@dataclass
class AgentCallMetric:
    """Metrics for an LLM agent call."""
    agent_name: str
    model_name: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None


@dataclass
class TelemetryRecord:
    """Base telemetry record emitted by the tracker."""
    timestamp: str
    event: str
    source: str  # "workflow_step" | "agent_call" | "security" | "system"
    data: Dict[str, Any] = field(default_factory=dict)


class TelemetryTracker:
    """Simple in-memory telemetry tracker.

    In production, this could flush records to Prometheus, Datadog,
    Elasticsearch, or a local database.
    """

    def __init__(self, flush_interval: int = 100) -> None:
        self._records: List[TelemetryRecord] = []
        self._flush_interval = flush_interval
        self._call_count = 0

    def record_step(self, metric: StepMetric) -> None:
        """Record a workflow step metric."""
        record = TelemetryRecord(
            timestamp=metric.started_at,
            event="workflow_step",
            source="workflow_engine",
            data=asdict(metric),
        )
        self._records.append(record)
        self._call_count += 1
        if len(self._records) >= self._flush_interval:
            self._flush()

    def record_agent_call(self, metric: AgentCallMetric) -> None:
        """Record an agent LLM call metric."""
        record = TelemetryRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            event="agent_call",
            source="agent",
            data=asdict(metric),
        )
        self._records.append(record)
        self._call_count += 1
        if len(self._records) >= self._flush_interval:
            self._flush()

    def record_security(self, event: str, data: Dict[str, Any]) -> None:
        """Record a security-related event."""
        record = TelemetryRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            event="security",
            source="security_layer",
            data={"event": event, **data},
        )
        self._records.append(record)
        self._call_count += 1
        if len(self._records) >= self._flush_interval:
            self._flush()

    def record_system(self, event: str, data: Dict[str, Any]) -> None:
        """Record a system-level event."""
        record = TelemetryRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            event="system",
            source="system",
            data={event: data},
        )
        self._records.append(record)

    def _flush(self) -> None:
        """Flush records - override in subclass or hook into external system."""
        # In production, this would send records to a monitoring system
        # For now, just log the count
        if self._records:
            import structlog as _sl
            _sl.get_logger(__name__).debug(
                "telemetry_flush", count=len(self._records)
            )
            self._records.clear()

    def get_records(self) -> List[Dict[str, Any]]:
        """Get all recorded telemetry records as dictionaries."""
        return [asdict(r) for r in self._records]


# Global instance - can be replaced with DI in production
_telemetry = TelemetryTracker()


def get_tracker() -> TelemetryTracker:
    """Get the global telemetry tracker instance."""
    return _telemetry


def track_step(
    tracker: Optional[TelemetryTracker] = None,
) -> Callable:
    """Decorator-like helper to track workflow step execution.

    Usage in WorkflowEngine or custom wrappers:
        @track_step()
        def my_step(case: Case) -> str:
            ...
    """

    def decorator(func: Callable) -> Callable:
        import functools

        @functools.wraps(func)
        def wrapper(case: Any, *args: Any, **kwargs: Any) -> Any:
            t = tracker or _telemetry
            start = time.time()
            started_at = datetime.now(timezone.utc).isoformat()
            try:
                result = func(case, *args, **kwargs)
                duration_ms = (time.time() - start) * 1000
                metric = StepMetric(
                    step_name=func.__name__,
                    case_id=getattr(case, "case_id", "unknown"),
                    status="completed",
                    started_at=started_at,
                    completed_at=datetime.now(timezone.utc).isoformat(),
                    duration_ms=duration_ms,
                    result_size=len(str(result)) if result else 0,
                )
                t.record_step(metric)
                return result
            except Exception as exc:  # noqa: BLE001
                duration_ms = (time.time() - start) * 1000
                metric = StepMetric(
                    step_name=func.__name__,
                    case_id=getattr(case, "case_id", "unknown"),
                    status="failed",
                    started_at=started_at,
                    completed_at=datetime.now(timezone.utc).isoformat(),
                    duration_ms=duration_ms,
                    error=str(exc),
                )
                t.record_step(metric)
                raise

        return wrapper

    return decorator


def track_agent_call(
    tracker: Optional[TelemetryTracker] = None,
) -> Callable:
    """Decorator to track agent LLM call metrics.

    Usage in agent run methods:
        @track_agent_call()
        async def run(self, input_data: InputT) -> OutputT:
            ...
    """

    def decorator(func) -> Callable:
        import functools

        @functools.wraps(func)
        async def wrapper(self, input_data, *args, **kwargs):
            t = tracker or _telemetry
            start = time.time()
            try:
                result = await func(self, input_data, *args, **kwargs)
                latency_ms = (time.time() - start) * 1000
                # Try to extract token counts from result if available
                prompt_tokens = getattr(result, "prompt_tokens", 0) or 0
                completion_tokens = getattr(result, "completion_tokens", 0) or 0
                metric = AgentCallMetric(
                    agent_name=self.name,
                    model_name=self.model_name,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    latency_ms=latency_ms,
                    success=True,
                )
                t.record_agent_call(metric)
                return result
            except Exception as exc:  # noqa: BLE001
                latency_ms = (time.time() - start) * 1000
                metric = AgentCallMetric(
                    agent_name=self.name,
                    model_name=self.model_name,
                    latency_ms=latency_ms,
                    success=False,
                    error=str(exc),
                )
                t.record_agent_call(metric)
                raise

        return wrapper

    return decorator