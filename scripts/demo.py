#!/usr/bin/env python3
"""
Haggl Demo Script

Demonstrates the full procurement flow end-to-end.

Usage:
    python scripts/demo.py
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dotenv import load_dotenv

load_dotenv()

import httpx


API_URL = os.getenv("API_URL", "http://localhost:8001")


async def demo_flow():
    """Run a demonstration of the Haggl procurement flow."""
    print("\n" + "=" * 60)
    print("🚀 HAGGL DEMO - AI Procurement Automation")
    print("=" * 60 + "\n")

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: Create a business (onboarding)
        print("📝 Step 1: Onboarding a new business...")
        onboarding_data = {
            "business_name": "Demo Bakery",
            "business_type": "bakery",
            "location": "Austin, TX",
            "phone": "+15551234567",
            "selected_products": ["eggs", "flour", "butter"],
        }
        
        response = await client.post(
            f"{API_URL}/onboarding/complete",
            json=onboarding_data,
        )
        
        if response.status_code == 200:
            business_id = response.json().get("business_id")
            print(f"   ✓ Business created: {business_id}\n")
        else:
            print(f"   ✗ Onboarding failed: {response.text}\n")
            return

        # Step 2: Create an order
        print("🛒 Step 2: Creating a procurement order...")
        order_data = {
            "business_id": business_id,
            "items": [
                {"product": "eggs", "quantity": 12, "unit": "dozen"}
            ],
            "phone_number": "+15551234567",
            "delivery_date": "2026-01-15",
            "delivery_address": "123 Main St, Austin, TX",
        }
        
        response = await client.post(
            f"{API_URL}/orders/create",
            json=order_data,
        )
        
        if response.status_code == 200:
            order_id = response.json().get("order_id")
            print(f"   ✓ Order created: {order_id}")
            print("   → Sourcing vendors...")
            print("   → Calling vendors in parallel...")
            print("   → Evaluating offers...\n")
        else:
            print(f"   ✗ Order creation failed: {response.text}\n")
            return

        # Step 3: Wait for approval
        print("⏳ Step 3: Waiting for approval...")
        print("   (In production, this would wait for vendor calls to complete)\n")
        
        await asyncio.sleep(5)  # Simulated wait

        # Step 4: Check pending approvals
        print("📋 Step 4: Checking pending approvals...")
        response = await client.get(f"{API_URL}/orders/pending")
        
        if response.status_code == 200:
            pending = response.json().get("pending_approvals", [])
            if pending:
                print(f"   ✓ Found {len(pending)} pending approval(s)")
                for approval in pending:
                    print(f"     • {approval.get('product')}: ${approval.get('price', 'TBD')}")
            else:
                print("   ✓ No pending approvals (order may still be processing)")
        print()

        # Step 5: Recent events
        print("📊 Step 5: Recent activity events...")
        response = await client.get(f"{API_URL}/events/recent?limit=5")
        
        if response.status_code == 200:
            events = response.json().get("events", [])
            for event in events[:5]:
                stage = event.get("stage", "unknown")
                message = event.get("message", "")
                print(f"   [{stage}] {message}")
        print()

    print("=" * 60)
    print("✅ Demo complete!")
    print("=" * 60)
    print("\nTo see the full UI, visit: http://localhost:3000")
    print("To monitor events: curl -N http://localhost:8001/events/stream\n")


if __name__ == "__main__":
    asyncio.run(demo_flow())
