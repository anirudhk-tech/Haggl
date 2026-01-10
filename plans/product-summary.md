# Product Summary
## Haggl - One-Page Overview

**Tagline:** AI agents that source, negotiate, and pay for your business supplies autonomously

---

## What It Is

Haggl is a multi-agent AI system for B2B procurement. A business owner inputs their ingredient needs via **menu upload, CSV import, or SMS text**, sets their budget, and Haggl handles the rest. Four specialized agents work **concurrently** to find suppliers, negotiate prices via real phone calls, evaluate options, and process payments using the x402 protocol.

**New in v2.0:**
- **SMS Ordering** - Text to reorder, place new orders, or approve purchases
- **CSV Import** - Bulk upload ingredients from any spreadsheet
- **Preferred Vendor** - Auto-fill vendor from past orders

---

## The Problem

- **Time-Intensive:** Small business owners spend 5-10 hours/week sourcing suppliers
- **No Leverage:** Individual businesses can't negotiate bulk discounts
- **Manual Comparison:** Spreadsheets across dozens of vendors
- **Fragmented Payments:** Multiple invoices, methods, reconciliation

---

## The Solution

### 4 Concurrent AI Agents

**1. Sourcing Agent (Exa.ai)**
- Semantic web search for suppliers
- Extracts pricing, MOQs, shipping via Claude
- Finds 10+ suppliers per ingredient

**2. Negotiation Agent (Vapi TTS)**
- Makes REAL phone calls to vendors
- Negotiates bulk discounts (10-20% typical)
- Runs calls CONCURRENTLY
- Requests invoices to specific email

**3. Evaluation Agent**
- Scores quality vs price
- Optimizes within budget constraint
- Selects best combination
- Passes invoices to authorization layer

**3.5. x402 Authorization Layer**
- Cryptographic "permission slip" for each payment
- Enforces budget constraints (USDC in escrow)
- Creates on-chain audit trail
- **NOT a payment processor — an authorization layer**

**4. Payment Agent (Execution Layer)**
- Receives AUTHORIZED invoices from x402
- Claude Computer Use navigates payment portal
- Securely injects ACH credentials (AI never sees values)
- Submits payment, captures confirmation screenshot

---

## Key Innovation

### Agent-Native Authorization + Legacy Execution

> "x402 is the authorization and budgeting layer; ACH is just a legacy execution backend we have to deal with."

**What makes this powerful:**
- **x402** = Cryptographic authorization for AI agents
- **ACH** = Legacy execution backend (works with ANY vendor)
- **Result** = Bridging the future to the present

Most AI demos can't negotiate OR pay. Haggl does BOTH:
- **Real phone calls** via Vapi TTS
- **x402 authorization** — cryptographic spending limits for agents
- **Legacy execution** via Computer Use (browser ACH)
- **Visual demo** - watch AI authorize and pay through any portal

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Database | MongoDB Atlas |
| AI/LLM | Claude API (vision) |
| Web Search | Exa.ai |
| Voice AI | Vapi |
| **SMS** | **Twilio** |
| Payments | x402 + Computer Use |
| Browser | Playwright |

**Dependencies:** 11 packages

---

## Demo Flow (3 minutes)

### Option A: CLI Demo
```bash
$ python main.py --ingredients flour eggs butter --budget 2000

[PHASE 1] Sourcing suppliers concurrently...
  Found 12 potential suppliers

[PHASE 2] Negotiating with vendors...
  Calling Bay Area Foods Co...
    Negotiated 15% bulk discount
  Completed 6 calls, 4 successful

[PHASE 3] Evaluating best combination...
  Selected 3 vendors
  Total: $1,450 | Budget: $2,000

[PHASE 3.5] x402 AUTHORIZATION...
  📋 Invoice: Bay Area Foods Co - $212.50
  🔐 Budget check: $212.50 < $2,000 ✓
  ✍️  Signing authorization...
  ✅ x402 Auth: 0x8f3e7b2a... (on-chain)

[PHASE 4] EXECUTING payments via legacy rails...
  🖥️ Opening browser to payment portal...
  Step 1: Clicking ACH payment option
  Step 2: Injecting credentials securely
  Step 3: Clicking submit
  📸 Confirmation screenshot captured
  ✅ ACH Confirmation: ACH-2026-0192

ORDER COMPLETE!
Authorization: x402 (cryptographic)
Execution: ACH (legacy rails)
Savings: $550 (27%)
```

### Option B: SMS Demo
```
📱 Owner texts: "Reorder flour"

📱 Haggl responds: "Reorder 500 lbs all-purpose flour from Bay Area Foods @ $0.425/lb ($212.50)? Reply APPROVE or DENY"

📱 Owner texts: "APPROVE"

📱 Haggl responds: "✓ Order placed! x402 TX: 0x8f3e... ETA: Jan 12"
```

### Option C: CSV Import Demo
```bash
$ curl -X POST http://localhost:8000/upload/csv -F "file=@ingredients.csv"

{
  "status": "success",
  "ingredients": [
    {"name": "flour", "quantity": "500 lbs"},
    {"name": "eggs", "quantity": "1000 units"}
  ],
  "message": "2 ingredients imported. Starting sourcing..."
}
```

---

## MongoDB Collections

| Collection | Purpose |
|------------|---------|
| `suppliers` | Vendor database |
| `negotiations` | Call transcripts |
| `invoices` | Received invoices |
| `payments` | Payment records |

---

## Hackathon Alignment

- **Demo Impact (50%):** Real phone calls + real payments
- **Problem/Impact (25%):** Clear B2B value, $$ savings
- **Creativity (15%):** Voice AI + x402 combination
- **Pitch (10%):** Compelling narrative

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Suppliers found | 10+ |
| Phone calls | 3+ concurrent |
| Negotiation success | >50% |
| x402 payments | 2+ |
| Demo time | <3 minutes |

---

## Competitive Advantage

**vs. Manual Sourcing:**
- Hours → Minutes
- No negotiation → AI negotiates

**vs. Other Procurement Tools:**
- Require human approval → Fully autonomous
- No phone negotiation → Real Vapi calls

**vs. Other AI Demos:**
- Mock payments → Real x402 + Computer Use payments
- Text only → Voice + vision + browser automation
- API only → Works with ANY vendor portal

---

**Status:** Ready for Implementation
**Build Time:** 8 hours
