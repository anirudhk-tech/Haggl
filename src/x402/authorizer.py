"""x402 Authorization Layer.

This module implements the x402 protocol for authorizing payments.
x402 is NOT a payment processor - it's a cryptographic "permission slip"
that authorizes real-world actions with budget enforcement.
"""

import os
import logging
import secrets
import hashlib
from typing import Optional
from datetime import datetime, timedelta

from .schemas import (
    AuthorizationRequest,
    AuthorizationResponse,
    AuthorizationStatus,
    SpendingPolicy,
    Invoice,
    BudgetContext,
)
from .wallet import CDPWallet, get_wallet
from .escrow import EscrowManager, get_escrow_manager

logger = logging.getLogger(__name__)


class X402Authorizer:
    """
    x402 Authorization Layer for agent payments.
    
    Flow:
    1. Agent requests authorization for an invoice
    2. Authorizer checks spending policies
    3. If approved, transfers USDC to escrow (on-chain proof)
    4. Returns auth token that unlocks payment execution
    """
    
    def __init__(
        self,
        wallet: Optional[CDPWallet] = None,
        policy: Optional[SpendingPolicy] = None,
        escrow_manager: Optional[EscrowManager] = None
    ):
        self.wallet = wallet or get_wallet()
        self.policy = policy or SpendingPolicy()
        self.escrow = escrow_manager or get_escrow_manager()
        
        # In-memory storage (use MongoDB in production)
        self._authorizations: dict[str, AuthorizationResponse] = {}
        self._daily_spending: dict[str, float] = {}  # date -> amount
        self._weekly_spending: float = 0.0
        self._auth_tokens: dict[str, str] = {}  # token -> invoice_id
        self._token_to_escrow: dict[str, str] = {}  # auth_token -> escrow_id
    
    async def authorize(self, request: AuthorizationRequest) -> AuthorizationResponse:
        """
        Main authorization flow.
        
        Returns an authorization token if approved, which can be used
        to execute the payment through the legacy bridge (ACH/Stripe).
        """
        invoice = request.invoice
        request_id = request.request_id or secrets.token_urlsafe(16)
        
        logger.info(f"Processing authorization request: {request_id}")
        logger.info(f"  Invoice: {invoice.invoice_id}")
        logger.info(f"  Vendor: {invoice.vendor_name}")
        logger.info(f"  Amount: ${invoice.amount_usd}")
        
        # Step 1: Check spending policies
        policy_result = self._check_policies(invoice, request)
        
        if not policy_result["allowed"]:
            logger.warning(f"Authorization rejected: {policy_result['reason']}")
            return AuthorizationResponse(
                request_id=request_id,
                invoice_id=invoice.invoice_id,
                status=AuthorizationStatus.REJECTED,
                error=policy_result["reason"],
                policy_checks=policy_result["checks"]
            )
        
        # Step 2: Transfer to escrow (on-chain authorization proof)
        try:
            transfer_result = await self.wallet.transfer_to_escrow(
                amount_usdc=invoice.amount_usd,
                memo=f"AUTH:{invoice.invoice_id}"
            )
            
            if not transfer_result["success"]:
                return AuthorizationResponse(
                    request_id=request_id,
                    invoice_id=invoice.invoice_id,
                    status=AuthorizationStatus.REJECTED,
                    error=transfer_result.get("error", "Transfer failed"),
                    policy_checks=policy_result["checks"]
                )
            
        except Exception as e:
            logger.exception(f"Transfer failed: {e}")
            return AuthorizationResponse(
                request_id=request_id,
                invoice_id=invoice.invoice_id,
                status=AuthorizationStatus.REJECTED,
                error=str(e),
                policy_checks=policy_result["checks"]
            )
        
        # Step 3: Create escrow lock
        escrow_lock = self.escrow.create_lock(
            invoice_id=invoice.invoice_id,
            business_id=request.request_id or "default_business",
            amount_usdc=invoice.amount_usd,
            auth_token="pending",  # Will update after generating token
            tx_hash=transfer_result["tx_hash"],
            vendor_id=invoice.vendor_id,
        )
        
        # Step 4: Generate single-use auth token
        auth_token = self._generate_auth_token(invoice.invoice_id)
        
        # Link auth token to escrow
        self._token_to_escrow[auth_token] = escrow_lock.escrow_id
        
        # Step 5: Update spending tracking
        self._record_spending(invoice.amount_usd)
        
        # Step 6: Build response
        response = AuthorizationResponse(
            request_id=request_id,
            invoice_id=invoice.invoice_id,
            status=AuthorizationStatus.AUTHORIZED,
            auth_token=auth_token,
            tx_hash=transfer_result["tx_hash"],
            explorer_url=transfer_result["explorer_url"],
            amount_authorized=invoice.amount_usd,
            escrow_address=transfer_result["escrow_address"],
            policy_checks=policy_result["checks"]
        )
        
        # Cache authorization
        self._authorizations[request_id] = response
        
        logger.info(f"✅ Authorization granted: {request_id}")
        logger.info(f"   TX: {transfer_result['tx_hash']}")
        logger.info(f"   Explorer: {transfer_result['explorer_url']}")
        
        return response
    
    def _check_policies(
        self,
        invoice: Invoice,
        request: AuthorizationRequest
    ) -> dict:
        """Check all spending policies."""
        checks = {}
        amount = invoice.amount_usd
        
        # Check 1: Per-transaction limit
        checks["per_transaction"] = {
            "limit": self.policy.per_transaction_max,
            "amount": amount,
            "passed": amount <= self.policy.per_transaction_max
        }
        
        if not checks["per_transaction"]["passed"]:
            return {
                "allowed": False,
                "reason": f"Amount ${amount} exceeds per-transaction limit ${self.policy.per_transaction_max}",
                "checks": checks
            }
        
        # Check 2: Daily limit
        today = datetime.utcnow().strftime("%Y-%m-%d")
        today_spent = self._daily_spending.get(today, 0.0)
        checks["daily_limit"] = {
            "limit": self.policy.daily_limit,
            "spent_today": today_spent,
            "new_total": today_spent + amount,
            "passed": (today_spent + amount) <= self.policy.daily_limit
        }
        
        if not checks["daily_limit"]["passed"]:
            return {
                "allowed": False,
                "reason": f"Would exceed daily limit: ${today_spent + amount} > ${self.policy.daily_limit}",
                "checks": checks
            }
        
        # Check 3: Budget constraint
        checks["budget"] = {
            "total_budget": request.budget_total,
            "remaining": request.budget_remaining,
            "amount": amount,
            "passed": amount <= request.budget_remaining
        }
        
        if not checks["budget"]["passed"]:
            return {
                "allowed": False,
                "reason": f"Amount ${amount} exceeds remaining budget ${request.budget_remaining}",
                "checks": checks
            }
        
        # Check 4: Duplicate detection
        duplicate = any(
            auth.invoice_id == invoice.invoice_id and 
            auth.status == AuthorizationStatus.AUTHORIZED
            for auth in self._authorizations.values()
        )
        checks["duplicate"] = {
            "invoice_id": invoice.invoice_id,
            "passed": not duplicate
        }
        
        if not checks["duplicate"]["passed"]:
            return {
                "allowed": False,
                "reason": f"Duplicate authorization for invoice {invoice.invoice_id}",
                "checks": checks
            }
        
        return {
            "allowed": True,
            "reason": "All policy checks passed",
            "checks": checks
        }
    
    def _generate_auth_token(self, invoice_id: str) -> str:
        """Generate a single-use authorization token."""
        token = secrets.token_urlsafe(32)
        self._auth_tokens[token] = invoice_id
        return token
    
    def verify_auth_token(self, token: str, invoice_id: str) -> bool:
        """Verify an authorization token is valid for the given invoice."""
        stored_invoice_id = self._auth_tokens.get(token)
        return stored_invoice_id == invoice_id
    
    def consume_auth_token(self, token: str) -> Optional[str]:
        """
        Consume (invalidate) an auth token, returning the invoice_id.
        
        Tokens are single-use - once consumed, they cannot be reused.
        """
        return self._auth_tokens.pop(token, None)
    
    def _record_spending(self, amount: float):
        """Record spending for limit tracking."""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        self._daily_spending[today] = self._daily_spending.get(today, 0.0) + amount
        self._weekly_spending += amount
    
    def get_authorization(self, request_id: str) -> Optional[AuthorizationResponse]:
        """Get an authorization by request ID."""
        return self._authorizations.get(request_id)
    
    def get_spending_summary(self) -> dict:
        """Get current spending summary."""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        return {
            "today": self._daily_spending.get(today, 0.0),
            "daily_limit": self.policy.daily_limit,
            "daily_remaining": self.policy.daily_limit - self._daily_spending.get(today, 0.0),
            "weekly_total": self._weekly_spending,
            "weekly_limit": self.policy.weekly_limit,
            "weekly_remaining": self.policy.weekly_limit - self._weekly_spending
        }
    
    def release_escrow(
        self,
        auth_token: str,
        vendor_id: str,
        ach_confirmation: Optional[str] = None
    ) -> dict:
        """
        Release escrowed funds to vendor after successful payment.
        
        Args:
            auth_token: The authorization token used
            vendor_id: Vendor receiving funds
            ach_confirmation: ACH confirmation number if applicable
        
        Returns:
            Dict with release status
        """
        escrow_id = self._token_to_escrow.get(auth_token)
        if not escrow_id:
            return {"success": False, "error": "No escrow found for auth token"}
        
        release = self.escrow.release_to_vendor(
            escrow_id=escrow_id,
            vendor_id=vendor_id,
            ach_confirmation=ach_confirmation
        )
        
        if release:
            return {
                "success": True,
                "release_id": release.release_id,
                "amount": release.amount_usdc,
                "tx_hash": release.tx_hash
            }
        
        return {"success": False, "error": "Failed to release escrow"}
    
    def refund_escrow(self, auth_token: str, reason: str) -> dict:
        """
        Refund escrowed funds back to business.
        
        Args:
            auth_token: The authorization token
            reason: Reason for refund
        
        Returns:
            Dict with refund status
        """
        escrow_id = self._token_to_escrow.get(auth_token)
        if not escrow_id:
            return {"success": False, "error": "No escrow found for auth token"}
        
        success = self.escrow.refund_to_business(escrow_id, reason)
        return {"success": success, "reason": reason if success else "Refund failed"}
    
    def get_escrow_stats(self) -> dict:
        """Get escrow statistics."""
        return self.escrow.get_stats()
    
    def reset(self):
        """Reset all state (for testing)."""
        self._authorizations.clear()
        self._daily_spending.clear()
        self._weekly_spending = 0.0
        self._auth_tokens.clear()
        self._token_to_escrow.clear()


# Global authorizer instance
_authorizer: Optional[X402Authorizer] = None


def get_authorizer() -> X402Authorizer:
    """Get or create the global authorizer instance."""
    global _authorizer
    if _authorizer is None:
        _authorizer = X402Authorizer()
    return _authorizer
