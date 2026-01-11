"""
Haggl - AI-powered procurement automation for small businesses.

Multi-agent system that automates vendor sourcing, price negotiation,
and payment processing.
"""

__version__ = "1.0.0"
__author__ = "Haggl Contributors"
__license__ = "MIT"

from .events import AgentStage, EventType, AgentEvent, get_event_bus

__all__ = [
    "__version__",
    "AgentStage",
    "EventType",
    "AgentEvent",
    "get_event_bus",
]
