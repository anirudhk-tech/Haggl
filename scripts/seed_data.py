#!/usr/bin/env python3
"""
Seed database with sample data for development/testing.

Usage:
    python scripts/seed_data.py
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dotenv import load_dotenv

load_dotenv()

from storage.database import get_database, setup_indexes
from storage.schemas import (
    VendorDocument,
    BusinessProfileDocument,
    OrderDocument,
    OrderStatus,
)


SAMPLE_VENDORS = [
    {
        "vendor_id": str(uuid4()),
        "name": "Farm Fresh Eggs Co",
        "phone": "+15551234567",
        "email": "orders@farmfresh.com",
        "products": ["eggs", "dairy", "poultry"],
        "quality_score": 92.0,
        "reliability_score": 88.0,
        "certifications": ["organic", "free-range", "local"],
        "location": {"city": "Austin", "state": "TX", "zip": "78701"},
    },
    {
        "vendor_id": str(uuid4()),
        "name": "Central Texas Produce",
        "phone": "+15559876543",
        "email": "sales@ctxproduce.com",
        "products": ["vegetables", "fruits", "herbs"],
        "quality_score": 89.0,
        "reliability_score": 94.0,
        "certifications": ["organic", "non-gmo"],
        "location": {"city": "Round Rock", "state": "TX", "zip": "78664"},
    },
    {
        "vendor_id": str(uuid4()),
        "name": "Hill Country Flour Mill",
        "phone": "+15555551234",
        "email": "orders@hcflour.com",
        "products": ["flour", "grains", "baking supplies"],
        "quality_score": 95.0,
        "reliability_score": 91.0,
        "certifications": ["artisan", "local", "non-gmo"],
        "location": {"city": "Fredericksburg", "state": "TX", "zip": "78624"},
    },
]

SAMPLE_BUSINESSES = [
    {
        "business_id": str(uuid4()),
        "business_name": "Acme Bakery",
        "business_type": "bakery",
        "location": "Austin, TX",
        "phone": "+15550001111",
        "onboarding_complete": True,
        "selected_products": ["eggs", "flour", "butter", "sugar"],
    },
    {
        "business_id": str(uuid4()),
        "business_name": "Joe's Diner",
        "business_type": "restaurant",
        "location": "Round Rock, TX",
        "phone": "+15550002222",
        "onboarding_complete": True,
        "selected_products": ["eggs", "vegetables", "meat", "dairy"],
    },
]


async def seed_vendors(db) -> None:
    """Seed vendor collection."""
    collection = db["vendors"]
    
    # Clear existing
    await asyncio.to_thread(collection.delete_many, {})
    
    # Insert sample vendors
    for vendor in SAMPLE_VENDORS:
        vendor["created_at"] = datetime.now(timezone.utc)
        vendor["updated_at"] = datetime.now(timezone.utc)
    
    result = await asyncio.to_thread(collection.insert_many, SAMPLE_VENDORS)
    print(f"✓ Seeded {len(result.inserted_ids)} vendors")


async def seed_businesses(db) -> None:
    """Seed business collection."""
    collection = db["businesses"]
    
    # Clear existing
    await asyncio.to_thread(collection.delete_many, {})
    
    # Insert sample businesses
    for business in SAMPLE_BUSINESSES:
        business["created_at"] = datetime.now(timezone.utc)
        business["updated_at"] = datetime.now(timezone.utc)
    
    result = await asyncio.to_thread(collection.insert_many, SAMPLE_BUSINESSES)
    print(f"✓ Seeded {len(result.inserted_ids)} businesses")


async def seed_sample_order(db) -> None:
    """Seed a sample order for testing."""
    collection = db["orders"]
    
    # Get first business
    businesses_col = db["businesses"]
    business = await asyncio.to_thread(businesses_col.find_one, {})
    
    if not business:
        print("⚠ No businesses found, skipping order seed")
        return
    
    sample_order = {
        "order_id": str(uuid4()),
        "business_id": business["business_id"],
        "product": "eggs",
        "quantity": 12,
        "unit": "dozen",
        "status": OrderStatus.PENDING.value,
        "delivery_date": "2026-01-15",
        "delivery_address": "123 Main St, Austin, TX",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    
    await asyncio.to_thread(collection.insert_one, sample_order)
    print(f"✓ Seeded sample order: {sample_order['order_id']}")


async def main() -> None:
    """Main seed function."""
    print("\n🌱 Seeding Haggl database...\n")
    
    db = get_database()
    
    # Setup indexes first
    setup_indexes()
    print("✓ Database indexes created\n")
    
    # Seed data
    await seed_vendors(db)
    await seed_businesses(db)
    await seed_sample_order(db)
    
    print("\n✅ Database seeding complete!\n")


if __name__ == "__main__":
    asyncio.run(main())
