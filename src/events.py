"""Real-time event streaming for Haggl agents.

Provides Server-Sent Events (SSE) for live updates on agent status.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import AsyncGenerator, Optional
from enum import Enum
from pydantic import BaseModel, Field
from collections import defaultdict

logger = logging.getLogger(__name__)


class AgentStage(str, Enum):
    """Agent processing stages."""
    IDLE = "idle"
    MESSAGE_RECEIVED = "message_received"
    SOURCING = "sourcing"
    CALLING = "calling"
    NEGOTIATING = "negotiating"
    EVALUATING = "evaluating"
    CONFIRMED = "confirmed"
    APPROVAL_PENDING = "approval_pending"
    APPROVED = "approved"
    PAYING = "paying"
    PAYMENT_COMPLETE = "payment_complete"
    COMPLETED = "completed"
    FAILED = "failed"


class EventType(str, Enum):
    """Types of events."""
    STAGE_CHANGE = "stage_change"
    LOG = "log"
    VENDOR_UPDATE = "vendor_update"
    CALL_UPDATE = "call_update"
    EVALUATION_UPDATE = "evaluation_update"
    ORDER_UPDATE = "order_update"
    APPROVAL_REQUIRED = "approval_required"
    PAYMENT_UPDATE = "payment_update"
    SYSTEM = "system"


class AgentEvent(BaseModel):
    """Event emitted by agents."""
    event_type: EventType
    stage: AgentStage
    order_id: Optional[str] = None
    message: str
    data: dict = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_sse(self) -> str:
        """Format as Server-Sent Event."""
        return f"data: {self.model_dump_json()}\n\n"


class EventBus:
    """
    Simple async event bus for broadcasting events to connected clients.
    """
    
    def __init__(self):
        self._subscribers: dict[str, asyncio.Queue] = {}
        self._event_history: list[AgentEvent] = []
        self._max_history = 100
        self._current_stage: dict[str, AgentStage] = {}  # order_id -> stage
        self._lock = asyncio.Lock()
    
    async def subscribe(self, client_id: str) -> AsyncGenerator[str, None]:
        """
        Subscribe to events. Yields SSE-formatted strings.
        
        Args:
            client_id: Unique client identifier
            
        Yields:
            SSE formatted event strings
        """
        queue: asyncio.Queue = asyncio.Queue()
        
        async with self._lock:
            self._subscribers[client_id] = queue
            logger.info(f"Client {client_id} subscribed. Total: {len(self._subscribers)}")
        
        # Send recent history first
        for event in self._event_history[-20:]:
            yield event.to_sse()
        
        try:
            while True:
                event = await queue.get()
                yield event.to_sse()
        finally:
            async with self._lock:
                self._subscribers.pop(client_id, None)
                logger.info(f"Client {client_id} unsubscribed. Total: {len(self._subscribers)}")
    
    async def publish(self, event: AgentEvent):
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
        
        # Update current stage if order_id present
        if event.order_id:
            self._current_stage[event.order_id] = event.stage
        
        # Broadcast to all subscribers
        async with self._lock:
            for client_id, queue in self._subscribers.items():
                try:
                    await queue.put(event)
                except Exception as e:
                    logger.error(f"Failed to send event to {client_id}: {e}")
        
        logger.debug(f"Published event: {event.event_type} - {event.message}")
    
    def get_current_stage(self, order_id: str) -> AgentStage:
        """Get current stage for an order."""
        return self._current_stage.get(order_id, AgentStage.IDLE)
    
    def get_recent_events(self, limit: int = 20) -> list[AgentEvent]:
        """Get recent events."""
        return self._event_history[-limit:]


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get or create the global event bus."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


# Convenience functions for emitting events
async def emit_stage_change(
    stage: AgentStage,
    message: str,
    order_id: Optional[str] = None,
    **data
):
    """Emit a stage change event."""
    event = AgentEvent(
        event_type=EventType.STAGE_CHANGE,
        stage=stage,
        order_id=order_id,
        message=message,
        data=data,
    )
    await get_event_bus().publish(event)


async def emit_log(
    stage: AgentStage,
    message: str,
    order_id: Optional[str] = None,
    level: str = "info",
    **data
):
    """Emit a log event."""
    event = AgentEvent(
        event_type=EventType.LOG,
        stage=stage,
        order_id=order_id,
        message=message,
        data={"level": level, **data},
    )
    await get_event_bus().publish(event)


async def emit_vendor_update(
    stage: AgentStage,
    message: str,
    order_id: str,
    vendor_name: str,
    **data
):
    """Emit a vendor-related update."""
    event = AgentEvent(
        event_type=EventType.VENDOR_UPDATE,
        stage=stage,
        order_id=order_id,
        message=message,
        data={"vendor_name": vendor_name, **data},
    )
    await get_event_bus().publish(event)


async def emit_call_update(
    stage: AgentStage,
    message: str,
    order_id: str,
    vendor_name: str,
    call_status: str,
    **data
):
    """Emit a call status update."""
    event = AgentEvent(
        event_type=EventType.CALL_UPDATE,
        stage=stage,
        order_id=order_id,
        message=message,
        data={"vendor_name": vendor_name, "call_status": call_status, **data},
    )
    await get_event_bus().publish(event)


async def emit_evaluation_update(
    stage: AgentStage,
    message: str,
    order_id: str,
    selected_vendor: Optional[str] = None,
    **data
):
    """Emit an evaluation update."""
    event = AgentEvent(
        event_type=EventType.EVALUATION_UPDATE,
        stage=stage,
        order_id=order_id,
        message=message,
        data={"selected_vendor": selected_vendor, **data},
    )
    await get_event_bus().publish(event)


async def emit_approval_required(
    order_id: str,
    vendor_name: str,
    price: float,
    product: str,
    quantity: int,
    unit: str,
):
    """Emit approval required event."""
    event = AgentEvent(
        event_type=EventType.APPROVAL_REQUIRED,
        stage=AgentStage.APPROVAL_PENDING,
        order_id=order_id,
        message=f"Approval needed: {quantity} {unit} of {product} from {vendor_name} at ${price:.2f}",
        data={
            "vendor_name": vendor_name,
            "price": price,
            "product": product,
            "quantity": quantity,
            "unit": unit,
        },
    )
    await get_event_bus().publish(event)


async def emit_order_approved(order_id: str, vendor_name: str):
    """Emit order approved event."""
    event = AgentEvent(
        event_type=EventType.ORDER_UPDATE,
        stage=AgentStage.APPROVED,
        order_id=order_id,
        message=f"Order approved! Proceeding with {vendor_name}",
        data={"vendor_name": vendor_name, "action": "approved"},
    )
    await get_event_bus().publish(event)


async def emit_payment_started(order_id: str, vendor_name: str, amount: float):
    """Emit payment started event."""
    event = AgentEvent(
        event_type=EventType.PAYMENT_UPDATE,
        stage=AgentStage.PAYING,
        order_id=order_id,
        message=f"Processing payment of ${amount:.2f} to {vendor_name}...",
        data={"vendor_name": vendor_name, "amount": amount, "status": "processing"},
    )
    await get_event_bus().publish(event)


async def emit_payment_complete(
    order_id: str,
    vendor_name: str,
    amount: float,
    confirmation: str,
    receipt_url: Optional[str] = None,
):
    """Emit payment complete event."""
    event = AgentEvent(
        event_type=EventType.PAYMENT_UPDATE,
        stage=AgentStage.PAYMENT_COMPLETE,
        order_id=order_id,
        message=f"✅ Payment complete! ${amount:.2f} paid to {vendor_name}",
        data={
            "vendor_name": vendor_name,
            "amount": amount,
            "status": "succeeded",
            "confirmation": confirmation,
            "receipt_url": receipt_url,
        },
    )
    await get_event_bus().publish(event)


async def emit_payment_failed(order_id: str, vendor_name: str, error: str):
    """Emit payment failed event."""
    event = AgentEvent(
        event_type=EventType.PAYMENT_UPDATE,
        stage=AgentStage.FAILED,
        order_id=order_id,
        message=f"❌ Payment failed: {error}",
        data={"vendor_name": vendor_name, "status": "failed", "error": error},
    )
    await get_event_bus().publish(event)
