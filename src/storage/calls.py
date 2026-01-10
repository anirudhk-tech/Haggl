"""Call storage operations."""

import logging
from datetime import datetime
from typing import Optional

from .database import get_collection
from .schemas import CallDocument, CallStatus, CallOutcomeDocument

logger = logging.getLogger(__name__)

COLLECTION = "calls"


def save_call(call: CallDocument) -> bool:
    """
    Save or update a call record.
    
    Args:
        call: CallDocument to save
        
    Returns:
        True if successful
    """
    collection = get_collection(COLLECTION)
    if collection is None:
        logger.warning("No database connection - call not saved")
        return False
    
    try:
        call.updated_at = datetime.utcnow()
        collection.update_one(
            {"call_id": call.call_id},
            {"$set": call.model_dump()},
            upsert=True
        )
        logger.info(f"Saved call: {call.call_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to save call: {e}")
        return False


def get_call(call_id: str) -> Optional[CallDocument]:
    """Get a call by ID."""
    collection = get_collection(COLLECTION)
    if collection is None:
        return None
    
    try:
        doc = collection.find_one({"call_id": call_id})
        if doc:
            doc.pop("_id", None)
            return CallDocument(**doc)
        return None
    except Exception as e:
        logger.error(f"Failed to get call: {e}")
        return None


def update_call_status(
    call_id: str,
    status: CallStatus,
    ended_reason: Optional[str] = None,
    duration_seconds: Optional[int] = None,
    outcome: Optional[CallOutcomeDocument] = None
) -> bool:
    """
    Update call status and outcome.
    
    Args:
        call_id: Call ID
        status: New status
        ended_reason: Why call ended
        duration_seconds: Call duration
        outcome: Call outcome (confirmed, price, etc.)
        
    Returns:
        True if successful
    """
    collection = get_collection(COLLECTION)
    if collection is None:
        return False
    
    try:
        update = {
            "status": status.value,
            "updated_at": datetime.utcnow(),
        }
        
        if ended_reason:
            update["ended_reason"] = ended_reason
        if duration_seconds is not None:
            update["duration_seconds"] = duration_seconds
        if outcome:
            update["outcome"] = outcome.model_dump()
        
        result = collection.update_one(
            {"call_id": call_id},
            {"$set": update}
        )
        
        if result.modified_count > 0:
            logger.info(f"Updated call {call_id} -> {status.value}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to update call status: {e}")
        return False


def get_calls_by_order(order_id: str) -> list[CallDocument]:
    """Get all calls for an order."""
    collection = get_collection(COLLECTION)
    if collection is None:
        return []
    
    try:
        cursor = collection.find({"order_id": order_id}).sort("created_at", 1)
        
        calls = []
        for doc in cursor:
            doc.pop("_id", None)
            calls.append(CallDocument(**doc))
        
        return calls
    except Exception as e:
        logger.error(f"Failed to get calls by order: {e}")
        return []


def create_call(
    call_id: str,
    order_id: str,
    vendor_id: str,
    vendor_name: str,
    vendor_phone: str
) -> Optional[CallDocument]:
    """
    Create a new call record.
    
    Args:
        call_id: Vapi call ID
        order_id: Associated order ID
        vendor_id: Vendor being called
        vendor_name: Vendor name
        vendor_phone: Phone number called
        
    Returns:
        Created CallDocument or None
    """
    call = CallDocument(
        call_id=call_id,
        order_id=order_id,
        vendor_id=vendor_id,
        vendor_name=vendor_name,
        vendor_phone=vendor_phone,
        status=CallStatus.INITIATED,
    )
    
    if save_call(call):
        return call
    return None


def get_successful_calls(order_id: str) -> list[CallDocument]:
    """Get calls that were confirmed for an order."""
    collection = get_collection(COLLECTION)
    if collection is None:
        return []
    
    try:
        cursor = collection.find({
            "order_id": order_id,
            "outcome.confirmed": True
        })
        
        calls = []
        for doc in cursor:
            doc.pop("_id", None)
            calls.append(CallDocument(**doc))
        
        return calls
    except Exception as e:
        logger.error(f"Failed to get successful calls: {e}")
        return []
