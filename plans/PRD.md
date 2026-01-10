# Product Requirements Document
## IngredientAI - Autonomous B2B Procurement Platform

**Version:** 1.0
**Date:** January 9, 2026
**Hackathon:** MongoDB Agentic Orchestration & Collaboration (8 hours)

---

## Executive Summary

IngredientAI is a multi-agent AI system that autonomously sources, negotiates, evaluates, and pays for business ingredients and supplies. A business owner (baker, restaurant, manufacturer) inputs their ingredient needs, quantities, and budget. Four specialized agents work **concurrently** to find the best suppliers, negotiate prices via real phone calls, evaluate options, and process payments using the x402 protocol.

**Core Innovation:** Real-time phone negotiations via Vapi TTS combined with autonomous x402 payments - AI agents that can both negotiate verbally AND pay autonomously.

---

## Problem Statement

### Pain Points for Small Business Owners

1. **Time-Intensive Sourcing:** 5-10 hours/week finding and comparing suppliers
2. **No Negotiation Power:** Individual businesses lack leverage for bulk/contract discounts
3. **Manual Price Comparison:** Spreadsheet comparisons across dozens of vendors
4. **Fragmented Payments:** Multiple invoices, payment methods, reconciliation
5. **Quality vs Price Tradeoffs:** Difficult to balance ingredient quality with budget

### Market Opportunity

- **TAM:** $2.3T B2B procurement market
- **SAM:** $180B small business ingredient sourcing
- **SOM:** Food service, bakeries, restaurants, small manufacturers

### User Persona

**Sarah**, owner of "Sweet Dreams Bakery"
- Orders $5,000-15,000/month in ingredients
- Uses 3-4 suppliers found through Google/word of mouth
- Spends 6 hours/week on sourcing and ordering
- Rarely negotiates (doesn't have time)
- Wants better prices but can't sacrifice quality

---

## Solution: Four Concurrent Agents

```
BUSINESS OWNER INPUT
├── Ingredients needed (eggs, flour, sugar, butter)
├── Quantities required (500 lbs, 1000 units, etc.)
├── Quality requirements (organic, grade A, etc.)
├── Budget constraint ($2,000)
└── Delivery location (San Francisco, CA)

         ↓ [CONCURRENT EXECUTION]

┌─────────────────────────────────────────────────────────┐
│  [1] SOURCING AGENT        [2] NEGOTIATION AGENT       │
│  Uses exa.ai to find       Uses Vapi TTS to phone      │
│  suppliers across web      vendors CONCURRENTLY        │
│         ↓                         ↓                    │
│  Ingests pricing,          Negotiates bulk discounts,  │
│  features, MOQs            long-term contracts         │
└─────────────────────────────────────────────────────────┘
                    ↓
         [3] EVALUATION AGENT
         Analyzes quality vs price
         Optimizes within budget
         Selects best combination
         Requests invoices from vendors
                    ↓
         [4] PAYMENT AGENT
         Receives invoices via email
         Processes via x402 protocol
         Executes payments (Stripe/ACH)
         Sends confirmation to owner
```

---

## Agent 1: Sourcing Agent

**Technology:** Exa.ai + Claude API

**Purpose:** Find all potential suppliers for requested ingredients

**Process:**
1. Use Exa.ai semantic search for each ingredient
2. Extract pricing, MOQs, shipping costs via Claude
3. Find quality certifications and reviews
4. Get contact information (phone, email)
5. Cache results in MongoDB

**Input:**
```json
{
  "ingredients": [
    {"name": "All-purpose flour", "quantity": "500 lbs", "quality": "commercial grade"},
    {"name": "Eggs", "quantity": "1000 units", "quality": "Grade A, cage-free"},
    {"name": "Butter", "quantity": "100 lbs", "quality": "unsalted"}
  ],
  "location": "San Francisco, CA"
}
```

**Output:**
```json
{
  "suppliers": [
    {
      "vendor": "Bay Area Foods Co",
      "ingredient": "All-purpose flour",
      "price_per_unit": 0.45,
      "unit": "lb",
      "moq": 100,
      "shipping": 25.00,
      "phone": "+1-415-555-0123",
      "email": "orders@bayareafoods.com",
      "quality_score": 8.5,
      "certifications": ["FDA approved", "Organic available"]
    }
  ]
}
```

**MongoDB Collection:** `suppliers`

---

## Agent 2: Negotiation Agent

**Technology:** Vapi TTS + Claude API

**Purpose:** Phone vendors to gather info and negotiate prices CONCURRENTLY

**Process:**
1. Make concurrent outbound calls via Vapi
2. Ask clarifying questions about products
3. Negotiate bulk discounts (5-20% typical)
4. Negotiate long-term contract pricing
5. Request invoices to specific email

**Negotiation Strategies:**
- **Volume discount:** "We're ordering 500 lbs, what's your bulk pricing?"
- **Competitive leverage:** "Another supplier quoted us $X, can you match?"
- **Long-term commitment:** "If we commit to monthly orders, what discount?"
- **Bundle deals:** "We're also ordering eggs and butter, any package deal?"

**Vapi Call Flow:**
```
1. "Hi, I'm calling on behalf of Sweet Dreams Bakery..."
2. "We're looking to order 500 lbs of all-purpose flour..."
3. "What's your current price per pound?"
4. "We're comparing a few suppliers. Can you do better on price?"
5. "Great, please send the invoice to orders@sweetdreams.com"
```

**MongoDB Collection:** `negotiations`, `offers`

---

## Agent 3: Evaluation Agent

**Technology:** Claude API + MongoDB Vector Search

**Purpose:** Analyze all options and select optimal combination

**Evaluation Factors:**

| Factor | Weight | Description |
|--------|--------|-------------|
| Price | 35% | Total cost including shipping |
| Quality | 30% | Certifications, reviews, grade |
| Reliability | 15% | Delivery track record |
| Negotiated Discount | 10% | Additional savings achieved |
| Relationship Potential | 10% | Long-term partnership value |

**Process:**
1. Score each supplier on multi-factor criteria
2. Optimize selection within budget constraint
3. Handle partial fulfillment (split orders)
4. Generate justification for each selection
5. Contact selected vendors to request invoices

**Output:**
```json
{
  "selected_vendors": [
    {
      "vendor": "Bay Area Foods Co",
      "ingredient": "All-purpose flour",
      "quantity": "500 lbs",
      "original_price": 250.00,
      "negotiated_price": 212.50,
      "discount_pct": 15,
      "quality_score": 8.5
    }
  ],
  "total_cost": 1847.50,
  "budget": 2000.00,
  "savings": 152.50
}
```

**MongoDB Collection:** `evaluations`, `decisions`

---

## x402: Authorization & Budgeting Layer

**Technology:** x402 Protocol + Coinbase CDP Server Wallets

**Position:** Between Evaluation Agent and Payment Agent

**Purpose:** Cryptographic authorization and budget enforcement for real-world actions

> **Key Insight:** x402 is NOT a payment processor. x402 is a cryptographic "permission slip" that authorizes irreversible real-world actions. ACH is simply one example of such an action.

**Why x402 Matters:**

| What x402 IS | What x402 is NOT |
|--------------|------------------|
| Authorization layer | Payment processor |
| Budget enforcement | Stripe replacement |
| Cryptographic audit trail | Bank transfer mechanism |
| Agent-native permission protocol | Just another payment API |

**x402 Authorization Flow:**

```
Evaluation Agent: "I've selected vendors. Ready to pay $1,847.50"
        ↓
x402 AUTHORIZATION LAYER
  • Check: Is amount within budget?
  • Check: Does wallet have sufficient USDC?
  • Action: Sign cryptographic authorization
  • Output: On-chain tx hash (audit trail)
        ↓
AUTHORIZED: Proceed to execution
```

---

## Agent 4: Payment Agent (Execution Layer)

**Technology:** Claude Computer Use + Playwright

**Purpose:** Execute authorized payments through legacy rails (ACH)

**Position:** After x402 authorization layer

> **Correct Framing:** "x402 is the authorization and budgeting layer; ACH is just a legacy execution backend we have to deal with."

**x402 + Computer Use Architecture:**

```
x402 Authorization Token (from authorization layer)
        ↓
PAYMENT AGENT receives AUTHORIZED invoice
        ↓
Computer Use ACH Bridge:
  - Launch browser (Playwright)
  - Navigate to invoice payment portal
  - Claude vision analyzes page
  - Inject ACH credentials securely (AI never sees values)
  - Submit payment
  - Capture confirmation screenshot
        ↓
RESULT:
  • Vendor receives: Normal ACH payment (legacy rails)
  • We maintain: Cryptographic authorization (x402 tx hash)
  • Audit trail: On-chain proof + confirmation screenshot
```

**The Bridge Concept:** x402 becomes the universal authorization layer for AI agents, even when execution happens off-chain through legacy payment rails.

**Payment Flow:**

**Step 1: Invoice Receipt (with payment URL)**
```json
{
  "invoice_id": "INV-2026-0192",
  "vendor": "Bay Area Foods Co",
  "amount_usd": 212.50,
  "payment_url": "https://bayareafoods.com/pay/INV-2026-0192",
  "due_date": "2026-01-15"
}
```

**Step 2: x402 Authorization**
```
POST /pay-invoice

If unpaid:
HTTP/1.1 402 Payment Required
X-Payment-Amount: 212.50
X-Payment-Currency: USDC
X-Payment-Recipient: 0xYourEscrowWallet
X-Payment-Memo: BAYAREA_INV_2026_0192
```

**Step 3: Wallet Authorization**
- Agent evaluates spend rules
- Signs USDC transfer to escrow wallet
- Retries request with payment signature

**Step 4: Computer Use ACH Bridge**
```
1. Open browser to payment_url
2. Screenshot → Claude vision
3. Claude identifies: "I see an ACH payment form"
4. Fill routing number field
5. Fill account number field
6. Fill account name field
7. Click "Pay Now" button
8. Screenshot confirmation → extract confirmation number
```

**Step 5: Confirmation**
- Screenshot saved to `screenshots/INV-2026-0192-confirm.png`
- ACH confirmation number extracted: `ACH-2026-0192-BAYAREA`
- Transaction logged to MongoDB

**MongoDB Collection:** `invoices`, `payments`

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Database | MongoDB Atlas | Agent state, coordination, logging |
| AI/LLM | Claude API | Reasoning, extraction, vision |
| Web Search | Exa.ai | Semantic supplier search |
| Voice AI | Vapi | Phone calls and TTS |
| Payments | x402 + Computer Use | Authorization + browser ACH |
| Browser | Playwright | ACH payment automation |
| Backend | Python/FastAPI | API endpoints |

### Dependencies (8 packages)
```
pymongo>=4.6.0
anthropic>=0.40.0
exa-py>=1.0.0
vapi-python>=0.1.0
cdp-sdk>=0.0.5
playwright>=1.40.0
fastapi>=0.109.0
uvicorn>=0.27.0
python-dotenv>=1.0.0
```

---

## MongoDB Schema

| Collection | Purpose | Features |
|------------|---------|----------|
| `suppliers` | Vendor database | Vector Search |
| `ingredients` | Ingredient catalog | Text indexes |
| `negotiations` | Call transcripts | TTL for privacy |
| `offers` | Negotiated prices | - |
| `evaluations` | Scoring records | - |
| `decisions` | Final selections | - |
| `invoices` | Received invoices | TTL auto-cleanup |
| `payments` | Payment records | Time Series |

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Suppliers found | 10+ per ingredient |
| Concurrent phone calls | 3+ via Vapi |
| Negotiation success rate | >50% |
| x402 payments executed | 2+ |
| Budget compliance | 100% |
| Demo time | <3 minutes |

---

## Hackathon Alignment

| Criteria | How We Win |
|----------|------------|
| **Demo Impact (50%)** | Real phone calls + real payments |
| **Problem/Impact (25%)** | Clear B2B value, $$ savings |
| **Creativity (15%)** | Voice AI + x402 combination |
| **Pitch (10%)** | Compelling narrative |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Vapi calls fail | Pre-record demo calls as backup |
| x402 payment fails | Show wallet code + explain flow |
| Exa.ai rate limits | Cache supplier data beforehand |
| Network issues | Have offline demo mode |

---

**Document Status:** Ready for Implementation
**Build Time:** 8 hours
