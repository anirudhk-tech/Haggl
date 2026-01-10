"""
IngredientAI Calling Agent - Phase 2

This agent orchestrates the vendor calling workflow using a simple
state machine pattern. It wraps the Vapi tools and manages the
call lifecycle.
"""

import asyncio
import logging
from typing import Optional
from datetime import datetime

from .schemas import (
    AgentState,
    AgentRequest,
    AgentResponse,
    CallVendorInput,
    CallOutcome,
)
from .tools.vapi_tool import (
    call_vendor,
    wait_for_call_completion,
    parse_call_outcome,
)

logger = logging.getLogger(__name__)


class CallingAgent:
    """
    The Calling Agent manages the state machine for vendor calls.
    
    States:
        READY_TO_CALL -> CALL_IN_PROGRESS -> PROCESSING -> CONFIRMED -> PLACED
                                          -> FAILED (from any state)
    """
    
    def __init__(self):
        self.state = AgentState.READY_TO_CALL
        self.call_id: Optional[str] = None
        self.outcome: Optional[CallOutcome] = None
        self.error: Optional[str] = None
        self._call_history: dict[str, dict] = {}  # For idempotency
    
    def _transition(self, new_state: AgentState) -> None:
        """Transition to a new state with logging."""
        logger.info(f"Agent state transition: {self.state} -> {new_state}")
        self.state = new_state
    
    async def process_order(self, request: AgentRequest) -> AgentResponse:
        """
        Main entry point: process an order request.
        
        Implements idempotency - if we've already processed this order,
        return the cached result.
        """
        # Idempotency check
        if request.order_id in self._call_history:
            cached = self._call_history[request.order_id]
            logger.info(f"Returning cached result for order {request.order_id}")
            return AgentResponse(
                order_id=request.order_id,
                status=cached["status"],
                call_id=cached.get("call_id"),
                outcome=cached.get("outcome"),
                error=cached.get("error"),
            )
        
        # Reset state for new order
        self.state = AgentState.READY_TO_CALL
        self.call_id = None
        self.outcome = None
        self.error = None
        
        try:
            # Step 1: Initiate the call
            self._transition(AgentState.CALL_IN_PROGRESS)
            
            call_input = CallVendorInput(
                phone_number=request.vendor.phone,
                vendor_name=request.vendor.name,
                business_name=request.order_context.business_name,
                product=request.order_context.product,
                quantity=request.order_context.quantity,
                unit=request.order_context.unit,
            )
            
            logger.info(f"Initiating call to {request.vendor.name} at {request.vendor.phone}")
            call_result = await call_vendor(call_input)
            
            if call_result.get("error"):
                self._transition(AgentState.FAILED)
                self.error = call_result["error"]
                return self._build_response(request.order_id)
            
            self.call_id = call_result["call_id"]
            logger.info(f"Call initiated with ID: {self.call_id}")
            
            # Step 2: Wait for call completion
            logger.info("Waiting for call to complete...")
            final_status = await wait_for_call_completion(self.call_id)
            
            self._transition(AgentState.PROCESSING)
            
            if final_status.get("error"):
                self._transition(AgentState.FAILED)
                self.error = final_status["error"]
                return self._build_response(request.order_id)
            
            # Step 3: Parse the outcome
            logger.info("Parsing call outcome...")
            self.outcome = parse_call_outcome(
                final_status.get("transcript", ""),
                final_status.get("ended_reason"),
            )
            
            # Step 4: Determine final state
            if self.outcome.confirmed:
                self._transition(AgentState.CONFIRMED)
                # Calculate total price if we have a price
                if self.outcome.price:
                    total = self.outcome.price * request.order_context.quantity
                    logger.info(f"Order confirmed! Price: ${self.outcome.price}/dozen, Total: ${total}")
                self._transition(AgentState.PLACED)
            else:
                self._transition(AgentState.FAILED)
                self.error = "Order was not confirmed by vendor"
            
            # Cache the result for idempotency
            response = self._build_response(request.order_id)
            self._call_history[request.order_id] = {
                "status": response.status,
                "call_id": response.call_id,
                "outcome": response.outcome,
                "error": response.error,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            return response
            
        except Exception as e:
            logger.exception(f"Agent error: {e}")
            self._transition(AgentState.FAILED)
            self.error = str(e)
            return self._build_response(request.order_id)
    
    def _build_response(self, order_id: str) -> AgentResponse:
        """Build the response object from current state."""
        return AgentResponse(
            order_id=order_id,
            status=self.state,
            call_id=self.call_id,
            outcome=self.outcome,
            error=self.error,
        )
    
    def get_state(self) -> AgentState:
        """Get the current agent state."""
        return self.state
    
    def clear_history(self) -> None:
        """Clear the call history (for testing)."""
        self._call_history.clear()


# Global agent instance
_agent: Optional[CallingAgent] = None


def get_agent() -> CallingAgent:
    """Get or create the global agent instance."""
    global _agent
    if _agent is None:
        _agent = CallingAgent()
    return _agent
