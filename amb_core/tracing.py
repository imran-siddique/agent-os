"""OpenTelemetry tracing utilities for AMB."""

from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def get_trace_id() -> Optional[str]:
    """
    Get the current trace ID from the active span context.

    Returns:
        Trace ID as hex string if available, None otherwise
    """
    span = trace.get_current_span()
    if span and span.get_span_context().is_valid:
        return format(span.get_span_context().trace_id, '032x')
    return None


def initialize_tracing(_service_name: str = "amb-core") -> None:
    """
    Initialize OpenTelemetry tracing for the message bus.

    This sets up a basic tracer with console export for development.
    In production, you would configure this to export to your preferred backend
    (e.g., Jaeger, Zipkin, or a cloud provider's tracing service).

    Args:
        _service_name: Name of the service for tracing (reserved for future use)
    """
    provider = TracerProvider()
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)


def get_tracer(name: str = "amb-core") -> trace.Tracer:
    """
    Get a tracer instance for creating spans.

    Args:
        name: Name for the tracer

    Returns:
        OpenTelemetry Tracer instance
    """
    return trace.get_tracer(name)
