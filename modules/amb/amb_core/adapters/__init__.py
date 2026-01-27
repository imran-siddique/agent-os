"""
Broker adapters package for AMB.

This module provides optional adapters for different message brokers.
Each adapter requires its corresponding extra dependencies.

Available Adapters:
    - RedisBroker: pip install amb-core[redis]
    - RabbitMQBroker: pip install amb-core[rabbitmq]
    - KafkaBroker: pip install amb-core[kafka]

Example:
    >>> from amb_core.adapters.redis_broker import RedisBroker
    >>> broker = RedisBroker(url="redis://localhost:6379/0")
"""

from typing import TYPE_CHECKING, List

__all__: List[str] = [
    "RedisBroker",
    "RabbitMQBroker",
    "KafkaBroker",
]


def __getattr__(name: str):
    """Lazy import adapters to avoid import errors when dependencies missing."""
    if name == "RedisBroker":
        from amb_core.adapters.redis_broker import RedisBroker
        return RedisBroker
    elif name == "RabbitMQBroker":
        from amb_core.adapters.rabbitmq_broker import RabbitMQBroker
        return RabbitMQBroker
    elif name == "KafkaBroker":
        from amb_core.adapters.kafka_broker import KafkaBroker
        return KafkaBroker
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
