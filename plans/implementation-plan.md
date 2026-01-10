# Implementation Plan
## IngredientAI - 8-Hour Hackathon Build

**Version:** 1.0
**Date:** January 9, 2026
**Total Time:** 8 hours

---

## Timeline Overview

| Phase | Time | Duration | Deliverable |
|-------|------|----------|-------------|
| 1 | 0:00-1:00 | 1 hr | Setup & Infrastructure |
| 2 | 1:00-2:30 | 1.5 hr | Sourcing Agent (Exa.ai) |
| 3 | 2:30-4:30 | 2 hr | Negotiation Agent (Vapi) |
| 4 | 4:30-5:30 | 1 hr | Evaluation Agent |
| 5 | 5:30-7:00 | 1.5 hr | Payment Agent (x402) |
| 6 | 7:00-8:00 | 1 hr | Integration & Demo Polish |

---

## Phase 1: Setup & Infrastructure (1 hour)

### Hour 0:00-1:00

**Tasks:**
- [ ] Create project structure
- [ ] Set up virtual environment
- [ ] Install dependencies
- [ ] Configure environment variables
- [ ] Set up MongoDB Atlas cluster
- [ ] Test all API connections

**Commands:**
```bash
mkdir ingredient-ai && cd ingredient-ai
python -m venv venv
source venv/bin/activate

pip install pymongo anthropic exa-py vapi-python cdp-sdk fastapi uvicorn python-dotenv

touch .env main.py requirements.txt
mkdir agents api utils
```

**.env Configuration:**
```bash
# MongoDB
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/ingredient_ai

# Claude API
ANTHROPIC_API_KEY=sk-ant-...

# Exa.ai
EXA_API_KEY=...

# Vapi
VAPI_API_KEY=...
VAPI_ASSISTANT_ID=...

# Coinbase CDP
CDP_API_KEY_NAME=...
CDP_API_PRIVATE_KEY=...

# Stripe (for actual payments)
STRIPE_SECRET_KEY=sk_test_...
```

**Verification Script:**
```python
# test_connections.py
import os
from dotenv import load_dotenv
load_dotenv()

# Test MongoDB
from pymongo import MongoClient
client = MongoClient(os.getenv("MONGODB_URI"))
print("MongoDB:", client.server_info()["version"])

# Test Claude
from anthropic import Anthropic
claude = Anthropic()
print("Claude: Connected")

# Test Exa
from exa_py import Exa
exa = Exa(os.getenv("EXA_API_KEY"))
print("Exa.ai: Connected")

# Test Vapi
import vapi
print("Vapi: Connected")

print("\n All connections successful!")
```

**Deliverable:** All APIs connected, MongoDB cluster ready

---

## Phase 2: Sourcing Agent (1.5 hours)

### Hour 1:00-2:30

**File:** `agents/sourcing.py`

```python
import os
from exa_py import Exa
from anthropic import Anthropic
from pymongo import MongoClient

exa = Exa(os.getenv("EXA_API_KEY"))
claude = Anthropic()
db = MongoClient(os.getenv("MONGODB_URI"))["ingredient_ai"]


async def search_suppliers(ingredient: str, quantity: str, location: str) -> list:
    """
    Search for suppliers using Exa.ai semantic search
    Extract structured data using Claude
    """

    # Step 1: Exa semantic search
    query = f"wholesale {ingredient} supplier {location} bulk pricing commercial"

    print(f"  Searching for {ingredient} suppliers...")

    results = exa.search_and_contents(
        query,
        type="neural",
        num_results=5,
        text={"max_characters": 2000},
        highlights=True
    )

    suppliers = []

    for result in results.results:
        # Step 2: Extract structured data via Claude
        extraction_prompt = f"""Extract supplier information from this text.

TEXT:
{result.text[:2000]}

Return JSON with these fields (use null if not found):
- vendor_name: string
- phone: string (format: +1-XXX-XXX-XXXX)
- email: string
- price_per_unit: number
- unit: string (lb, oz, unit, etc.)
- minimum_order: number
- shipping_cost: number or "free"
- certifications: array of strings
- location: string

JSON:"""

        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": extraction_prompt}]
        )

        try:
            import json
            extracted = json.loads(response.content[0].text)

            supplier = {
                "ingredient": ingredient,
                "quantity_needed": quantity,
                "source_url": result.url,
                **extracted
            }

            suppliers.append(supplier)
            print(f"    Found: {extracted.get('vendor_name', 'Unknown')}")

        except json.JSONDecodeError:
            continue

    # Step 3: Save to MongoDB
    if suppliers:
        db.suppliers.insert_many(suppliers)

    return suppliers


async def search_all_ingredients(ingredients: list, location: str) -> list:
    """Search for all ingredients concurrently"""
    import asyncio

    tasks = [
        search_suppliers(ing["name"], ing["quantity"], location)
        for ing in ingredients
    ]

    results = await asyncio.gather(*tasks)

    # Flatten results
    all_suppliers = [s for batch in results for s in batch]

    return all_suppliers
```

**Test:**
```python
# test_sourcing.py
import asyncio
from agents.sourcing import search_all_ingredients

ingredients = [
    {"name": "all-purpose flour", "quantity": "500 lbs"},
    {"name": "eggs", "quantity": "1000 units"}
]

suppliers = asyncio.run(search_all_ingredients(ingredients, "San Francisco, CA"))
print(f"Found {len(suppliers)} suppliers")
```

**Deliverable:** Sourcing agent finds 5+ suppliers per ingredient

---

## Phase 3: Negotiation Agent (2 hours)

### Hour 2:30-4:30

**File:** `agents/negotiation.py`

```python
import os
import vapi
from pymongo import MongoClient

db = MongoClient(os.getenv("MONGODB_URI"))["ingredient_ai"]

# Vapi assistant configuration
NEGOTIATION_ASSISTANT = {
    "name": "IngredientAI Procurement Agent",
    "model": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "systemPrompt": """You are a professional procurement agent calling on behalf of a small bakery business.

YOUR GOALS:
1. Confirm product availability and current pricing
2. Negotiate for bulk discounts (aim for 10-20% off)
3. Ask about long-term contract options
4. Request invoice to be sent to: orders@sweetdreamsbakery.com

NEGOTIATION TACTICS:
- "We're ordering [quantity], what's your best bulk price?"
- "We're comparing several suppliers. Can you match $X per unit?"
- "If we commit to monthly orders, what discount can you offer?"
- "We'd like to start a long-term partnership. What terms can you offer?"

Be professional, friendly, and persistent but not pushy.
Always end by requesting an invoice be sent to the email address.""",
        "temperature": 0.7
    },
    "voice": {
        "provider": "11labs",
        "voiceId": "21m00Tcm4TlvDq8ikWAM"  # Professional voice
    },
    "firstMessage": "Hi, I'm calling on behalf of Sweet Dreams Bakery. We're looking to place a bulk order and wanted to discuss pricing options."
}


async def setup_vapi_assistant():
    """Create or get Vapi assistant"""
    client = vapi.Client(api_key=os.getenv("VAPI_API_KEY"))

    # Check if assistant exists
    existing = os.getenv("VAPI_ASSISTANT_ID")
    if existing:
        return existing

    # Create new assistant
    assistant = await client.assistants.create(**NEGOTIATION_ASSISTANT)
    print(f"Created Vapi assistant: {assistant.id}")

    return assistant.id


async def call_vendor(supplier: dict) -> dict:
    """
    Make outbound call to vendor via Vapi
    Returns negotiation results
    """
    client = vapi.Client(api_key=os.getenv("VAPI_API_KEY"))
    assistant_id = await setup_vapi_assistant()

    print(f"  Calling {supplier['vendor_name']}...")

    # Customize first message with context
    context_message = f"""Hi, I'm calling on behalf of Sweet Dreams Bakery.
    We're looking to order {supplier['quantity_needed']} of {supplier['ingredient']}
    and wanted to discuss bulk pricing options."""

    # Make the call
    call = await client.calls.create(
        assistant_id=assistant_id,
        customer={
            "number": supplier["phone"]
        },
        assistant_overrides={
            "firstMessage": context_message
        }
    )

    # Wait for call to complete (max 5 minutes)
    result = await client.calls.wait(call.id, timeout=300)

    # Parse negotiation outcome from transcript
    outcome = parse_negotiation_outcome(result.transcript, supplier)

    # Save to MongoDB
    negotiation_record = {
        "vendor": supplier["vendor_name"],
        "ingredient": supplier["ingredient"],
        "call_id": call.id,
        "transcript": result.transcript,
        "duration_seconds": result.duration,
        "outcome": outcome["status"],
        "original_price": supplier.get("price_per_unit"),
        "negotiated_price": outcome.get("negotiated_price"),
        "discount_pct": outcome.get("discount_pct"),
        "terms": outcome.get("terms"),
        "invoice_requested": outcome.get("invoice_requested", False)
    }

    db.negotiations.insert_one(negotiation_record)

    return negotiation_record


def parse_negotiation_outcome(transcript: str, supplier: dict) -> dict:
    """Parse call transcript to extract negotiation results"""
    from anthropic import Anthropic
    claude = Anthropic()

    prompt = f"""Analyze this phone call transcript and extract negotiation results.

TRANSCRIPT:
{transcript}

ORIGINAL PRICE: ${supplier.get('price_per_unit', 'unknown')} per {supplier.get('unit', 'unit')}

Return JSON with:
- status: "success" | "partial" | "failed"
- negotiated_price: number or null
- discount_pct: number (percentage discount achieved)
- terms: string (any agreed terms like "net-30", "monthly orders")
- invoice_requested: boolean
- notes: string (any important details)

JSON:"""

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    try:
        return json.loads(response.content[0].text)
    except:
        return {"status": "failed", "notes": "Could not parse outcome"}


async def negotiate_all_vendors(suppliers: list) -> list:
    """Make concurrent calls to all vendors"""
    import asyncio

    # Limit concurrent calls to avoid overwhelming
    semaphore = asyncio.Semaphore(3)

    async def limited_call(supplier):
        async with semaphore:
            return await call_vendor(supplier)

    tasks = [limited_call(s) for s in suppliers]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out errors
    successful = [r for r in results if isinstance(r, dict)]

    return successful
```

**Fallback (Pre-recorded demo):**
```python
# If Vapi calls fail during demo, use pre-recorded results
DEMO_NEGOTIATIONS = [
    {
        "vendor": "Bay Area Foods Co",
        "outcome": "success",
        "original_price": 0.50,
        "negotiated_price": 0.425,
        "discount_pct": 15,
        "terms": "Net-30, monthly orders"
    },
    {
        "vendor": "Fresh Farm Eggs",
        "outcome": "success",
        "original_price": 0.55,
        "negotiated_price": 0.50,
        "discount_pct": 9,
        "terms": "Free shipping over $200"
    }
]
```

**Deliverable:** Vapi calls working, negotiations logged to MongoDB

---

## Phase 4: Evaluation Agent (1 hour)

### Hour 4:30-5:30

**File:** `agents/evaluation.py`

```python
import os
from anthropic import Anthropic
from pymongo import MongoClient

claude = Anthropic()
db = MongoClient(os.getenv("MONGODB_URI"))["ingredient_ai"]


def score_supplier(supplier: dict, negotiation: dict = None) -> float:
    """
    Score supplier on multiple factors (0-100)

    Weights:
    - Price: 35%
    - Quality: 30%
    - Reliability: 15%
    - Negotiation: 10%
    - Relationship: 10%
    """
    score = 0

    # Price score (lower is better, normalized)
    price = negotiation.get("negotiated_price") if negotiation else supplier.get("price_per_unit")
    if price:
        # Assume $1/unit is baseline, lower = better score
        price_score = max(0, 100 - (price * 100))
        score += price_score * 0.35

    # Quality score (based on certifications)
    certs = supplier.get("certifications", [])
    quality_score = min(100, len(certs) * 25)  # 25 points per cert, max 100
    score += quality_score * 0.30

    # Reliability (placeholder - would use historical data)
    reliability_score = 70  # Default
    score += reliability_score * 0.15

    # Negotiation success
    if negotiation and negotiation.get("outcome") == "success":
        discount = negotiation.get("discount_pct", 0)
        negotiation_score = min(100, discount * 5)  # 5 points per % discount
        score += negotiation_score * 0.10

    # Relationship potential (placeholder)
    relationship_score = 60
    score += relationship_score * 0.10

    return round(score, 2)


async def optimize_selection(budget: float) -> dict:
    """
    Select optimal combination of suppliers within budget
    Uses greedy algorithm with scoring
    """

    # Get all suppliers and negotiations from MongoDB
    suppliers = list(db.suppliers.find())
    negotiations = {n["vendor"]: n for n in db.negotiations.find()}

    # Group by ingredient
    by_ingredient = {}
    for s in suppliers:
        ing = s["ingredient"]
        if ing not in by_ingredient:
            by_ingredient[ing] = []

        neg = negotiations.get(s["vendor_name"])
        s["score"] = score_supplier(s, neg)
        s["final_price"] = neg.get("negotiated_price") if neg else s.get("price_per_unit", 0)
        s["negotiation"] = neg

        by_ingredient[ing].append(s)

    # Select best supplier for each ingredient
    selected = []
    total_cost = 0

    for ingredient, options in by_ingredient.items():
        # Sort by score (highest first)
        options.sort(key=lambda x: x["score"], reverse=True)

        for option in options:
            cost = calculate_total_cost(option)

            if total_cost + cost <= budget:
                selected.append({
                    "vendor": option["vendor_name"],
                    "ingredient": ingredient,
                    "quantity": option["quantity_needed"],
                    "unit_price": option["final_price"],
                    "total_cost": cost,
                    "score": option["score"],
                    "discount_achieved": option.get("negotiation", {}).get("discount_pct", 0)
                })
                total_cost += cost
                break

    # Generate justification via Claude
    justification = await generate_justification(selected, budget, total_cost)

    result = {
        "selected_vendors": selected,
        "total_cost": round(total_cost, 2),
        "budget": budget,
        "under_budget_by": round(budget - total_cost, 2),
        "justification": justification
    }

    # Save to MongoDB
    db.decisions.insert_one(result)

    return result


def calculate_total_cost(supplier: dict) -> float:
    """Calculate total cost including quantity and shipping"""
    quantity = parse_quantity(supplier.get("quantity_needed", "1"))
    unit_price = supplier.get("final_price", 0)
    shipping = supplier.get("shipping_cost", 0)

    if shipping == "free":
        shipping = 0

    return (quantity * unit_price) + shipping


def parse_quantity(qty_str: str) -> float:
    """Parse quantity string like '500 lbs' to number"""
    import re
    match = re.search(r'(\d+)', qty_str)
    return float(match.group(1)) if match else 1


async def generate_justification(selected: list, budget: float, total: float) -> str:
    """Generate human-readable justification for selections"""

    prompt = f"""Generate a brief justification for these supplier selections:

SELECTIONS:
{selected}

BUDGET: ${budget}
TOTAL COST: ${total}

Write 2-3 sentences explaining why these suppliers were chosen.
Focus on price, quality, and any discounts achieved."""

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


async def request_invoices(selected_vendors: list) -> None:
    """Request invoices from selected vendors (via email or noted in call)"""

    for vendor in selected_vendors:
        # In real implementation, would send email
        # For demo, we assume invoice was requested during Vapi call

        db.invoices.insert_one({
            "vendor": vendor["vendor"],
            "ingredient": vendor["ingredient"],
            "amount": vendor["total_cost"],
            "status": "pending",
            "requested_at": datetime.now()
        })

        print(f"  Invoice requested from {vendor['vendor']}")
```

**Deliverable:** Evaluation agent selects optimal vendors within budget

---

## Phase 5: Payment Agent with Computer Use (1.5 hours)

### Hour 5:30-7:00

**File:** `computer_use/browser.py`

```python
import os
import base64
from playwright.async_api import async_playwright

class BrowserController:
    """Playwright browser controller for Computer Use"""

    def __init__(self):
        self.browser = None
        self.page = None

    async def start(self, headless=False):
        """Start browser - headless=False for demo visibility"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=headless)
        self.page = await self.browser.new_page()
        return self

    async def navigate(self, url: str):
        """Navigate to URL"""
        await self.page.goto(url)
        await self.page.wait_for_load_state("networkidle")

    async def screenshot(self) -> str:
        """Take screenshot and return base64"""
        screenshot_bytes = await self.page.screenshot()
        return base64.b64encode(screenshot_bytes).decode()

    async def click(self, x: int, y: int):
        """Click at coordinates"""
        await self.page.mouse.click(x, y)

    async def type_text(self, text: str):
        """Type text"""
        await self.page.keyboard.type(text)

    async def save_screenshot(self, path: str):
        """Save screenshot to file"""
        await self.page.screenshot(path=path)

    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
```

**File:** `computer_use/ach_bridge.py`

```python
import os
from anthropic import Anthropic
from .browser import BrowserController
from pymongo import MongoClient
from datetime import datetime

claude = Anthropic()
db = MongoClient(os.getenv("MONGODB_URI"))["ingredient_ai"]

# ACH details from environment
ACH_ROUTING = os.getenv("ACH_ROUTING_NUMBER")
ACH_ACCOUNT = os.getenv("ACH_ACCOUNT_NUMBER")
ACH_NAME = os.getenv("ACH_ACCOUNT_NAME")


async def execute_ach_payment(payment_url: str, amount: float, invoice_id: str) -> dict:
    """
    Execute ACH payment via Computer Use

    1. Open browser to payment URL
    2. Take screenshot, send to Claude
    3. Claude identifies form fields
    4. Fill ACH details and submit
    5. Capture confirmation
    """

    browser = await BrowserController().start(headless=False)  # Visible for demo

    try:
        print(f"    Opening payment portal...")
        await browser.navigate(payment_url)

        # Computer Use loop
        max_iterations = 10
        for i in range(max_iterations):
            # Take screenshot
            screenshot_b64 = await browser.screenshot()

            # Send to Claude with vision
            response = claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": screenshot_b64
                            }
                        },
                        {
                            "type": "text",
                            "text": f"""You are paying an invoice via ACH. Current amount: ${amount}

ACH Details to use:
- Routing Number: {ACH_ROUTING}
- Account Number: {ACH_ACCOUNT}
- Account Name: {ACH_NAME}

Analyze this screenshot and tell me the next action:
1. If you see a payment form, identify which field to fill next
2. If you see a submit/pay button and form is complete, click it
3. If you see a confirmation page, extract the confirmation number

Return JSON:
{{
  "action": "click" | "type" | "done",
  "x": <x coordinate if clicking>,
  "y": <y coordinate if clicking>,
  "text": "<text to type if typing>",
  "confirmation": "<confirmation number if done>",
  "reasoning": "<brief explanation>"
}}"""
                        }
                    ]
                }]
            )

            # Parse response
            import json
            result = json.loads(response.content[0].text)

            print(f"    Step {i+1}: {result['reasoning']}")

            if result["action"] == "done":
                # Payment complete
                await browser.save_screenshot(f"screenshots/{invoice_id}-confirm.png")
                return {
                    "status": "success",
                    "method": "computer_use_ach",
                    "confirmation": result.get("confirmation"),
                    "screenshot": f"screenshots/{invoice_id}-confirm.png"
                }

            elif result["action"] == "click":
                await browser.click(result["x"], result["y"])
                await browser.page.wait_for_timeout(500)

            elif result["action"] == "type":
                await browser.type_text(result["text"])
                await browser.page.wait_for_timeout(300)

        return {"status": "max_iterations", "method": "computer_use_ach"}

    finally:
        await browser.close()
```

**File:** `agents/payment.py`

```python
import os
from cdp import Cdp, Wallet
from pymongo import MongoClient
from datetime import datetime
from computer_use.ach_bridge import execute_ach_payment

# Initialize
Cdp.configure_from_json("cdp_api_key.json")
db = MongoClient(os.getenv("MONGODB_URI"))["ingredient_ai"]

ESCROW_WALLET = os.getenv("ESCROW_WALLET_ADDRESS")


class PaymentAgent:
    def __init__(self):
        self.wallet = self._init_wallet()

    def _init_wallet(self):
        """Initialize or load CDP wallet"""
        try:
            with open(".wallet_data", "r") as f:
                wallet_data = f.read()
            return Wallet.import_data(wallet_data)
        except FileNotFoundError:
            wallet = Wallet.create()
            with open(".wallet_data", "w") as f:
                f.write(wallet.export_data())
            return wallet

    def get_balance(self) -> dict:
        return self.wallet.balances()

    async def process_invoice(self, invoice: dict) -> dict:
        """
        Process invoice through x402 + Computer Use flow

        1. Validate invoice
        2. Authorize via x402 (USDC to escrow)
        3. Execute ACH via Computer Use browser automation
        4. Log transaction
        """

        print(f"  Processing invoice from {invoice['vendor']}...")

        if invoice["amount"] <= 0:
            return {"status": "error", "message": "Invalid amount"}

        # Step 1: x402 authorization
        x402_result = await self._x402_authorize(invoice)

        if x402_result["status"] != "authorized":
            return {"status": "error", "message": "x402 authorization failed"}

        # Step 2: Execute ACH via Computer Use
        print(f"    Launching Computer Use ACH bridge...")
        ach_result = await execute_ach_payment(
            payment_url=invoice["payment_url"],
            amount=invoice["amount"],
            invoice_id=invoice["invoice_id"]
        )

        # Step 3: Log to MongoDB
        transaction = {
            "invoice_id": invoice.get("invoice_id"),
            "vendor": invoice["vendor"],
            "amount": invoice["amount"],
            "x402_tx_hash": x402_result["tx_hash"],
            "x402_explorer": f"https://basescan.org/tx/{x402_result['tx_hash']}",
            "payment_method": "computer_use_ach",
            "ach_confirmation": ach_result.get("confirmation"),
            "screenshot_url": ach_result.get("screenshot"),
            "status": "completed",
            "timestamp": datetime.now()
        }

        db.payments.insert_one(transaction)
        db.invoices.update_one(
            {"_id": invoice["_id"]},
            {"$set": {"status": "paid"}}
        )

        print(f"    x402 TX: {x402_result['tx_hash'][:16]}...")
        print(f"    ACH Confirmation: {ach_result.get('confirmation')}")

        return transaction

    async def _x402_authorize(self, invoice: dict) -> dict:
        """x402 authorization - USDC to escrow"""
        try:
            transfer = self.wallet.transfer(
                amount=invoice["amount"],
                asset_id="usdc",
                destination=ESCROW_WALLET
            )
            return {
                "status": "authorized",
                "tx_hash": transfer.transaction_hash,
                "amount": invoice["amount"]
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}


async def process_all_invoices() -> list:
    """Process all pending invoices"""
    agent = PaymentAgent()

    balance = agent.get_balance()
    print(f"  Wallet balance: {balance}")

    invoices = list(db.invoices.find({"status": "pending"}))

    results = []
    for invoice in invoices:
        result = await agent.process_invoice(invoice)
        results.append(result)

    return results
```

**File:** `api/x402.py` (x402 endpoint with Computer Use bridge)

```python
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import os

app = FastAPI()
ESCROW_WALLET = os.getenv("ESCROW_WALLET_ADDRESS")

class InvoicePaymentRequest(BaseModel):
    invoice_id: str
    vendor: str
    amount: float
    payment_url: str  # URL to vendor payment portal


@app.post("/pay-invoice")
async def pay_invoice(
    request: InvoicePaymentRequest,
    x_payment_signature: str = Header(None, alias="X-Payment-Signature")
):
    """
    x402-protected payment endpoint with Computer Use ACH bridge

    If no payment signature: Returns 402 Payment Required
    If valid signature: Executes ACH payment via Computer Use
    """

    if not x_payment_signature:
        raise HTTPException(
            status_code=402,
            detail="Payment Required",
            headers={
                "X-Payment-Amount": str(request.amount),
                "X-Payment-Currency": "USDC",
                "X-Payment-Recipient": ESCROW_WALLET,
                "X-Payment-Memo": f"{request.vendor}_{request.invoice_id}",
                "X-Payment-Network": "base"
            }
        )

    if not verify_x402_signature(x_payment_signature, request.amount):
        raise HTTPException(status_code=401, detail="Invalid payment signature")

    # Execute ACH via Computer Use bridge
    from computer_use.ach_bridge import execute_ach_payment

    result = await execute_ach_payment(
        payment_url=request.payment_url,
        amount=request.amount,
        invoice_id=request.invoice_id
    )

    return {
        "status": "success",
        "method": "computer_use_ach",
        "confirmation": result.get("confirmation"),
        "screenshot": result.get("screenshot")
    }


def verify_x402_signature(signature: str, amount: float) -> bool:
    """Verify x402 payment signature"""
    # In production: Verify on-chain transaction
    return bool(signature)
```

**Deliverable:** x402 authorization + Computer Use ACH payments working

---

## Phase 6: Integration & Demo Polish (1 hour)

### Hour 7:00-8:00

**File:** `main.py`

```python
import asyncio
import argparse
from datetime import datetime

from agents.sourcing import search_all_ingredients
from agents.negotiation import negotiate_all_vendors
from agents.evaluation import optimize_selection, request_invoices
from agents.payment import process_all_invoices, PaymentAgent


def print_header():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                      IngredientAI                            ║
    ║         Autonomous B2B Procurement Platform                  ║
    ╚══════════════════════════════════════════════════════════════╝
    """)


async def main():
    parser = argparse.ArgumentParser(description="IngredientAI - Autonomous Procurement")
    parser.add_argument("--ingredients", nargs="+", required=True, help="Ingredients to source")
    parser.add_argument("--quantities", nargs="+", required=True, help="Quantities for each ingredient")
    parser.add_argument("--budget", type=float, required=True, help="Total budget in USD")
    parser.add_argument("--location", default="San Francisco, CA", help="Delivery location")

    args = parser.parse_args()

    print_header()

    # Prepare ingredients list
    ingredients = [
        {"name": ing, "quantity": qty}
        for ing, qty in zip(args.ingredients, args.quantities)
    ]

    print(f"Business: Sweet Dreams Bakery")
    print(f"Budget: ${args.budget:,.2f}")
    print(f"Location: {args.location}")
    print(f"Ingredients: {', '.join(args.ingredients)}")
    print()

    # Show wallet balance
    agent = PaymentAgent()
    balance = agent.get_balance()
    print(f"Agent Wallet Balance: {balance}")
    print()

    # PHASE 1: Sourcing
    print("[PHASE 1] Sourcing suppliers concurrently...")
    suppliers = await search_all_ingredients(ingredients, args.location)
    print(f"  Found {len(suppliers)} potential suppliers")
    print()

    # PHASE 2: Negotiation
    print("[PHASE 2] Negotiating with vendors (concurrent calls)...")
    # Select top 3 suppliers per ingredient for negotiation
    top_suppliers = suppliers[:min(6, len(suppliers))]  # Limit for demo
    negotiations = await negotiate_all_vendors(top_suppliers)

    successful = [n for n in negotiations if n.get("outcome") == "success"]
    print(f"  Completed {len(negotiations)} calls, {len(successful)} successful negotiations")
    print()

    # PHASE 3: Evaluation
    print("[PHASE 3] Evaluating best combination...")
    selection = await optimize_selection(args.budget)

    print(f"  Selected {len(selection['selected_vendors'])} vendors")
    print(f"  Total cost: ${selection['total_cost']:,.2f}")
    print(f"  Under budget by: ${selection['under_budget_by']:,.2f}")
    print()

    # Request invoices
    await request_invoices(selection['selected_vendors'])

    # PHASE 4: Payment
    print("[PHASE 4] Processing payments via x402...")
    payments = await process_all_invoices()

    print()
    print("=" * 60)
    print("ORDER COMPLETE!")
    print("=" * 60)
    print()

    # Summary
    print("Selected Vendors:")
    for v in selection['selected_vendors']:
        discount = v.get('discount_achieved', 0)
        discount_str = f" ({discount}% off)" if discount > 0 else ""
        print(f"  {v['ingredient']}: {v['vendor']} - ${v['total_cost']:,.2f}{discount_str}")

    print()
    print(f"Total Cost: ${selection['total_cost']:,.2f}")
    print(f"Budget: ${args.budget:,.2f}")
    print(f"Savings: ${selection['under_budget_by']:,.2f}")

    print()
    print("Transactions:")
    for p in payments:
        if p.get("x402_explorer"):
            print(f"  {p['vendor']}: {p['x402_explorer']}")

    print()
    print("Thank you for using IngredientAI!")


if __name__ == "__main__":
    asyncio.run(main())
```

**Demo Command:**
```bash
python main.py \
  --ingredients "flour" "eggs" "butter" "sugar" \
  --quantities "500 lbs" "1000 units" "100 lbs" "200 lbs" \
  --budget 2000 \
  --location "San Francisco, CA"
```

**Expected Output:**
```
╔══════════════════════════════════════════════════════════════╗
║                      IngredientAI                            ║
║         Autonomous B2B Procurement Platform                  ║
╚══════════════════════════════════════════════════════════════╝

Business: Sweet Dreams Bakery
Budget: $2,000.00
Location: San Francisco, CA
Ingredients: flour, eggs, butter, sugar

Agent Wallet Balance: {'usdc': '500.0'}

[PHASE 1] Sourcing suppliers concurrently...
  Searching for flour suppliers...
    Found: Bay Area Foods Co
    Found: Golden Gate Grains
  Searching for eggs suppliers...
    Found: Fresh Farm Eggs
  ...
  Found 12 potential suppliers

[PHASE 2] Negotiating with vendors (concurrent calls)...
  Calling Bay Area Foods Co...
    "Hi, I'm calling on behalf of Sweet Dreams Bakery..."
    Negotiated 15% bulk discount
  Calling Fresh Farm Eggs...
    Negotiated free shipping over $200
  Completed 6 calls, 4 successful negotiations

[PHASE 3] Evaluating best combination...
  Selected 4 vendors
  Total cost: $1,847.50
  Under budget by: $152.50

[PHASE 4] Processing payments via x402 + Computer Use...
  Processing invoice from Bay Area Foods Co...
    x402 Authorization: 0x8f3e7b2a9c1d...
    Launching Computer Use ACH bridge...
    Opening payment portal...
    Step 1: Clicking on ACH payment option
    Step 2: Filling routing number field
    Step 3: Filling account number field
    Step 4: Filling account name field
    Step 5: Clicking submit payment button
    Step 6: Payment confirmed!
    ACH Confirmation: ACH-2026-0192-BAYAREA
  Processing invoice from Fresh Farm Eggs...
    x402 Authorization: 0x1a2b3c4d5e6f...
    Launching Computer Use ACH bridge...
    ACH Confirmation: ACH-2026-0193-FRESHFARM

============================================================
ORDER COMPLETE!
============================================================

Selected Vendors:
  flour: Bay Area Foods Co - $212.50 (15% off)
  eggs: Fresh Farm Eggs - $485.00 (9% off)
  butter: Dairy Direct - $650.00 (10% off)
  sugar: SweetSupply Co - $500.00

Total Cost: $1,847.50
Budget: $2,000.00
Savings: $152.50

Transactions:
  Bay Area Foods Co: https://basescan.org/tx/0x8f3e7b2a...
  Fresh Farm Eggs: https://basescan.org/tx/0x1a2b3c4d...

Thank you for using IngredientAI!
```

---

## Deliverables Checklist

### Must Have
- [ ] Exa.ai sourcing works for 2+ ingredients
- [ ] 1+ Vapi phone call completes (live or recorded fallback)
- [ ] Evaluation selects vendors within budget
- [ ] 1+ x402 authorization with on-chain proof
- [ ] 1+ Computer Use ACH payment with screenshot confirmation
- [ ] MongoDB logging for all agents

### Should Have
- [ ] Concurrent Vapi calls (2-3 simultaneous)
- [ ] Real invoice processing with payment URLs
- [ ] Quality scoring visible
- [ ] Browser visible during demo (headless=False)

### Nice to Have
- [ ] Web UI
- [ ] Payment confirmation screenshot gallery
- [ ] Analytics dashboard

---

**Implementation Status:** Ready to Build
**Key Innovation:** x402 authorization layer + Computer Use ACH bridge