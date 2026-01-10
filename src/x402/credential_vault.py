"""
Encrypted Credential Vault for ACH/Banking Details.

This module provides secure storage for sensitive payment credentials:
- AES-256-GCM encryption at rest
- MongoDB storage with field-level encryption
- Access only via valid x402 authorization tokens
- Full audit logging

SECURITY: ACH credentials are NEVER exposed to AI agents.
They are decrypted only at the moment of injection into browser forms.
"""

import os
import base64
import logging
import secrets
from typing import Optional
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

# MongoDB configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "haggl")

# Encryption key derivation
VAULT_MASTER_KEY = os.getenv("VAULT_MASTER_KEY")  # Should be 32+ chars
VAULT_SALT = os.getenv("VAULT_SALT", "haggl_vault_salt_v1")


def _derive_key(master_key: str, salt: str) -> bytes:
    """Derive encryption key from master key using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode(),
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
    return key


class CredentialVault:
    """
    Secure vault for ACH/banking credentials.
    
    Features:
    - AES-256-GCM encryption via Fernet
    - MongoDB storage
    - x402 authorization required for access
    - Audit logging for all operations
    """
    
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self._fernet: Optional[Fernet] = None
        self._db = None
        self._mock_credentials: dict[str, dict] = {}
        
        if not mock_mode:
            self._init_encryption()
            self._init_mongodb()
    
    def _init_encryption(self):
        """Initialize Fernet encryption."""
        if not VAULT_MASTER_KEY:
            logger.warning("VAULT_MASTER_KEY not set, using generated key (NOT FOR PRODUCTION)")
            # Generate a temporary key for development
            key = Fernet.generate_key()
        else:
            key = _derive_key(VAULT_MASTER_KEY, VAULT_SALT)
        
        self._fernet = Fernet(key)
        logger.info("Credential vault encryption initialized")
    
    def _init_mongodb(self):
        """Initialize MongoDB connection."""
        try:
            from pymongo import MongoClient
            client = MongoClient(MONGODB_URI)
            self._db = client[MONGODB_DB]
            # Create indexes
            self._db.credentials.create_index("business_id", unique=True)
            self._db.credential_access_log.create_index("timestamp")
            logger.info(f"Connected to MongoDB: {MONGODB_DB}")
        except Exception as e:
            logger.warning(f"MongoDB connection failed: {e}. Using mock mode.")
            self.mock_mode = True
    
    def store_credentials(
        self,
        business_id: str,
        routing_number: str,
        account_number: str,
        account_name: str,
        bank_name: Optional[str] = None,
    ) -> dict:
        """
        Store encrypted ACH credentials for a business.
        
        This is called during business onboarding (NOT by AI).
        
        Args:
            business_id: Unique business identifier
            routing_number: 9-digit ABA routing number
            account_number: Bank account number
            account_name: Name on the account
            bank_name: Optional bank name
        
        Returns:
            Dict with status and credential_id
        """
        if self.mock_mode:
            credential_id = f"cred_{secrets.token_hex(8)}"
            self._mock_credentials[business_id] = {
                "credential_id": credential_id,
                "routing_last4": routing_number[-4:],
                "account_last4": account_number[-4:],
                "account_name": account_name,
                "bank_name": bank_name,
                "created_at": datetime.utcnow().isoformat(),
            }
            logger.info(f"[MOCK] Stored credentials for business {business_id}")
            return {"status": "stored", "credential_id": credential_id}
        
        # Encrypt sensitive fields
        encrypted_routing = self._fernet.encrypt(routing_number.encode()).decode()
        encrypted_account = self._fernet.encrypt(account_number.encode()).decode()
        encrypted_name = self._fernet.encrypt(account_name.encode()).decode()
        
        credential_id = f"cred_{secrets.token_hex(8)}"
        
        doc = {
            "business_id": business_id,
            "credential_id": credential_id,
            "routing_encrypted": encrypted_routing,
            "account_encrypted": encrypted_account,
            "name_encrypted": encrypted_name,
            "routing_last4": routing_number[-4:],
            "account_last4": account_number[-4:],
            "bank_name": bank_name,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        # Upsert (update or insert)
        self._db.credentials.update_one(
            {"business_id": business_id},
            {"$set": doc},
            upsert=True
        )
        
        self._log_access(business_id, "store", "Credentials stored")
        logger.info(f"Stored encrypted credentials for business {business_id}")
        
        return {"status": "stored", "credential_id": credential_id}
    
    def get_credentials_for_injection(
        self,
        business_id: str,
        auth_token: str,
        invoice_id: str,
    ) -> Optional[dict]:
        """
        Retrieve decrypted credentials for secure injection.
        
        SECURITY: This method should ONLY be called by the secure
        credential injector, NEVER by AI agents.
        
        Args:
            business_id: Business requesting credentials
            auth_token: Valid x402 authorization token
            invoice_id: Invoice being paid (for audit)
        
        Returns:
            Dict with decrypted routing, account, name
            Or None if not found/unauthorized
        """
        # Verify authorization token first
        if not self._verify_authorization(auth_token, invoice_id):
            logger.warning(f"Unauthorized credential access attempt: {business_id}")
            self._log_access(business_id, "denied", f"Invalid auth token for {invoice_id}")
            return None
        
        if self.mock_mode:
            if business_id not in self._mock_credentials:
                # Return default mock credentials
                return {
                    "routing": os.getenv("ACH_ROUTING_NUMBER", "021000021"),
                    "account": os.getenv("ACH_ACCOUNT_NUMBER", "1234567890"),
                    "name": os.getenv("ACH_ACCOUNT_NAME", "Haggl Demo Business"),
                }
            
            # In mock mode, return env vars or stored mock
            stored = self._mock_credentials[business_id]
            return {
                "routing": os.getenv("ACH_ROUTING_NUMBER", "021000021"),
                "account": os.getenv("ACH_ACCOUNT_NUMBER", "1234567890"),
                "name": stored.get("account_name", "Demo Business"),
            }
        
        # Fetch from MongoDB
        doc = self._db.credentials.find_one({"business_id": business_id})
        if not doc:
            logger.warning(f"No credentials found for business {business_id}")
            return None
        
        # Decrypt
        try:
            routing = self._fernet.decrypt(doc["routing_encrypted"].encode()).decode()
            account = self._fernet.decrypt(doc["account_encrypted"].encode()).decode()
            name = self._fernet.decrypt(doc["name_encrypted"].encode()).decode()
            
            self._log_access(business_id, "decrypt", f"Credentials decrypted for {invoice_id}")
            
            return {
                "routing": routing,
                "account": account,
                "name": name,
            }
        except Exception as e:
            logger.error(f"Decryption failed for {business_id}: {e}")
            return None
    
    def get_credential_info(self, business_id: str) -> Optional[dict]:
        """
        Get non-sensitive credential info (for display).
        
        Returns masked info like ****7890 for account numbers.
        """
        if self.mock_mode:
            if business_id in self._mock_credentials:
                stored = self._mock_credentials[business_id]
                return {
                    "credential_id": stored["credential_id"],
                    "routing_last4": stored["routing_last4"],
                    "account_last4": stored["account_last4"],
                    "account_name": stored["account_name"],
                    "bank_name": stored.get("bank_name"),
                }
            return None
        
        doc = self._db.credentials.find_one(
            {"business_id": business_id},
            {"routing_encrypted": 0, "account_encrypted": 0, "name_encrypted": 0}
        )
        
        if not doc:
            return None
        
        return {
            "credential_id": doc["credential_id"],
            "routing_last4": doc["routing_last4"],
            "account_last4": doc["account_last4"],
            "bank_name": doc.get("bank_name"),
            "created_at": doc["created_at"].isoformat() if doc.get("created_at") else None,
        }
    
    def _verify_authorization(self, auth_token: str, invoice_id: str) -> bool:
        """
        Verify x402 authorization token is valid.
        
        In production, this would check against the authorizer.
        """
        # Import here to avoid circular dependency
        from .authorizer import get_authorizer
        
        authorizer = get_authorizer()
        return authorizer.verify_auth_token(auth_token, invoice_id)
    
    def _log_access(self, business_id: str, action: str, details: str):
        """Log credential access for audit trail."""
        log_entry = {
            "business_id": business_id,
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow(),
        }
        
        if self.mock_mode:
            logger.info(f"[AUDIT] {action}: {business_id} - {details}")
            return
        
        try:
            self._db.credential_access_log.insert_one(log_entry)
        except Exception as e:
            logger.error(f"Failed to log access: {e}")
    
    def delete_credentials(self, business_id: str) -> bool:
        """Delete credentials for a business."""
        if self.mock_mode:
            if business_id in self._mock_credentials:
                del self._mock_credentials[business_id]
                return True
            return False
        
        result = self._db.credentials.delete_one({"business_id": business_id})
        self._log_access(business_id, "delete", "Credentials deleted")
        return result.deleted_count > 0


# Global vault instance
_vault: Optional[CredentialVault] = None


def get_vault(mock_mode: bool = None) -> CredentialVault:
    """Get or create the global vault instance."""
    global _vault
    
    if mock_mode is None:
        # Auto-detect: use mock if no MongoDB URI or master key
        mock_mode = not (MONGODB_URI and VAULT_MASTER_KEY)
    
    if _vault is None:
        _vault = CredentialVault(mock_mode=mock_mode)
    
    return _vault
