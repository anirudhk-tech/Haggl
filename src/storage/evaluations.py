"""Evaluation storage operations."""

import logging
from datetime import datetime
from typing import Optional

from .database import get_collection
from .schemas import EvaluationDocument, EvaluationStatus, VendorCallResult

logger = logging.getLogger(__name__)

COLLECTION = "evaluations"


def save_evaluation(evaluation: EvaluationDocument) -> bool:
    """
    Save or update an evaluation document.
    
    Args:
        evaluation: EvaluationDocument to save
        
    Returns:
        True if successful
    """
    collection = get_collection(COLLECTION)
    if collection is None:
        logger.warning("No database connection - evaluation not saved")
        return False
    
    try:
        evaluation.updated_at = datetime.utcnow()
        collection.update_one(
            {"evaluation_id": evaluation.evaluation_id},
            {"$set": evaluation.model_dump()},
            upsert=True
        )
        logger.info(f"Saved evaluation: {evaluation.evaluation_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to save evaluation: {e}")
        return False


def get_evaluation(evaluation_id: str) -> Optional[EvaluationDocument]:
    """Get an evaluation by ID."""
    collection = get_collection(COLLECTION)
    if collection is None:
        return None
    
    try:
        doc = collection.find_one({"evaluation_id": evaluation_id})
        if doc:
            doc.pop("_id", None)
            return EvaluationDocument(**doc)
        return None
    except Exception as e:
        logger.error(f"Failed to get evaluation: {e}")
        return None


def get_evaluation_by_order(order_id: str) -> Optional[EvaluationDocument]:
    """Get evaluation for an order."""
    collection = get_collection(COLLECTION)
    if collection is None:
        return None
    
    try:
        doc = collection.find_one({"order_id": order_id})
        if doc:
            doc.pop("_id", None)
            return EvaluationDocument(**doc)
        return None
    except Exception as e:
        logger.error(f"Failed to get evaluation by order: {e}")
        return None


def update_evaluation_status(
    evaluation_id: str,
    status: EvaluationStatus,
    **kwargs
) -> bool:
    """
    Update evaluation status and optional fields.
    
    Args:
        evaluation_id: Evaluation ID
        status: New status
        **kwargs: Additional fields (selected_vendor_id, selection_reason, etc.)
        
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
            **kwargs
        }
        
        result = collection.update_one(
            {"evaluation_id": evaluation_id},
            {"$set": update}
        )
        
        if result.modified_count > 0:
            logger.info(f"Updated evaluation {evaluation_id} -> {status.value}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to update evaluation status: {e}")
        return False


def create_evaluation(
    evaluation_id: str,
    order_id: str,
    vendor_results: list[VendorCallResult]
) -> Optional[EvaluationDocument]:
    """
    Create a new evaluation document.
    
    Args:
        evaluation_id: Unique evaluation ID
        order_id: Associated order ID
        vendor_results: List of vendor call results
        
    Returns:
        Created EvaluationDocument or None
    """
    evaluation = EvaluationDocument(
        evaluation_id=evaluation_id,
        order_id=order_id,
        vendor_results=vendor_results,
        status=EvaluationStatus.PENDING,
    )
    
    if save_evaluation(evaluation):
        return evaluation
    return None
