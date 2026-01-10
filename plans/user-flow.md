# User Flow & Demo Walkthrough
## Haggl - Step-by-Step Demo

**Demo Duration:** <3 minutes
**Date:** January 10, 2026

---

## Input Methods Overview

Haggl supports **four ways** for business owners to interact:

| Method | Best For | Example |
|--------|----------|---------|
| **Menu Upload** | Initial setup | Upload bakery menu PDF |
| **CSV Import** | Bulk inventory | Import spreadsheet with 50+ items |
| **SMS Texting** | On-the-go orders | "Reorder flour" from phone |
| **Dashboard** | Full control | Web UI with analytics |

---

## Pre-Demo Setup

### 1. Verify Connections (5 min before)
```bash
cd haggl
source venv/bin/activate

# Test all APIs
python test_connections.py
# MongoDB: Connected
# Claude: Connected
# Exa.ai: Connected
# Vapi: Connected
# Twilio: Connected
# CDP Wallet: 500 USDC
```

### 2. Clear Previous Data
```bash
python -c "
from pymongo import MongoClient
db = MongoClient()['ingredient_ai']
db.suppliers.delete_many({})
db.negotiations.delete_many({})
db.invoices.delete_many({})
db.payments.delete_many({})
print('Database cleared')
"
```

### 3. Open Browser Tabs
- Tab 1: Terminal (for demo)
- Tab 2: BaseScan (https://basescan.org)
- Tab 3: MongoDB Atlas (optional)

---

## Demo Script

### Scene 1: Introduction (15 seconds)

**What You Say:**
> "Meet Haggl - AI agents that source, negotiate, and pay for business supplies autonomously. Let me show you how it works for a bakery ordering ingredients."

---

### Scene 2: Show Wallet (10 seconds)

**Run:**
```bash
python -c "from agents.payment import PaymentAgent; print(PaymentAgent().get_balance())"
```

**Output:**
```
{'usdc': '500.0'}
```

**Say:**
> "Our AI agent has its own wallet with $500 USDC, ready to make autonomous payments."

---

### Scene 3: Start Demo (10 seconds)

**Run:**
```bash
python main.py \
  --ingredients "flour" "eggs" "butter" "sugar" \
  --quantities "500 lbs" "1000 units" "100 lbs" "200 lbs" \
  --budget 2000 \
  --location "San Francisco, CA"
```

**Say:**
> "A baker needs flour, eggs, butter, and sugar with a $2,000 budget. Watch what happens."

---

### Scene 4: Sourcing Phase (30 seconds)

**Output:**
```
[PHASE 1] Sourcing suppliers concurrently...
  Searching for flour suppliers...
    Found: Bay Area Foods Co
    Found: Golden Gate Grains
    Found: Pacific Flour Mills
  Searching for eggs suppliers...
    Found: Fresh Farm Eggs
    Found: Happy Hen Farms
  Searching for butter suppliers...
    Found: Dairy Direct
  Searching for sugar suppliers...
    Found: SweetSupply Co
  Found 12 potential suppliers
```

**Say:**
> "The sourcing agent is using Exa.ai to search the web for wholesale suppliers. It's finding real vendors, extracting pricing, and caching everything to MongoDB."

**Key Point:** Emphasize "concurrent" and "real vendors"

---

### Scene 5: Negotiation Phase (60 seconds) - THE WOW MOMENT

**Output:**
```
[PHASE 2] Negotiating with vendors (concurrent calls)...
  Calling Bay Area Foods Co...
```

**Say:**
> "Now watch this. The negotiation agent is making REAL phone calls via Vapi. These are actual calls happening right now to these vendors."

*[Pause to let call happen]*

**Output:**
```
    "Hi, I'm calling on behalf of Sweet Dreams Bakery..."
    "We're looking to order 500 lbs of flour..."
    "What's your best bulk pricing?"
    "We're comparing several suppliers..."
    Negotiated 15% bulk discount!

  Calling Fresh Farm Eggs...
    Negotiated free shipping over $200

  Calling Dairy Direct...
    Negotiated 10% for monthly commitment

  Completed 6 calls, 4 successful negotiations
```

**Say:**
> "The AI just negotiated a 15% discount by phone! It mentioned we're comparing suppliers and asked for bulk pricing. All calls happened concurrently - 6 vendors called in parallel."

**Key Point:** THIS IS THE WOW MOMENT - AI making real phone calls

---

### Scene 6: Evaluation Phase (20 seconds)

**Output:**
```
[PHASE 3] Evaluating best combination...
  Scoring suppliers on quality, price, reliability...
  Optimizing within $2,000 budget...
  Selected 4 vendors
  Total cost: $1,847.50
  Under budget by: $152.50

  Requesting invoices from selected vendors...
```

**Say:**
> "The evaluation agent scored all suppliers on price, quality, and the discounts we negotiated. It selected the optimal combination under budget and requested invoices."

---

### Scene 7: Payment Phase (45 seconds) - SECOND WOW MOMENT

**Output:**
```
[PHASE 4] Processing payments via x402...
  Processing invoice from Bay Area Foods Co...
    x402 authorization...
    TX: 0x8f3e7b2a9c1d4f5e6b8a7c9d2e1f3b4a5c6d7e8f9a0b
  Processing invoice from Fresh Farm Eggs...
    TX: 0x1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t

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
  https://basescan.org/tx/0x8f3e7b2a...
  https://basescan.org/tx/0x1a2b3c4d...
```

**Say:**
> "Now the payment agent processes invoices through x402. These are REAL on-chain transactions. Let me show you the proof."

**Do:**
1. Copy transaction hash
2. Switch to BaseScan tab
3. Paste hash, press enter
4. Show confirmed transaction

**Say:**
> "There it is - a real USDC transaction on Base network. The agent negotiated AND paid, all autonomously. No human clicked confirm."

---

### Scene 8: Summary (15 seconds)

**Say:**
> "To recap: Our AI agents sourced 12 vendors, made 6 concurrent phone calls, negotiated 15% discounts, and executed real payments via x402. Total time: under 3 minutes. Savings: $152 plus future discounts from long-term contracts."

---

## SMS Demo Script (Alternative Flow)

### SMS Reorder Demo (30 seconds)

**Show phone screen or terminal:**

**Step 1: Owner texts reorder**
```
Owner → Haggl: "Reorder flour"
```

**Step 2: Haggl responds with confirmation**
```
Haggl → Owner: "Reorder 500 lbs all-purpose flour from Bay Area Foods @ $0.425/lb ($212.50 total)? Reply APPROVE or DENY"
```

**Step 3: Owner approves**
```
Owner → Haggl: "APPROVE"
```

**Step 4: Haggl confirms and processes**
```
Haggl → Owner: "✓ Order placed! x402 TX: 0x8f3e... ETA: Jan 12. Tracking: #HGL-2026-0192"
```

**Say:**
> "Business owners can reorder with a single text. No app needed. Haggl remembers their previous orders and preferred vendors."

---

## CSV Import Demo (15 seconds)

**Show dashboard or curl command:**

```bash
# Upload ingredients.csv
curl -X POST http://localhost:8000/upload/csv \
  -F "file=@ingredients.csv"

# Response:
{
  "status": "success",
  "ingredients": [
    {"name": "flour", "quantity": "500 lbs", "quality": "commercial"},
    {"name": "eggs", "quantity": "1000 units", "quality": "cage-free"},
    ...
  ]
}
```

**Say:**
> "Bulk import from any spreadsheet. Just upload CSV, we parse the ingredients, and start sourcing immediately."

---

## Q&A Responses

### "Are those real phone calls?"
> "Yes, using Vapi's voice AI. It creates a Claude-powered assistant that makes actual outbound calls with text-to-speech. The calls are happening in real-time."

### "How does x402 work?"
> "x402 sits between our agent and our backend. When the agent wants to pay an invoice, it first authorizes the spend with a USDC transfer to our escrow wallet. Once verified, our backend executes the actual payment to the vendor via Stripe or ACH. The vendor never knows x402 exists - they just get paid normally."

### "What if negotiation fails?"
> "The agent has fallback strategies. If a vendor won't negotiate, it notes that for future reference and moves to the next supplier. We also have competitive leverage - 'another supplier quoted us $X.'"

### "Is this production-ready?"
> "The core technology works today. For production, we'd add user authentication, more payment methods, and compliance features. But the autonomous sourcing, negotiation, and payment? That works right now."

### "How does SMS ordering work?"
> "Business owners text a Twilio number we provision. Claude parses their intent - reorder, new order, approve, deny, or status check. For reorders, we look up their previous order history in MongoDB and auto-fill quantities. They just reply APPROVE and we handle the rest."

### "Can they import bulk orders?"
> "Yes, CSV upload. We auto-detect column mappings - ingredient, quantity, unit, quality. Works with any spreadsheet export from their inventory system."

---

## Backup Demo (If Live Fails)

### Pre-Recorded Vapi Call
Have a 30-second audio clip of a successful negotiation call ready to play.

### Cached Results
```python
# fallback_demo.py
DEMO_RESULTS = {
    "suppliers": 12,
    "negotiations": [
        {"vendor": "Bay Area Foods", "discount": "15%"},
        {"vendor": "Fresh Farm Eggs", "discount": "free shipping"}
    ],
    "total_cost": 1847.50,
    "savings": 152.50,
    "tx_hash": "0x8f3e7b2a..."
}
```

### Show Code
If all else fails, walk through the code explaining what each agent does.

---

## Success Checklist

**During Demo:**
- [ ] Wallet balance shown
- [ ] Sourcing finds 10+ suppliers
- [ ] At least 1 Vapi call plays
- [ ] Negotiation discount achieved
- [ ] Payment executes
- [ ] BaseScan confirmation shown
- [ ] Under 3 minutes total

**Judge Reaction Goals:**
- "Wait, it made actual phone calls?"
- "That's a real blockchain transaction"
- "This could actually work for businesses"

---

**Demo Status:** Ready
**Confidence:** High
