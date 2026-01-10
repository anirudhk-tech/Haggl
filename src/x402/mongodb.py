"""
MongoDB Atlas Setup and Connection for Haggl x402.

Collections:
- credentials: Encrypted ACH credentials
- escrow_locks: Active escrow records
- escrow_releases: Completed releases
- authorizations: x402 authorization records
- payments: Payment execution records
- audit_log: Security audit trail
"""

import os
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# MongoDB configuration
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "haggl")

# Connection pool
_client = None
_db = None


def get_mongodb_client():
    """Get or create MongoDB client."""
    global _client
    
    if _client is not None:
        return _client
    
    if not MONGODB_URI:
        logger.warning("MONGODB_URI not set - using mock mode")
        return None
    
    try:
        from pymongo import MongoClient
        _client = MongoClient(MONGODB_URI)
        # Test connection
        _client.admin.command('ping')
        logger.info("Connected to MongoDB Atlas")
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


def setup_indexes():
    """Create indexes for all collections."""
    db = get_database()
    if db is None:
        logger.warning("Cannot setup indexes - no database connection")
        return False
    
    try:
        # Credentials collection
        db.credentials.create_index("business_id", unique=True)
        db.credentials.create_index("credential_id", unique=True)
        
        # Escrow locks
        db.escrow_locks.create_index("escrow_id", unique=True)
        db.escrow_locks.create_index("invoice_id")
        db.escrow_locks.create_index("business_id")
        db.escrow_locks.create_index("status")
        db.escrow_locks.create_index("expires_at")
        
        # Escrow releases
        db.escrow_releases.create_index("release_id", unique=True)
        db.escrow_releases.create_index("escrow_id")
        db.escrow_releases.create_index("invoice_id")
        
        # Authorizations
        db.authorizations.create_index("request_id", unique=True)
        db.authorizations.create_index("invoice_id")
        db.authorizations.create_index("status")
        db.authorizations.create_index("timestamp")
        
        # Payments
        db.payments.create_index("payment_id", unique=True)
        db.payments.create_index("invoice_id")
        db.payments.create_index("status")
        
        # Audit log
        db.audit_log.create_index("timestamp")
        db.audit_log.create_index("business_id")
        db.audit_log.create_index("action")
        
        logger.info("MongoDB indexes created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        return False


def log_audit_event(
    action: str,
    business_id: Optional[str] = None,
    invoice_id: Optional[str] = None,
    details: Optional[dict] = None,
    severity: str = "info"
):
    """Log an audit event to MongoDB."""
    db = get_database()
    
    event = {
        "action": action,
        "business_id": business_id,
        "invoice_id": invoice_id,
        "details": details or {},
        "severity": severity,
        "timestamp": datetime.utcnow(),
    }
    
    if db is not None:
        try:
            db.audit_log.insert_one(event)
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
    
    # Also log to standard logger
    log_msg = f"[AUDIT] {action}"
    if business_id:
        log_msg += f" | business={business_id}"
    if invoice_id:
        log_msg += f" | invoice={invoice_id}"
    
    if severity == "error":
        logger.error(log_msg)
    elif severity == "warning":
        logger.warning(log_msg)
    else:
        logger.info(log_msg)


def get_collection_stats() -> dict:
    """Get statistics for all collections."""
    db = get_database()
    
    if db is None:
        return {"error": "No database connection"}
    
    try:
        return {
            "credentials": db.credentials.count_documents({}),
            "escrow_locks": db.escrow_locks.count_documents({}),
            "escrow_releases": db.escrow_releases.count_documents({}),
            "authorizations": db.authorizations.count_documents({}),
            "payments": db.payments.count_documents({}),
            "audit_log": db.audit_log.count_documents({}),
        }
    except Exception as e:
        return {"error": str(e)}


def close_connection():
    """Close MongoDB connection."""
    global _client, _db
    
    if _client is not None:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB connection closed")


# Initialize on import if URI is set
if MONGODB_URI:
    get_mongodb_client()
