#!/usr/bin/env python3
"""
Haggl Full Payment Flow Demo

Demonstrates the complete x402 authorization and payment execution flow:
1. Store ACH credentials in encrypted vault
2. Authorize payment via x402 (creates escrow lock)
3. Execute payment via Browserbase (or mock)
4. Release escrow to vendor

Usage:
    python demo_full_flow.py [--real]

Options:
    --real    Use real Browserbase sessions (requires API key)
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import Haggl modules
from src.x402 import (
    get_authorizer,
    get_vault,
    get_escrow_manager,
    AuthorizationRequest,
    Invoice,
)
from src.payment_agent.browserbase import BrowserbaseClient, PaymentPortalAutomator
from src.payment_agent.executor import get_executor
from src.payment_agent.schemas import PaymentRequest, PaymentMethod


async def demo_full_flow(use_real_browser: bool = False):
    """Run the full payment flow demo."""
    
    print("\n" + "="*70)
    print("🚀 HAGGL x402 FULL PAYMENT FLOW DEMO")
    print("="*70)
    
    # Configuration
    business_id = "demo_business_001"
    vendor_name = "Acme Supplies Inc."
    invoice_id = f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    amount = 150.00
    budget_total = 1000.00
    budget_remaining = 500.00
    
    print(f"\n📋 Invoice Details:")
    print(f"   ID: {invoice_id}")
    print(f"   Vendor: {vendor_name}")
    print(f"   Amount: ${amount}")
    print(f"   Budget: ${budget_remaining} remaining of ${budget_total}")
    
    # ==========================================================================
    # Step 1: Store ACH Credentials in Encrypted Vault
    # ==========================================================================
    print("\n" + "-"*70)
    print("📦 STEP 1: Store ACH Credentials in Encrypted Vault")
    print("-"*70)
    
    vault = get_vault(mock_mode=True)  # Use mock for demo
    
    result = vault.store_credentials(
        business_id=business_id,
        routing_number="021000021",  # Chase test routing
        account_number="123456789012",
        account_name="Haggl Demo Business LLC",
        bank_name="Chase Bank"
    )
    
    print(f"   ✅ Credentials stored: {result['credential_id']}")
    
    # Verify we can get masked info
    info = vault.get_credential_info(business_id)
    print(f"   📄 Stored info: ****{info['routing_last4']} / ****{info['account_last4']}")
    
    # ==========================================================================
    # Step 2: x402 Authorization (Creates Escrow Lock)
    # ==========================================================================
    print("\n" + "-"*70)
    print("🔐 STEP 2: x402 Authorization (Creates Escrow Lock)")
    print("-"*70)
    
    authorizer = get_authorizer()
    
    invoice = Invoice(
        invoice_id=invoice_id,
        vendor_name=vendor_name,
        vendor_id="vendor_acme_001",
        amount_usd=amount,
        description="Office supplies - Q1 2026"
    )
    
    auth_request = AuthorizationRequest(
        invoice=invoice,
        budget_total=budget_total,
        budget_remaining=budget_remaining,
        request_id=business_id
    )
    
    auth_response = await authorizer.authorize(auth_request)
    
    if auth_response.status.value != "authorized":
        print(f"   ❌ Authorization failed: {auth_response.error}")
        return
    
    print(f"   ✅ Authorization granted!")
    print(f"   🔑 Auth Token: {auth_response.auth_token[:20]}...")
    print(f"   📜 TX Hash: {auth_response.tx_hash[:20]}...")
    print(f"   🏦 Escrow: {auth_response.escrow_address}")
    
    # Check escrow was created
    escrow_manager = get_escrow_manager()
    escrow = escrow_manager.get_lock_by_invoice(invoice_id)
    if escrow:
        print(f"   💰 Escrow Lock: {escrow.escrow_id}")
        print(f"   💵 Amount Locked: ${escrow.amount_usdc} USDC")
    
    # ==========================================================================
    # Step 3: Payment Execution
    # ==========================================================================
    print("\n" + "-"*70)
    print("💳 STEP 3: Payment Execution")
    print("-"*70)
    
    if use_real_browser:
        print("   🌐 Using REAL Browserbase session...")
        
        # For real browser, we'd navigate to the actual invoice URL
        # For demo, we'll use a test URL
        test_url = "https://connect.intuit.com/t/scs-v1-26297a3db4e7480aafeabb334abefac156cc685711ec4c7fb924a5173d9a44b4b84020803d524618846eb7c5280bb7f2"
        
        browser = BrowserbaseClient(mock_mode=False)
        automator = PaymentPortalAutomator(browser)
        
        payment_result = await automator.pay_invoice(
            invoice_url=test_url,
            business_id=business_id,
            auth_token=auth_response.auth_token,
            contact_email="orders@haggl.demo"
        )
        
        print(f"   Status: {payment_result['status']}")
        print(f"   Steps: {len(payment_result['steps'])} completed")
        if payment_result.get('parsed_invoice'):
            parsed = payment_result['parsed_invoice']
            print(f"   Parsed: {parsed.get('vendor_name')} - ${parsed.get('amount')}")
        if payment_result.get('confirmation'):
            print(f"   Confirmation: {payment_result['confirmation']}")
    else:
        print("   🎭 Using MOCK payment execution...")
        
        executor = get_executor()
        payment_request = PaymentRequest(
            auth_token=auth_response.auth_token,
            invoice_id=invoice_id,
            amount_usd=amount,
            vendor_name=vendor_name,
            payment_method=PaymentMethod.MOCK_ACH
        )
        
        # Consume the auth token
        authorizer.consume_auth_token(auth_response.auth_token)
        
        payment_result = await executor.execute_payment(
            payment_request,
            x402_tx_hash=auth_response.tx_hash
        )
        
        print(f"   ✅ Payment Status: {payment_result.status.value}")
        print(f"   🏦 Method: {payment_result.payment_method.value}")
        if payment_result.ach_payment:
            print(f"   📝 ACH Transfer ID: {payment_result.ach_payment.ach_transfer_id}")
            print(f"   🏦 Bank: {payment_result.ach_payment.bank_name}")
        if payment_result.confirmation_number:
            print(f"   📋 Confirmation: {payment_result.confirmation_number}")
    
    # ==========================================================================
    # Step 4: Release Escrow to Vendor
    # ==========================================================================
    print("\n" + "-"*70)
    print("🔓 STEP 4: Release Escrow to Vendor")
    print("-"*70)
    
    # Get the escrow lock
    escrow = escrow_manager.get_lock_by_invoice(invoice_id)
    
    if escrow and escrow.status.value == "locked":
        # Release to vendor
        release = escrow_manager.release_to_vendor(
            escrow_id=escrow.escrow_id,
            vendor_id="vendor_acme_001",
            ach_confirmation=payment_result.confirmation_number if hasattr(payment_result, 'confirmation_number') else "ACH_CONFIRMED"
        )
        
        if release:
            print(f"   ✅ Escrow Released!")
            print(f"   📋 Release ID: {release.release_id}")
            print(f"   💵 Amount: ${release.amount_usdc} USDC")
            print(f"   📜 TX Hash: {release.tx_hash[:20]}...")
        else:
            print("   ⚠️ Escrow release failed")
    else:
        print(f"   ⚠️ Escrow not in locked state: {escrow.status.value if escrow else 'not found'}")
    
    # ==========================================================================
    # Summary
    # ==========================================================================
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    # Spending summary
    spending = authorizer.get_spending_summary()
    print(f"\n💰 Spending Summary:")
    print(f"   Today: ${spending['today']}")
    print(f"   Daily Remaining: ${spending['daily_remaining']}")
    
    # Escrow stats
    escrow_stats = escrow_manager.get_stats()
    print(f"\n🏦 Escrow Stats:")
    print(f"   Total Locks: {escrow_stats['total_locks']}")
    print(f"   Released: {escrow_stats['released']}")
    print(f"   Total Released USDC: ${escrow_stats['total_released_usdc']}")
    
    print("\n" + "="*70)
    print("✅ DEMO COMPLETE!")
    print("="*70 + "\n")


if __name__ == "__main__":
    use_real = "--real" in sys.argv
    
    if use_real:
        print("\n⚠️  Running with REAL Browserbase sessions!")
        print("   This will use your API credits.\n")
    
    asyncio.run(demo_full_flow(use_real_browser=use_real))
