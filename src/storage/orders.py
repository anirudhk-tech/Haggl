"""Order storage operations."""

import logging
from datetime import datetime
from typing import Optional

from .database import get_collection
from .schemas import OrderDocument, OrderStatus

logger = logging.getLogger(__name__)

COLLECTION = "orders"


def save_order(order: OrderDocument) -> bool:
    """
    Save or update an order.
    
    Args:
        order: OrderDocument to save
        
    Returns:
        True if successful
    """
    collection = get_collection(COLLECTION)
    if collection is None:
        logger.warning("No database connection - order not saved")
        return False
    
    try:
        order.updated_at = datetime.utcnow()
        collection.update_one(
            {"order_id": order.order_id},
            {"$set": order.model_dump()},
            upsert=True
        )
        logger.info(f"Saved order: {order.order_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to save order: {e}")
        return False


def get_order(order_id: str) -> Optional[OrderDocument]:
    """Get an order by ID."""
    collection = get_collection(COLLECTION)
    if collection is None:
        return None
    
    try:
        doc = collection.find_one({"order_id": order_id})
        if doc:
            doc.pop("_id", None)
            return OrderDocument(**doc)
        return None
    except Exception as e:
        logger.error(f"Failed to get order: {e}")
        return None


def update_order_status(
    order_id: str,
    status: OrderStatus,
    **kwargs
) -> bool:
    """
    Update order status and optional fields.
    
    Args:
        order_id: Order ID
        status: New status
        **kwargs: Additional fields to update (vendor_confirmed, confirmed_price, etc.)
        
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
            {"order_id": order_id},
            {"$set": update}
        )
        
        if result.modified_count > 0:
            logger.info(f"Updated order {order_id} -> {status.value}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to update order status: {e}")
        return False


def add_vendor_to_order(
    order_id: str,
    vendor_id: str,
    field: str = "vendors_called"
) -> bool:
    """
    Add a vendor to an order's vendor list.
    
    Args:
        order_id: Order ID
        vendor_id: Vendor ID to add
        field: Which list (vendors_sourced, vendors_called)
        
    Returns:
        True if successful
    """
    collection = get_collection(COLLECTION)
    if collection is None:
        return False
    
    try:
        collection.update_one(
            {"order_id": order_id},
            {
                "$addToSet": {field: vendor_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return True
    except Exception as e:
        logger.error(f"Failed to add vendor to order: {e}")
        return False


def get_orders_by_phone(
    phone_number: str,
    limit: int = 10,
    status: Optional[OrderStatus] = None
) -> list[OrderDocument]:
    """
    Get orders for a phone number.
    
    Args:
        phone_number: Customer phone number
        limit: Max orders to return
        status: Optional status filter
        
    Returns:
        List of OrderDocuments (newest first)
    """
    collection = get_collection(COLLECTION)
    if collection is None:
        return []
    
    try:
        query = {"phone_number": phone_number}
        if status:
            query["status"] = status.value
        
        cursor = collection.find(query).sort("created_at", -1).limit(limit)
        
        orders = []
        for doc in cursor:
            doc.pop("_id", None)
            orders.append(OrderDocument(**doc))
        
        return orders
    except Exception as e:
        logger.error(f"Failed to get orders by phone: {e}")
        return []


def create_order(
    order_id: str,
    phone_number: str,
    product: str,
    quantity: float,
    unit: str
) -> Optional[OrderDocument]:
    """
    Create a new order.
    
    Args:
        order_id: Unique order ID
        phone_number: Customer phone
        product: Product being ordered
        quantity: Amount
        unit: Unit of measurement
        
    Returns:
        Created OrderDocument or None
    """
    order = OrderDocument(
        order_id=order_id,
        phone_number=phone_number,
        product=product,
        quantity=quantity,
        unit=unit,
        status=OrderStatus.PENDING,
    )
    
    if save_order(order):
        return order
    return None
