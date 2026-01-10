"""
Escrow Management for x402 Payments.

Handles the lifecycle of escrowed USDC:
1. Lock: USDC transferred to escrow during authorization
2. Release: USDC released to vendor after successful payment
3. Refund: USDC returned to user if payment fails

MongoDB collections:
- escrow_locks: Active escrow records
- escrow_releases: Completed releases
- escrow_refunds: Refunded amounts
"""

import os
import logging
import secrets
from typing import Optional
from datetime import datetime, timedelta
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# MongoDB configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "haggl")


class EscrowStatus(str, Enum):
    """Status of an escrow lock."""
    LOCKED = "locked"
    RELEASED = "released"
    REFUNDED = "refunded"
    EXPIRED = "expired"


class EscrowLock(BaseModel):
    """Record of USDC locked in escrow."""
    escrow_id: str = Field(description="Unique escrow identifier")
    invoice_id: str = Field(description="Associated invoice")
    business_id: str = Field(description="Business that authorized")
    vendor_id: Optional[str] = Field(default=None, description="Vendor to receive funds")
    amount_usdc: float = Field(description="Amount locked")
    
    # x402 authorization reference
    auth_token: str = Field(description="x402 auth token used")
    tx_hash: str = Field(description="On-chain lock transaction")
    
    # Status tracking
    status: EscrowStatus = Field(default=EscrowStatus.LOCKED)
    locked_at: str = Field(description="When funds were locked")
    expires_at: str = Field(description="When lock expires if not released")
    
    # Release/refund info
    released_at: Optional[str] = None
    release_tx_hash: Optional[str] = None
    release_recipient: Optional[str] = None
    refund_reason: Optional[str] = None


class EscrowRelease(BaseModel):
    """Record of escrow release to vendor."""
    release_id: str
    escrow_id: str
    invoice_id: str
    vendor_id: str
    vendor_wallet: Optional[str] = None  # If vendor accepts crypto
    vendor_bank_confirmed: bool = False  # If ACH was used
    amount_usdc: float
    tx_hash: str
    released_at: str
    ach_confirmation: Optional[str] = None


class EscrowManager:
    """
    Manages escrow lifecycle for x402 payments.
    
    Flow:
    1. Authorization creates escrow lock (USDC → escrow wallet)
    2. Payment execution confirms ACH success
    3. Release transfers USDC to vendor (or refunds to user)
    """
    
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self._db = None
        self._mock_escrows: dict[str, EscrowLock] = {}
        self._mock_releases: list[EscrowRelease] = []
        
        # Escrow wallet address (would be real CDP wallet in production)
        self.escrow_wallet = os.getenv("ESCROW_WALLET_ADDRESS", "0xEscrowWallet...")
        
        if not mock_mode:
            self._init_mongodb()
    
    def _init_mongodb(self):
        """Initialize MongoDB connection."""
        try:
            from pymongo import MongoClient
            client = MongoClient(MONGODB_URI)
            self._db = client[MONGODB_DB]
            # Create indexes
            self._db.escrow_locks.create_index("escrow_id", unique=True)
            self._db.escrow_locks.create_index("invoice_id")
            self._db.escrow_locks.create_index("status")
            self._db.escrow_releases.create_index("release_id", unique=True)
            logger.info("Escrow manager connected to MongoDB")
        except Exception as e:
            logger.warning(f"MongoDB connection failed: {e}. Using mock mode.")
            self.mock_mode = True
    
    def create_lock(
        self,
        invoice_id: str,
        business_id: str,
        amount_usdc: float,
        auth_token: str,
        tx_hash: str,
        vendor_id: Optional[str] = None,
        expiry_hours: int = 72,
    ) -> EscrowLock:
        """
        Create an escrow lock when x402 authorization is granted.
        
        Args:
            invoice_id: Invoice being paid
            business_id: Business authorizing payment
            amount_usdc: Amount to lock
            auth_token: x402 authorization token
            tx_hash: On-chain transaction hash
            vendor_id: Vendor to receive funds
            expiry_hours: Hours until lock expires
        
        Returns:
            EscrowLock record
        """
        escrow_id = f"escrow_{secrets.token_hex(8)}"
        now = datetime.utcnow()
        expires = now + timedelta(hours=expiry_hours)
        
        lock = EscrowLock(
            escrow_id=escrow_id,
            invoice_id=invoice_id,
            business_id=business_id,
            vendor_id=vendor_id,
            amount_usdc=amount_usdc,
            auth_token=auth_token,
            tx_hash=tx_hash,
            status=EscrowStatus.LOCKED,
            locked_at=now.isoformat(),
            expires_at=expires.isoformat(),
        )
        
        if self.mock_mode:
            self._mock_escrows[escrow_id] = lock
            logger.info(f"[MOCK] Created escrow lock: {escrow_id} for ${amount_usdc}")
        else:
            self._db.escrow_locks.insert_one(lock.model_dump())
            logger.info(f"Created escrow lock: {escrow_id} for ${amount_usdc}")
        
        return lock
    
    def release_to_vendor(
        self,
        escrow_id: str,
        vendor_id: str,
        vendor_wallet: Optional[str] = None,
        ach_confirmation: Optional[str] = None,
    ) -> Optional[EscrowRelease]:
        """
        Release escrowed funds to vendor after successful payment.
        
        This is called after ACH payment is confirmed.
        
        Args:
            escrow_id: Escrow to release
            vendor_id: Vendor receiving funds
            vendor_wallet: Vendor's crypto wallet (if they accept USDC)
            ach_confirmation: ACH confirmation number (if ACH was used)
        
        Returns:
            EscrowRelease record, or None if failed
        """
        # Get the escrow lock
        lock = self.get_lock(escrow_id)
        if not lock:
            logger.error(f"Escrow not found: {escrow_id}")
            return None
        
        if lock.status != EscrowStatus.LOCKED:
            logger.error(f"Escrow {escrow_id} is not locked (status: {lock.status})")
            return None
        
        # Create release record
        release_id = f"release_{secrets.token_hex(8)}"
        now = datetime.utcnow()
        
        # In production, this would trigger actual USDC transfer
        # For now, generate mock tx hash
        release_tx = f"0x{secrets.token_hex(32)}"
        
        release = EscrowRelease(
            release_id=release_id,
            escrow_id=escrow_id,
            invoice_id=lock.invoice_id,
            vendor_id=vendor_id,
            vendor_wallet=vendor_wallet,
            vendor_bank_confirmed=bool(ach_confirmation),
            amount_usdc=lock.amount_usdc,
            tx_hash=release_tx,
            released_at=now.isoformat(),
            ach_confirmation=ach_confirmation,
        )
        
        # Update escrow status
        lock.status = EscrowStatus.RELEASED
        lock.released_at = now.isoformat()
        lock.release_tx_hash = release_tx
        lock.release_recipient = vendor_wallet or f"ACH:{ach_confirmation}"
        
        if self.mock_mode:
            self._mock_escrows[escrow_id] = lock
            self._mock_releases.append(release)
            logger.info(f"[MOCK] Released escrow {escrow_id}: ${lock.amount_usdc} to {vendor_id}")
        else:
            self._db.escrow_locks.update_one(
                {"escrow_id": escrow_id},
                {"$set": lock.model_dump()}
            )
            self._db.escrow_releases.insert_one(release.model_dump())
            logger.info(f"Released escrow {escrow_id}: ${lock.amount_usdc} to {vendor_id}")
        
        return release
    
    def refund_to_business(
        self,
        escrow_id: str,
        reason: str,
    ) -> bool:
        """
        Refund escrowed funds back to business.
        
        Called when payment fails or is cancelled.
        
        Args:
            escrow_id: Escrow to refund
            reason: Reason for refund
        
        Returns:
            True if refund successful
        """
        lock = self.get_lock(escrow_id)
        if not lock:
            logger.error(f"Escrow not found: {escrow_id}")
            return False
        
        if lock.status != EscrowStatus.LOCKED:
            logger.error(f"Escrow {escrow_id} cannot be refunded (status: {lock.status})")
            return False
        
        # Update status
        lock.status = EscrowStatus.REFUNDED
        lock.refund_reason = reason
        lock.released_at = datetime.utcnow().isoformat()
        
        if self.mock_mode:
            self._mock_escrows[escrow_id] = lock
            logger.info(f"[MOCK] Refunded escrow {escrow_id}: ${lock.amount_usdc} - {reason}")
        else:
            self._db.escrow_locks.update_one(
                {"escrow_id": escrow_id},
                {"$set": lock.model_dump()}
            )
            logger.info(f"Refunded escrow {escrow_id}: ${lock.amount_usdc} - {reason}")
        
        return True
    
    def get_lock(self, escrow_id: str) -> Optional[EscrowLock]:
        """Get an escrow lock by ID."""
        if self.mock_mode:
            return self._mock_escrows.get(escrow_id)
        
        doc = self._db.escrow_locks.find_one({"escrow_id": escrow_id})
        if doc:
            doc.pop("_id", None)
            return EscrowLock(**doc)
        return None
    
    def get_lock_by_invoice(self, invoice_id: str) -> Optional[EscrowLock]:
        """Get escrow lock for an invoice."""
        if self.mock_mode:
            for lock in self._mock_escrows.values():
                if lock.invoice_id == invoice_id:
                    return lock
            return None
        
        doc = self._db.escrow_locks.find_one({"invoice_id": invoice_id})
        if doc:
            doc.pop("_id", None)
            return EscrowLock(**doc)
        return None
    
    def get_business_escrows(self, business_id: str) -> list[EscrowLock]:
        """Get all escrows for a business."""
        if self.mock_mode:
            return [
                lock for lock in self._mock_escrows.values()
                if lock.business_id == business_id
            ]
        
        docs = self._db.escrow_locks.find({"business_id": business_id})
        locks = []
        for doc in docs:
            doc.pop("_id", None)
            locks.append(EscrowLock(**doc))
        return locks
    
    def expire_old_locks(self) -> int:
        """Expire locks that have passed their expiry time."""
        now = datetime.utcnow()
        expired_count = 0
        
        if self.mock_mode:
            for escrow_id, lock in list(self._mock_escrows.items()):
                if lock.status == EscrowStatus.LOCKED:
                    expires = datetime.fromisoformat(lock.expires_at)
                    if now > expires:
                        lock.status = EscrowStatus.EXPIRED
                        self._mock_escrows[escrow_id] = lock
                        expired_count += 1
        else:
            result = self._db.escrow_locks.update_many(
                {
                    "status": EscrowStatus.LOCKED.value,
                    "expires_at": {"$lt": now.isoformat()}
                },
                {"$set": {"status": EscrowStatus.EXPIRED.value}}
            )
            expired_count = result.modified_count
        
        if expired_count > 0:
            logger.info(f"Expired {expired_count} escrow locks")
        
        return expired_count
    
    def get_stats(self) -> dict:
        """Get escrow statistics."""
        if self.mock_mode:
            locks = list(self._mock_escrows.values())
            return {
                "total_locks": len(locks),
                "locked": sum(1 for l in locks if l.status == EscrowStatus.LOCKED),
                "released": sum(1 for l in locks if l.status == EscrowStatus.RELEASED),
                "refunded": sum(1 for l in locks if l.status == EscrowStatus.REFUNDED),
                "expired": sum(1 for l in locks if l.status == EscrowStatus.EXPIRED),
                "total_locked_usdc": sum(l.amount_usdc for l in locks if l.status == EscrowStatus.LOCKED),
                "total_released_usdc": sum(l.amount_usdc for l in locks if l.status == EscrowStatus.RELEASED),
            }
        
        pipeline = [
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "total_usdc": {"$sum": "$amount_usdc"}
            }}
        ]
        
        results = list(self._db.escrow_locks.aggregate(pipeline))
        stats = {
            "total_locks": 0,
            "locked": 0,
            "released": 0,
            "refunded": 0,
            "expired": 0,
            "total_locked_usdc": 0.0,
            "total_released_usdc": 0.0,
        }
        
        for r in results:
            status = r["_id"]
            stats["total_locks"] += r["count"]
            stats[status] = r["count"]
            if status == "locked":
                stats["total_locked_usdc"] = r["total_usdc"]
            elif status == "released":
                stats["total_released_usdc"] = r["total_usdc"]
        
        return stats


# Global escrow manager instance
_escrow_manager: Optional[EscrowManager] = None


def get_escrow_manager(mock_mode: bool = None) -> EscrowManager:
    """Get or create the global escrow manager instance."""
    global _escrow_manager
    
    if mock_mode is None:
        mock_mode = not MONGODB_URI or MONGODB_URI == "mongodb://localhost:27017"
    
    if _escrow_manager is None:
        _escrow_manager = EscrowManager(mock_mode=mock_mode)
    
    return _escrow_manager
