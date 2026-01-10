"""Payment Executor - Mock Stripe/ACH execution for demos.

This module simulates payment execution through:
- Mock Stripe card payments
- Mock Stripe ACH (bank transfer)
- Mock direct ACH

In production, this would use real Stripe SDK or Computer Use
to navigate vendor payment portals.
"""

import os
import logging
import secrets
import asyncio
from typing import Optional
from datetime import datetime, timedelta

from .schemas import (
    PaymentMethod,
    PaymentRequest,
    PaymentResult,
    PaymentStatus,
    MockStripePayment,
    MockACHPayment,
)

logger = logging.getLogger(__name__)


class PaymentExecutor:
    """
    Mock Payment Executor for hackathon demos.
    
    Simulates the legacy execution layer that would:
    - Process Stripe payments (card or ACH)
    - Navigate vendor portals via Computer Use
    - Inject ACH credentials securely
    
    For demos, this returns realistic-looking mock responses.
    """
    
    def __init__(self, simulate_delays: bool = True):
        self.simulate_delays = simulate_delays
        self._payment_history: dict[str, PaymentResult] = {}
        
        # Mock ACH credentials (would be in secure vault in production)
        self._mock_ach = {
            "routing": os.getenv("ACH_ROUTING_NUMBER", "021000021"),
            "account": os.getenv("ACH_ACCOUNT_NUMBER", "1234567890"),
            "name": os.getenv("ACH_ACCOUNT_NAME", "Haggl Demo Business"),
        }
    
    async def execute_payment(
        self,
        request: PaymentRequest,
        x402_tx_hash: Optional[str] = None
    ) -> PaymentResult:
        """
        Execute a payment using the specified method.
        
        Requires a valid x402 auth token (verified by authorizer).
        """
        start_time = datetime.utcnow()
        
        logger.info(f"💳 Executing payment for invoice {request.invoice_id}")
        logger.info(f"   Method: {request.payment_method.value}")
        logger.info(f"   Amount: ${request.amount_usd}")
        logger.info(f"   Vendor: {request.vendor_name}")
        
        # Simulate processing delay
        if self.simulate_delays:
            await asyncio.sleep(0.5)  # 500ms processing
        
        try:
            if request.payment_method == PaymentMethod.MOCK_CARD:
                result = await self._execute_mock_card(request)
            elif request.payment_method == PaymentMethod.STRIPE_CARD:
                result = await self._execute_stripe_card(request)
            elif request.payment_method in (PaymentMethod.MOCK_ACH, PaymentMethod.STRIPE_ACH):
                result = await self._execute_ach(request)
            elif request.payment_method == PaymentMethod.BROWSERBASE_ACH:
                result = await self._execute_browserbase_ach(request)
            else:
                result = PaymentResult(
                    invoice_id=request.invoice_id,
                    status=PaymentStatus.FAILED,
                    payment_method=request.payment_method,
                    amount_usd=request.amount_usd,
                    error=f"Unsupported payment method: {request.payment_method}"
                )
            
            # Add x402 reference
            result.x402_tx_hash = x402_tx_hash
            
            # Calculate processing time
            end_time = datetime.utcnow()
            result.processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Cache result
            self._payment_history[request.invoice_id] = result
            
            if result.status == PaymentStatus.SUCCEEDED:
                logger.info(f"✅ Payment succeeded: {result.confirmation_number}")
            else:
                logger.warning(f"❌ Payment failed: {result.error}")
            
            return result
            
        except Exception as e:
            logger.exception(f"Payment execution error: {e}")
            return PaymentResult(
                invoice_id=request.invoice_id,
                status=PaymentStatus.FAILED,
                payment_method=request.payment_method,
                amount_usd=request.amount_usd,
                error=str(e),
                retry_eligible=True
            )
    
    async def _execute_mock_card(self, request: PaymentRequest) -> PaymentResult:
        """Execute a mock card payment (simulates Stripe)."""
        
        # Generate mock Stripe-like IDs
        payment_intent_id = f"pi_{secrets.token_hex(12)}"
        confirmation = f"ch_{secrets.token_hex(12)}"
        
        # Simulate Stripe PaymentIntent
        stripe_payment = MockStripePayment(
            payment_intent_id=payment_intent_id,
            client_secret=f"{payment_intent_id}_secret_{secrets.token_hex(12)}",
            amount=int(request.amount_usd * 100),  # Stripe uses cents
            currency="usd",
            status="succeeded",
            payment_method_type="card"
        )
        
        return PaymentResult(
            invoice_id=request.invoice_id,
            status=PaymentStatus.SUCCEEDED,
            payment_method=PaymentMethod.MOCK_CARD,
            amount_usd=request.amount_usd,
            stripe_payment=stripe_payment,
            confirmation_number=confirmation,
            receipt_url=f"https://pay.stripe.com/receipts/{confirmation}"
        )
    
    async def _execute_stripe_card(self, request: PaymentRequest) -> PaymentResult:
        """
        Execute a Stripe card payment.
        
        In production, this would use the Stripe SDK:
        ```python
        import stripe
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        
        payment_intent = stripe.PaymentIntent.create(
            amount=int(request.amount_usd * 100),
            currency="usd",
            payment_method_types=["card"],
            metadata={"invoice_id": request.invoice_id}
        )
        ```
        
        For demo, we return mock data.
        """
        # For hackathon, use mock implementation
        return await self._execute_mock_card(request)
    
    async def _execute_ach(self, request: PaymentRequest) -> PaymentResult:
        """
        Execute an ACH bank transfer.
        
        In production with Stripe ACH:
        ```python
        payment_intent = stripe.PaymentIntent.create(
            amount=int(request.amount_usd * 100),
            currency="usd",
            payment_method_types=["us_bank_account"],
            payment_method_data={
                "type": "us_bank_account",
                "us_bank_account": {
                    "account_holder_type": "company",
                    "account_number": self._ach_account,  # From secure vault
                    "routing_number": self._ach_routing,
                }
            }
        )
        ```
        
        Or with Computer Use (browser automation):
        1. Navigate to vendor payment portal
        2. Select ACH payment option
        3. Inject credentials from secure vault (AI never sees values)
        4. Submit and capture confirmation
        
        For demo, we simulate this flow.
        """
        
        # Simulate ACH processing delay (ACH is slower than cards)
        if self.simulate_delays:
            await asyncio.sleep(1.0)  # Simulate bank verification
        
        # Generate mock ACH transfer
        transfer_id = f"ach_{secrets.token_hex(8)}"
        estimated_arrival = (datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%d")
        
        ach_payment = MockACHPayment(
            ach_transfer_id=transfer_id,
            routing_number_last4=self._mock_ach["routing"][-4:],
            account_number_last4=self._mock_ach["account"][-4:],
            bank_name="Chase Bank",  # Mock bank name
            status="pending",  # ACH starts as pending
            estimated_arrival=estimated_arrival
        )
        
        confirmation = f"ACH-{request.invoice_id}-{secrets.token_hex(4).upper()}"
        
        logger.info(f"🏦 ACH Transfer initiated")
        logger.info(f"   Transfer ID: {transfer_id}")
        logger.info(f"   Bank: {ach_payment.bank_name}")
        logger.info(f"   Account: ****{ach_payment.account_number_last4}")
        logger.info(f"   Estimated arrival: {estimated_arrival}")
        
        return PaymentResult(
            invoice_id=request.invoice_id,
            status=PaymentStatus.PROCESSING,  # ACH takes time
            payment_method=request.payment_method,
            amount_usd=request.amount_usd,
            ach_payment=ach_payment,
            confirmation_number=confirmation,
            receipt_url=None  # ACH doesn't have instant receipts
        )
    
    async def _execute_browserbase_ach(self, request: PaymentRequest) -> PaymentResult:
        """
        Execute ACH payment via Browserbase x402 browser automation.
        
        This uses real cloud browsers (paid with USDC) to navigate
        vendor payment portals like Intuit QuickBooks.
        """
        from .browserbase import pay_intuit_invoice
        
        logger.info("🌐 Executing via Browserbase x402...")
        
        # For demo, use mock mode if no Browserbase credentials
        mock_mode = not os.getenv("BROWSERBASE_PROJECT_ID")
        
        # Get the payment URL (would come from invoice in production)
        payment_url = getattr(request, 'payment_url', None)
        
        if not payment_url:
            # For demo without URL, fall back to mock ACH
            logger.info("No payment URL provided, using mock ACH flow")
            return await self._execute_ach(request)
        
        try:
            result = await pay_intuit_invoice(
                invoice_url=payment_url,
                auth_token=request.auth_token,
                mock_mode=mock_mode
            )
            
            if result["status"] == "succeeded":
                return PaymentResult(
                    invoice_id=request.invoice_id,
                    status=PaymentStatus.SUCCEEDED,
                    payment_method=PaymentMethod.BROWSERBASE_ACH,
                    amount_usd=request.amount_usd,
                    confirmation_number=result.get("confirmation"),
                    ach_payment=MockACHPayment(
                        ach_transfer_id=result.get("confirmation", "BB_TRANSFER"),
                        routing_number_last4=self._mock_ach["routing"][-4:],
                        account_number_last4=self._mock_ach["account"][-4:],
                        bank_name="Via Browserbase",
                        status="succeeded",
                        estimated_arrival="Instant"
                    )
                )
            else:
                return PaymentResult(
                    invoice_id=request.invoice_id,
                    status=PaymentStatus.FAILED,
                    payment_method=PaymentMethod.BROWSERBASE_ACH,
                    amount_usd=request.amount_usd,
                    error=result.get("error", "Browserbase execution failed"),
                    retry_eligible=True
                )
                
        except Exception as e:
            logger.exception(f"Browserbase execution error: {e}")
            return PaymentResult(
                invoice_id=request.invoice_id,
                status=PaymentStatus.FAILED,
                payment_method=PaymentMethod.BROWSERBASE_ACH,
                amount_usd=request.amount_usd,
                error=str(e),
                retry_eligible=True
            )
    
    def get_payment_status(self, invoice_id: str) -> Optional[PaymentResult]:
        """Get the status of a payment by invoice ID."""
        return self._payment_history.get(invoice_id)
    
    def get_all_payments(self) -> list[PaymentResult]:
        """Get all payment results."""
        return list(self._payment_history.values())
    
    def reset(self):
        """Reset payment history (for testing)."""
        self._payment_history.clear()


# Global executor instance
_executor: Optional[PaymentExecutor] = None


def get_executor(simulate_delays: bool = True) -> PaymentExecutor:
    """Get or create the global executor instance."""
    global _executor
    if _executor is None:
        _executor = PaymentExecutor(simulate_delays=simulate_delays)
    return _executor
