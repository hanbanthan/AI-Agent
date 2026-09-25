import json
import logging

from agent_engineer.observability.metrics import aggregate_trace

from agent_engineer.observability.trace import Trace

class TraceLogger:

    def __init__(
        self,
        logger: logging.Logger | None = None
    ) -> None:
        self.logger = (
            logger
            if logger is not None
            else logging.getLogger("agent_engineer")
        )

    def log(
        self,
        trace: Trace,
    ) -> None:

        metrics = aggregate_trace(trace)

        payload = {
            "trace_id": trace.id,
            "name": trace.name,
            "latency_ms": metrics.latency_ms,
            "input_tokens": metrics.input_tokens,
            "output_tokens": metrics.output_tokens,
            "total_tokens": metrics.total_tokens,
            "cost": metrics.cost,
            "tool_calls": metrics.tool_calls,
            "retries": metrics.retries,
            "errors": metrics.error_count,
        }
        self.logger.info(
            json.dumps(payload)
        )