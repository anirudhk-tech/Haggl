#!/usr/bin/env python3
"""
Demo: Pay an Intuit QuickBooks Invoice via Browserbase x402

This demonstrates the full flow:
1. x402 authorization (budget enforcement)
2. Browserbase x402 session (pay for cloud browser with USDC)
3. Navigate to Intuit invoice
4. Fill ACH payment form (credentials injected securely)
5. Submit and capture confirmation

Usage:
    python demo_intuit_payment.py [invoice_url]

Example:
    python demo_intuit_payment.py "https://connect.intuit.com/t/scs-v1-..."
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dotenv import load_dotenv
load_dotenv()


# Default test invoice (Best Egg Co - $0.01)
DEFAULT_INVOICE_URL = (
    "https://connect.intuit.com/t/scs-v1-26297a3db4e7480aafeabb334abefac156cc685711ec4c7fb924a5173d9a44b4b84020803d524618846eb7c5280bb7f2"
    "?cta=viewinvoicenow&locale=en_US&grw=email_pay_button_t1"
)


async def main():
    from x402 import get_authorizer, AuthorizationRequest, Invoice
    from payment_agent.browserbase import pay_intuit_invoice
    
    # Get invoice URL from args or use default
    invoice_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INVOICE_URL
    
    print("\n" + "="*70)
    print("🌐 BROWSERBASE x402 INTUIT PAYMENT DEMO")
    print("="*70)
    
    # Invoice details (would be extracted from URL or email in production)
    invoice_data = {
        "invoice_id": "INV-1001",
        "vendor_name": "Best Egg Co",
        "amount_usd": 0.01,  # Test invoice
        "description": "Test invoice for demo"
    }
    
    print(f"\n📄 INVOICE DETAILS")
    print(f"   Vendor: {invoice_data['vendor_name']}")
    print(f"   Invoice #: {invoice_data['invoice_id']}")
    print(f"   Amount: ${invoice_data['amount_usd']:.2f}")
    print(f"   URL: {invoice_url[:60]}...")
    
    # =========================================================================
    # PHASE 1: x402 AUTHORIZATION
    # =========================================================================
    print("\n" + "-"*70)
    print("[PHASE 1] x402 AUTHORIZATION")
    print("-"*70)
    
    authorizer = get_authorizer()
    authorizer.reset()  # Clean state for demo
    
    invoice = Invoice(
        invoice_id=invoice_data["invoice_id"],
        vendor_name=invoice_data["vendor_name"],
        amount_usd=invoice_data["amount_usd"],
        description=invoice_data["description"],
        payment_url=invoice_url
    )
    
    auth_request = AuthorizationRequest(
        invoice=invoice,
        budget_total=100.0,  # $100 budget for demo
        budget_remaining=100.0
    )
    
    print("\n🔐 Requesting authorization...")
    auth_response = await authorizer.authorize(auth_request)
    
    if auth_response.status.value != "authorized":
        print(f"❌ Authorization REJECTED: {auth_response.error}")
        return
    
    print(f"✅ AUTHORIZED!")
    print(f"   Auth Token: {auth_response.auth_token[:30]}...")
    print(f"   TX Hash: {auth_response.tx_hash}")
    print(f"   Explorer: {auth_response.explorer_url}")
    
    # =========================================================================
    # PHASE 2: BROWSERBASE x402 PAYMENT EXECUTION
    # =========================================================================
    print("\n" + "-"*70)
    print("[PHASE 2] BROWSERBASE x402 PAYMENT EXECUTION")
    print("-"*70)
    
    print("\n🌐 Creating Browserbase session (paid with USDC)...")
    print("   This would cost ~$0.002 USDC per session in production")
    
    # Check if we have real Browserbase credentials
    has_browserbase = bool(os.getenv("BROWSERBASE_PROJECT_ID"))
    mock_mode = not has_browserbase
    
    if mock_mode:
        print("   Mode: MOCK (no BROWSERBASE_PROJECT_ID set)")
        print("   Set BROWSERBASE_PROJECT_ID for real browser automation")
    else:
        print("   Mode: REAL (using Browserbase cloud browsers)")
    
    print("\n🖥️  Executing payment flow...")
    
    result = await pay_intuit_invoice(
        invoice_url=invoice_url,
        auth_token=auth_response.auth_token,
        mock_mode=mock_mode
    )
    
    # Print execution steps
    print("\n📋 Execution Steps:")
    for i, step in enumerate(result.get("steps", []), 1):
        print(f"   {i}. {step}")
    
    # =========================================================================
    # RESULT
    # =========================================================================
    print("\n" + "-"*70)
    print("[RESULT]")
    print("-"*70)
    
    if result["status"] == "succeeded":
        print(f"\n✅ PAYMENT SUCCEEDED!")
        print(f"   Confirmation: {result.get('confirmation', 'N/A')}")
        print(f"   Screenshots: {len(result.get('screenshots', []))} captured")
    else:
        print(f"\n❌ PAYMENT FAILED")
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    print(f"""
┌─────────────────────────────────────────────────────────────────────┐
│  TRANSACTION FLOW                                                    │
│                                                                      │
│  1. x402 Authorization                                               │
│     └─ Budget: $100.00                                              │
│     └─ Amount: ${invoice_data['amount_usd']:.2f}                                               │
│     └─ TX: {auth_response.tx_hash[:40]}...          │
│                                                                      │
│  2. Browserbase Session (x402 payment)                              │
│     └─ Cloud browser instance                                       │
│     └─ Cost: ~$0.002 USDC                                          │
│                                                                      │
│  3. Intuit Payment Portal                                           │
│     └─ URL: {invoice_url[:50]}...          │
│     └─ Method: ACH Bank Transfer                                    │
│     └─ Status: {result['status'].upper():12}                                        │
│                                                                      │
│  4. Confirmation                                                     │
│     └─ {result.get('confirmation', 'PAYMENT_SUBMITTED'):40}            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
""")
    
    print("🔑 KEY INNOVATIONS:")
    print("   • x402 used TWICE: authorization + browser session payment")
    print("   • ACH credentials NEVER visible to AI (secure injection)")
    print("   • Cloud browser = scalable, no local Playwright needed")
    print("   • Works with ANY payment portal (Intuit, Stripe, etc.)")
    
    print("\n" + "="*70)
    print("✨ DEMO COMPLETE")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
