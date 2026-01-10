"""MongoDB Atlas connection and database management."""

import os
import logging
from typing import Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

# MongoDB configuration from environment
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "haggl")

# Connection pool
_client = None
_db = None


def get_mongodb_client():
    """Get or create MongoDB client (singleton)."""
    global _client
    
    if _client is not None:
        return _client
    
    if not MONGODB_URI:
        logger.warning("MONGODB_URI not set - storage disabled")
        return None
    
    try:
        from pymongo import MongoClient
        _client = MongoClient(MONGODB_URI)
        # Test connection
        _client.admin.command('ping')
        logger.info(f"Connected to MongoDB Atlas: {MONGODB_DB}")
        return _client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return None


def get_database():
    """Get the Haggl database."""
    global _db
    
    if _db is not None:
        return _db
    
    client = get_mongodb_client()
    if client is None:
        return None
    
    _db = client[MONGODB_DB]
    return _db


def get_collection(name: str):
    """Get a collection by name."""
    db = get_database()
    if db is None:
        return None
    return db[name]


def setup_all_indexes():
    """Create indexes for all collections."""
    db = get_database()
    if db is None:
        logger.warning("Cannot setup indexes - no database connection")
        return False
    
    try:
        # Vendors collection
        db.vendors.create_index("vendor_id", unique=True)
        db.vendors.create_index("ingredient")
        db.vendors.create_index("name")
        db.vendors.create_index("location.state")
        db.vendors.create_index("created_at")
        
        # Vendor embeddings (for vector search)
        db.vendor_embeddings.create_index("vendor_id", unique=True)
        db.vendor_embeddings.create_index("ingredient")
        
        # Conversations
        db.conversations.create_index("phone_number", unique=True)
        db.conversations.create_index("updated_at")
        
        # Orders
        db.orders.create_index("order_id", unique=True)
        db.orders.create_index("phone_number")
        db.orders.create_index("status")
        db.orders.create_index("created_at")
        
        # Calls
        db.calls.create_index("call_id", unique=True)
        db.calls.create_index("order_id")
        db.calls.create_index("vendor_id")
        db.calls.create_index("status")
        db.calls.create_index("created_at")
        
        logger.info("MongoDB indexes created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        return False


def close_connection():
    """Close MongoDB connection."""
    global _client, _db
    
    if _client is not None:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB connection closed")


def is_connected() -> bool:
    """Check if MongoDB is connected."""
    return _client is not None and _db is not None


def get_stats() -> dict:
    """Get collection statistics."""
    db = get_database()
    if db is None:
        return {"connected": False}
    
    try:
        return {
            "connected": True,
            "database": MONGODB_DB,
            "vendors": db.vendors.count_documents({}),
            "vendor_embeddings": db.vendor_embeddings.count_documents({}),
            "conversations": db.conversations.count_documents({}),
            "orders": db.orders.count_documents({}),
            "calls": db.calls.count_documents({}),
        }
    except Exception as e:
        return {"connected": True, "error": str(e)}
