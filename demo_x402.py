#!/usr/bin/env python3
"""
Haggl x402 Payment Demo

This script demonstrates the full x402 authorization + payment flow:
1. x402 authorization (on-chain budget enforcement)
2. Payment execution (mock Stripe card or ACH)

Run with:
    python demo_x402.py

Or start the server:
    python demo_x402.py serve
"""

import asyncio
import argparse
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dotenv import load_dotenv
load_dotenv()


async def run_demo():
    """Run the x402 payment demo."""
    from x402 import get_authorizer, AuthorizationRequest, Invoice
    from payment_agent import get_executor, PaymentRequest, PaymentMethod
    
    print("\n" + "="*60)
    print("🔐 HAGGL x402 PAYMENT AUTHORIZATION DEMO")
    print("="*60)
    
    # Demo invoices (from hypothetical evaluation agent)
    invoices = [
        {
            "invoice_id": "INV-2026-0001",
            "vendor_name": "Bay Area Foods Co",
            "amount_usd": 212.50,
            "description": "500 lbs flour - wholesale"
        },
        {
            "invoice_id": "INV-2026-0002", 
            "vendor_name": "Farm Fresh Eggs LLC",
            "amount_usd": 450.00,
            "description": "1000 eggs - grade A"
        },
        {
            "invoice_id": "INV-2026-0003",
            "vendor_name": "Dairy Direct",
            "amount_usd": 187.50,
            "description": "50 lbs butter - unsalted"
        }
    ]
    
    budget = {
        "total": 2000.00,
        "remaining": 2000.00
    }
    
    print(f"\n📊 BUDGET: ${budget['total']:.2f}")
    print(f"📋 INVOICES TO PAY: {len(invoices)}")
    
    # Initialize components
    authorizer = get_authorizer()
    executor = get_executor(simulate_delays=True)
    
    # Reset any previous state
    authorizer.reset()
    executor.reset()
    
    results = []
    
    for invoice_data in invoices:
        print("\n" + "-"*60)
        print(f"📄 Processing: {invoice_data['invoice_id']}")
        print(f"   Vendor: {invoice_data['vendor_name']}")
        print(f"   Amount: ${invoice_data['amount_usd']:.2f}")
        print(f"   Description: {invoice_data['description']}")
        
        # =====================================================================
        # PHASE 1: x402 AUTHORIZATION
        # =====================================================================
        print("\n[PHASE 1] x402 AUTHORIZATION...")
        
        invoice = Invoice(
            invoice_id=invoice_data["invoice_id"],
            vendor_name=invoice_data["vendor_name"],
            amount_usd=invoice_data["amount_usd"],
            description=invoice_data["description"]
        )
        
        auth_request = AuthorizationRequest(
            invoice=invoice,
            budget_total=budget["total"],
            budget_remaining=budget["remaining"]
        )
        
        auth_response = await authorizer.authorize(auth_request)
        
        if auth_response.status.value != "authorized":
            print(f"   ❌ Authorization REJECTED: {auth_response.error}")
            results.append({
                "invoice_id": invoice_data["invoice_id"],
                "authorized": False,
                "paid": False,
                "error": auth_response.error
            })
            continue
        
        print(f"   ✅ AUTHORIZED")
        print(f"   📝 Auth Token: {auth_response.auth_token[:20]}...")
        print(f"   🔗 TX Hash: {auth_response.tx_hash}")
        print(f"   🌐 Explorer: {auth_response.explorer_url}")
        
        # Update remaining budget
        budget["remaining"] -= invoice_data["amount_usd"]
        print(f"   💰 Budget remaining: ${budget['remaining']:.2f}")
        
        # =====================================================================
        # PHASE 2: PAYMENT EXECUTION
        # =====================================================================
        print("\n[PHASE 2] PAYMENT EXECUTION...")
        
        # Alternate between card and ACH for demo
        payment_method = PaymentMethod.MOCK_CARD if len(results) % 2 == 0 else PaymentMethod.MOCK_ACH
        print(f"   Method: {payment_method.value}")
        
        # Consume auth token
        consumed_invoice = authorizer.consume_auth_token(auth_response.auth_token)
        
        payment_request = PaymentRequest(
            auth_token=auth_response.auth_token,
            invoice_id=invoice_data["invoice_id"],
            amount_usd=invoice_data["amount_usd"],
            vendor_name=invoice_data["vendor_name"],
            payment_method=payment_method
        )
        
        payment_result = await executor.execute_payment(
            payment_request,
            x402_tx_hash=auth_response.tx_hash
        )
        
        if payment_result.status.value in ("succeeded", "processing"):
            print(f"   ✅ Payment {payment_result.status.value.upper()}")
            print(f"   🧾 Confirmation: {payment_result.confirmation_number}")
            
            if payment_result.stripe_payment:
                print(f"   💳 Stripe ID: {payment_result.stripe_payment.payment_intent_id}")
            
            if payment_result.ach_payment:
                print(f"   🏦 ACH Transfer: {payment_result.ach_payment.ach_transfer_id}")
                print(f"   📅 Est. Arrival: {payment_result.ach_payment.estimated_arrival}")
            
            results.append({
                "invoice_id": invoice_data["invoice_id"],
                "authorized": True,
                "paid": True,
                "x402_tx": auth_response.tx_hash,
                "confirmation": payment_result.confirmation_number
            })
        else:
            print(f"   ❌ Payment FAILED: {payment_result.error}")
            results.append({
                "invoice_id": invoice_data["invoice_id"],
                "authorized": True,
                "paid": False,
                "error": payment_result.error
            })
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "="*60)
    print("📊 PAYMENT SUMMARY")
    print("="*60)
    
    total_authorized = sum(
        invoices[i]["amount_usd"] 
        for i, r in enumerate(results) 
        if r.get("authorized")
    )
    total_paid = sum(
        invoices[i]["amount_usd"] 
        for i, r in enumerate(results) 
        if r.get("paid")
    )
    
    print(f"\n💰 Budget: ${budget['total']:.2f}")
    print(f"✅ Authorized: ${total_authorized:.2f}")
    print(f"💳 Paid: ${total_paid:.2f}")
    print(f"💵 Remaining: ${budget['remaining']:.2f}")
    
    print("\n📋 Results by Invoice:")
    for i, result in enumerate(results):
        status = "✅ PAID" if result.get("paid") else ("🔐 AUTH ONLY" if result.get("authorized") else "❌ REJECTED")
        print(f"   {result['invoice_id']}: {status}")
        if result.get("x402_tx"):
            print(f"      x402: {result['x402_tx'][:20]}...")
        if result.get("confirmation"):
            print(f"      Confirmation: {result['confirmation']}")
        if result.get("error"):
            print(f"      Error: {result['error']}")
    
    # Spending summary
    spending = authorizer.get_spending_summary()
    print(f"\n📈 Spending Summary:")
    print(f"   Today: ${spending['today']:.2f} / ${spending['daily_limit']:.2f}")
    print(f"   Weekly: ${spending['weekly_total']:.2f} / ${spending['weekly_limit']:.2f}")
    
    print("\n" + "="*60)
    print("✨ DEMO COMPLETE")
    print("="*60)
    print("\nKey Points:")
    print("• x402 provides cryptographic authorization BEFORE payment")
    print("• On-chain TX hash proves budget was committed")
    print("• Auth tokens are single-use (consumed on payment)")
    print("• Mock Stripe/ACH simulates legacy execution")
    print("\nFor production: Replace mock executor with real Stripe SDK")
    print("or Computer Use browser automation for vendor portals.")


def main():
    parser = argparse.ArgumentParser(description="Haggl x402 Payment Demo")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Demo command (default)
    demo_parser = subparsers.add_parser("demo", help="Run the payment demo")
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start the API server")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host (default: 0.0.0.0)")
    serve_parser.add_argument("--port", type=int, default=8002, help="Port (default: 8002)")
    serve_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    if args.command == "serve":
        import uvicorn
        uvicorn.run(
            "src.payment_agent.server:app",
            host=args.host,
            port=args.port,
            reload=args.reload
        )
    else:
        # Default to demo
        asyncio.run(run_demo())


if __name__ == "__main__":
    main()
