# System Architecture
## Haggl - Technical Architecture

**Version:** 2.0
**Date:** January 10, 2026

**Related Docs:**
- [ADK Agent Setup Guide](./adk-agent-setup.md) - Complete agent configuration
- [x402 ACH Bridge Plan](./x402-ach-bridge-plan.md) - Secure payment architecture
- [Frontend Dashboard](../frontend/dashboard-overview.md) - UI/UX design

---

## Agent Development Kit (ADK)

Each agent is built using the **NVIDIA NeMo Agent Toolkit (NAT)**, an open-source framework for connecting, evaluating, and accelerating teams of AI agents:

| Agent | NAT Tools | Purpose |
|-------|-----------|---------|
| **Sourcing Agent** | `search_suppliers`, `extract_supplier_info` | Exa.ai search + data extraction |
| **Negotiation Agent** | `make_phone_call`, `get_call_transcript`, `parse_negotiation` | Vapi TTS integration |
| **Evaluation Agent** | `get_all_suppliers`, `get_all_negotiations`, `save_decision` | MongoDB queries + scoring |
| **Payment Agent** | `x402_authorize`, `inject_credentials`, browser tools | x402 + Computer Use ACH |
| **SMS Agent** | `parse_sms`, `send_sms`, `handle_approval` | Twilio SMS integration |
| **CSV Parser** | `parse_csv`, `validate_ingredients`, `save_import` | CSV ingredient ingestion |

### Why NVIDIA NeMo Agent Toolkit?

- **YAML Configuration**: Rapid prototyping with config-driven workflows
- **Framework Agnostic**: Works with LangChain, LlamaIndex, CrewAI, or raw Python
- **Multi-Agent Orchestration**: Built-in coordination and routing
- **Profiling & Observability**: Track tokens, timings, bottlenecks
- **MCP Support**: Model Context Protocol for remote tools
- **Production Ready**: Rate limiting, auth, REST API server

```bash
# Install and run
pip install "nvidia-nat[all]"
nat run --config_file configs/orchestrator.yml --input "Your query"
nat serve --config_file configs/orchestrator.yml --port 8000
```

See [adk-agent-setup.md](./adk-agent-setup.md) for complete setup instructions.

---

## x402: The Authorization & Budgeting Layer

### Key Insight

**x402 is NOT a payment processor. x402 is a cryptographic "permission slip" that authorizes irreversible real-world actions.**

ACH is simply one example of such an action. x402 becomes the **universal authorization layer for AI agents**, even when execution happens off-chain through legacy payment rails.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THE CORRECT MENTAL MODEL                         │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │                  EVALUATION AGENT                            │  │
│   │      "I've selected vendors. Total cost: $1,847.50"         │  │
│   │      "Budget remaining: $152.50"                            │  │
│   └─────────────────────────────────┬───────────────────────────┘  │
│                                     │                               │
│                                     ▼                               │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │           x402 AUTHORIZATION & BUDGETING LAYER              │  │
│   │                                                              │  │
│   │   • Cryptographic permission slip for each payment          │  │
│   │   • Enforces budget constraints (USDC in escrow wallet)     │  │
│   │   • Provides audit trail (on-chain tx hash)                 │  │
│   │   • Agent-native authorization protocol                     │  │
│   │                                                              │  │
│   │   "Is this payment within budget? → Sign authorization"    │  │
│   └─────────────────────────────────┬───────────────────────────┘  │
│                                     │                               │
│                              AUTHORIZED                             │
│                                     │                               │
│                                     ▼                               │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │              PAYMENT AGENT (Execution Layer)                 │  │
│   │                                                              │  │
│   │   Computer Use + ACH = Legacy Execution Backend              │  │
│   │   • Navigate to vendor payment portal                        │  │
│   │   • Fill ACH form (credentials injected securely)           │  │
│   │   • Submit payment through existing bank rails              │  │
│   │                                                              │  │
│   │   "Execute the authorized real-world action"                │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│   VENDOR RECEIVES: Normal ACH payment (no crypto involved)        │
│   WE MAINTAIN: Cryptographic authorization + audit trail          │
└─────────────────────────────────────────────────────────────────────┘
```

### Why This Matters

| What x402 IS | What x402 is NOT |
|--------------|------------------|
| Authorization layer | Payment processor |
| Budget enforcement | Stripe replacement |
| Cryptographic audit trail | Bank transfer mechanism |
| Agent-native permission protocol | Just another payment API |
| Universal across execution backends | Crypto-only solution |

### The Bridge Concept

**"x402 is the authorization and budgeting layer; ACH is just a legacy execution backend we have to deal with."**

This architecture enables:
- **Agent-native authorization**: AI agents get cryptographic spending limits
- **Legacy rail compatibility**: Works with any vendor (no API integration needed)
- **Future-proof**: When vendors support crypto, swap ACH for on-chain payments
- **Bridging the future to the present**: Modern authorization, legacy execution

### How to Talk About This

**Bad framing:**
> "We modified x402 to do ACH payments."

**Good framing:**
> "We use x402 to authorize real-world actions that don't have native crypto rails — ACH is one example."

**Best framing:**
> "x402 becomes the universal authorization layer for agents, even when execution happens off-chain."

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        BUSINESS OWNER INPUT                         │
│                                                                     │
│  INPUT METHODS:                                                     │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐│
│  │ Menu Upload│   │ CSV Import │   │ SMS Text   │   │ Dashboard  ││
│  │ (PDF/text) │   │(spreadsheet)│   │ (Twilio)   │   │ (Web UI)   ││
│  └─────┬──────┘   └─────┬──────┘   └─────┬──────┘   └─────┬──────┘│
│        │                │                │                │        │
│        └────────────────┴────────────────┴────────────────┘        │
│                                 │                                   │
│                                 ▼                                   │
│  Ingredients: flour, eggs, butter, sugar                           │
│  Quantities: 500 lbs, 1000 units, 100 lbs, 200 lbs                │
│  Budget: $2,000                                                     │
│  Location: San Francisco, CA                                        │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR                                │
│                    (Python async/concurrent)                        │
└─────────────────────────────────────────────────────────────────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
           ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  SOURCING       │    │  NEGOTIATION    │    │  SOURCING       │
│  (flour)        │    │  (Vendor A)     │    │  (eggs)         │
│  [exa.ai]       │    │  [Vapi call]    │    │  [exa.ai]       │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      MONGODB ATLAS                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │suppliers │ │negot-    │ │invoices  │ │payments  │              │
│  │          │ │iations   │ │          │ │          │              │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     EVALUATION AGENT                                │
│  - Scores all suppliers on quality/price                           │
│  - Optimizes within budget                                          │
│  - Selects vendors, requests invoices                               │
│  - Passes invoice list to authorization layer                       │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│          x402 AUTHORIZATION & BUDGETING LAYER                       │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  "Cryptographic permission slip for real-world actions"    │    │
│  │                                                             │    │
│  │  • Validates payment against budget (USDC in escrow)       │    │
│  │  • Signs cryptographic authorization for each invoice      │    │
│  │  • Creates on-chain audit trail (tx hash)                  │    │
│  │  • Enforces spending policies and limits                   │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  Input: Invoice list from Evaluation Agent                         │
│  Output: Cryptographic authorization tokens                        │
└─────────────────────────────────────────────────────────────────────┘
                                │
                         AUTHORIZED
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              PAYMENT AGENT (Execution Layer)                        │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  "Execute authorized actions via legacy rails"             │    │
│  │                                                             │    │
│  │  Computer Use ACH Bridge:                                  │    │
│  │  • Navigate to vendor payment portal (Playwright)          │    │
│  │  • Identify ACH form fields (Claude vision)                │    │
│  │  • Inject credentials securely (values hidden from AI)     │    │
│  │  • Submit payment, capture confirmation                    │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  VENDOR RECEIVES: Normal ACH payment (no crypto)                   │
│  WE MAINTAIN: Cryptographic authorization + full audit trail       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Agent Communication Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CONCURRENT PHASE 1                               │
│                                                                     │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐          │
│   │Source   │   │Source   │   │Source   │   │Source   │          │
│   │Flour    │   │Eggs     │   │Butter   │   │Sugar    │          │
│   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘          │
│        │             │             │             │                 │
│        └─────────────┴─────────────┴─────────────┘                 │
│                           │                                        │
│                    asyncio.gather()                                │
│                           │                                        │
│                           ▼                                        │
│                    ┌──────────────┐                                │
│                    │  MongoDB     │                                │
│                    │  suppliers   │                                │
│                    └──────────────┘                                │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CONCURRENT PHASE 2                               │
│                                                                     │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐          │
│   │Call     │   │Call     │   │Call     │   │Call     │          │
│   │Vendor A │   │Vendor B │   │Vendor C │   │Vendor D │          │
│   │[Vapi]   │   │[Vapi]   │   │[Vapi]   │   │[Vapi]   │          │
│   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘          │
│        │             │             │             │                 │
│        └─────────────┴─────────────┴─────────────┘                 │
│                           │                                        │
│                    asyncio.gather()                                │
│                           │                                        │
│                           ▼                                        │
│                    ┌──────────────┐                                │
│                    │  MongoDB     │                                │
│                    │  negotiations│                                │
│                    └──────────────┘                                │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SEQUENTIAL PHASE 3: EVALUATION                   │
│                                                                     │
│                    ┌──────────────┐                                │
│                    │  EVALUATION  │                                │
│                    │  AGENT       │                                │
│                    │              │                                │
│                    │ - Read all   │                                │
│                    │   suppliers  │                                │
│                    │ - Read all   │                                │
│                    │   negot.     │                                │
│                    │ - Optimize   │                                │
│                    │ - Select     │                                │
│                    │ - Request    │                                │
│                    │   invoices   │                                │
│                    └──────────────┘                                │
│                                                                     │
│   Output: Invoice list ready for authorization                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              PHASE 3.5: x402 AUTHORIZATION LAYER                    │
│                                                                     │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │  For each invoice:                                          │   │
│   │                                                             │   │
│   │  Invoice ──▶ Budget Check ──▶ Sign Authorization ──▶ Store │   │
│   │     │            │                    │                     │   │
│   │     ▼            ▼                    ▼                     │   │
│   │  $212.50    Wallet has     Cryptographic tx hash           │   │
│   │             sufficient      0x8f3e7b2a...                   │   │
│   │             USDC?                                           │   │
│   └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│   "Permission slip granted — proceed to execution"                 │
└─────────────────────────────────────────────────────────────────────┘
                                │
                         AUTHORIZED
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│           SEQUENTIAL PHASE 4: PAYMENT EXECUTION                     │
│                                                                     │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │  For each AUTHORIZED invoice:                               │   │
│   │                                                             │   │
│   │  Auth Token ──▶ Browser ──▶ ACH Form ──▶ Submit ──▶ Log   │   │
│   │       │            │           │           │                │   │
│   │       ▼            ▼           ▼           ▼                │   │
│   │  0x8f3e...    Playwright   Claude      Confirm             │   │
│   │               opens URL    fills form  screenshot           │   │
│   └────────────────────────────────────────────────────────────┘   │
│                                                                     │
│   VENDOR: Receives normal ACH (legacy rails)                       │
│   AUDIT:  On-chain authorization + confirmation screenshot         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## x402 Authorization + Legacy Execution (Detailed)

> **Key Insight:** x402 authorizes the action. Computer Use + ACH executes it through legacy rails.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    INVOICE FLOW                                     │
│                                                                     │
│   Vendor Email ──▶ Email Parser ──▶ Invoice DB                     │
│        │                                                            │
│        ▼                                                            │
│   ┌──────────────────────────────────────────────────────────┐     │
│   │  {                                                        │     │
│   │    "invoice_id": "INV-2026-0192",                        │     │
│   │    "vendor": "Bay Area Foods Co",                         │     │
│   │    "amount_usd": 212.50,                                  │     │
│   │    "payment_url": "https://vendor.com/pay/INV-2026-0192",│     │
│   │    "due_date": "2026-01-15"                              │     │
│   │  }                                                        │     │
│   └──────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    x402 AUTHORIZATION                               │
│                                                                     │
│   POST /pay-invoice                                                 │
│                                                                     │
│   Request without payment:                                          │
│   ┌──────────────────────────────────────────────────────────┐     │
│   │  HTTP/1.1 402 Payment Required                           │     │
│   │  X-Payment-Amount: 212.50                                │     │
│   │  X-Payment-Currency: USDC                                │     │
│   │  X-Payment-Recipient: 0xYourEscrowWallet                 │     │
│   │  X-Payment-Memo: BAYAREA_INV_2026_0192                   │     │
│   └──────────────────────────────────────────────────────────┘     │
│                                                                     │
│   Request with payment signature:                                   │
│   ┌──────────────────────────────────────────────────────────┐     │
│   │  HTTP/1.1 200 OK                                         │     │
│   │  { "status": "authorized", "tx_hash": "0x8f3e..." }     │     │
│   │  → Triggers Computer Use ACH Bridge                      │     │
│   └──────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│        LEGACY EXECUTION: Computer Use ACH Bridge                    │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────┐      │
│   │  PREREQUISITE: x402 authorization token received        │      │
│   │                                                          │      │
│   │  1. Launch browser (Playwright headless=False for demo) │      │
│   │  2. Navigate to invoice payment_url                     │      │
│   │  3. Screenshot + send to Claude vision                  │      │
│   │  4. Claude identifies ACH payment form elements         │      │
│   │  5. Inject credentials securely (AI never sees values): │      │
│   │     - Routing Number: injected from secure vault        │      │
│   │     - Account Number: injected from secure vault        │      │
│   │     - Account Name: injected from secure vault          │      │
│   │  6. Click submit/pay button                             │      │
│   │  7. Screenshot confirmation page                        │      │
│   │  8. Extract confirmation number via Claude              │      │
│   └─────────────────────────────────────────────────────────┘      │
│                                                                     │
│   RESULT:                                                           │
│   • Vendor receives: Normal ACH payment (legacy banking rails)     │
│   • We maintain: Cryptographic authorization (x402 tx hash)        │
│   • Audit trail: On-chain proof + confirmation screenshot          │
└─────────────────────────────────────────────────────────────────────┘
```

### Computer Use Tool Loop

```
┌──────────────────────────────────────────────────────────────┐
│                    CLAUDE COMPUTER USE LOOP                  │
│                                                              │
│   ┌────────────┐                                            │
│   │ Screenshot │ ◀─────────────────────────────┐            │
│   └─────┬──────┘                               │            │
│         │                                      │            │
│         ▼                                      │            │
│   ┌────────────┐                               │            │
│   │ Claude     │    "I see an ACH form.       │            │
│   │ Vision     │    I need to fill routing    │            │
│   │ Analysis   │    number field..."          │            │
│   └─────┬──────┘                               │            │
│         │                                      │            │
│         ▼                                      │            │
│   ┌────────────┐                               │            │
│   │ Tool Call  │    click(x=245, y=312)       │            │
│   │ (Playwright)│    type("021000021")        │            │
│   └─────┬──────┘                               │            │
│         │                                      │            │
│         ▼                                      │            │
│   ┌────────────┐                               │            │
│   │ Execute    │───────────────────────────────┘            │
│   │ Action     │    Loop until payment confirmed            │
│   └────────────┘                                            │
└──────────────────────────────────────────────────────────────┘
```

---

## MongoDB Collections

### suppliers
```javascript
{
  _id: ObjectId(),
  vendor_name: "Bay Area Foods Co",
  ingredients: ["flour", "sugar", "baking powder"],
  contact: {
    phone: "+1-415-555-0123",
    email: "orders@bayareafoods.com"
  },
  location: "Oakland, CA",
  pricing: {
    "flour": { price: 0.45, unit: "lb", moq: 100 }
  },
  quality_score: 8.5,
  certifications: ["FDA", "Organic"],
  embedding: [0.1, 0.2, ...],  // Vector Search
  last_updated: ISODate()
}
```

### negotiations
```javascript
{
  _id: ObjectId(),
  vendor: "Bay Area Foods Co",
  call_id: "vapi_call_123",
  transcript: "...",
  outcome: "success",
  original_price: 0.50,
  negotiated_price: 0.425,
  discount_pct: 15,
  terms: "Monthly orders, net-30",
  timestamp: ISODate(),
  expireAt: ISODate()  // TTL: 30 days
}
```

### invoices
```javascript
{
  _id: ObjectId(),
  invoice_id: "INV-2026-0192",
  vendor: "Bay Area Foods Co",
  amount_usd: 212.50,
  payment_url: "https://vendor.com/pay/INV-2026-0192",  // For Computer Use
  due_date: ISODate(),
  status: "pending",  // pending | paid | failed
  received_at: ISODate()
}
```

### payments
```javascript
{
  _id: ObjectId(),
  invoice_id: "INV-2026-0192",
  vendor: "Bay Area Foods Co",
  amount_usd: 212.50,
  x402_tx_hash: "0x8f3e...",           // On-chain authorization
  x402_explorer: "https://basescan.org/tx/0x8f3e...",
  payment_method: "computer_use_ach",   // Computer Use ACH bridge
  ach_confirmation: "ACH123456789",     // Confirmation from portal
  screenshot_url: "/screenshots/INV-2026-0192-confirm.png",
  status: "completed",
  timestamp: ISODate()
}
```

---

## API Endpoints

### FastAPI Backend

```python
from fastapi import FastAPI, HTTPException, Header

app = FastAPI()

@app.post("/search-suppliers")
async def search_suppliers(request: SupplierSearchRequest):
    """Sourcing Agent: Find suppliers via Exa.ai"""
    suppliers = await sourcing_agent.search(request.ingredients)
    return {"suppliers": suppliers}

@app.post("/negotiate")
async def negotiate(request: NegotiationRequest):
    """Negotiation Agent: Make Vapi call to vendor"""
    result = await negotiation_agent.call(request.vendor)
    return {"negotiation": result}

@app.post("/evaluate")
async def evaluate(request: EvaluationRequest):
    """Evaluation Agent: Score and select best vendors"""
    selection = await evaluation_agent.optimize(request.budget)
    return {"selection": selection}

@app.post("/pay-invoice")
async def pay_invoice(
    request: PaymentRequest,
    x_payment_signature: str = Header(None)
):
    """Payment Agent: x402-protected payment endpoint with Computer Use ACH"""

    if not x_payment_signature:
        # Return 402 Payment Required
        raise HTTPException(
            status_code=402,
            headers={
                "X-Payment-Amount": str(request.amount),
                "X-Payment-Currency": "USDC",
                "X-Payment-Recipient": ESCROW_WALLET,
                "X-Payment-Memo": request.invoice_id
            }
        )

    # Verify x402 payment
    if not verify_x402_signature(x_payment_signature):
        raise HTTPException(status_code=401)

    # Execute payment via Computer Use ACH Bridge
    from computer_use.ach_bridge import execute_ach_payment
    result = await execute_ach_payment(
        payment_url=request.payment_url,
        amount=request.amount,
        invoice_id=request.invoice_id
    )
    return {"payment": result}
```

---

## SMS Integration (Twilio)

### SMS Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      SMS BOT ARCHITECTURE                            │
│                                                                     │
│   BUSINESS OWNER                                                    │
│        │                                                            │
│        │ SMS: "Reorder flour"                                      │
│        ▼                                                            │
│   ┌─────────────┐                                                  │
│   │   Twilio    │ ───────────────────────────────────┐             │
│   │   Gateway   │                                    │             │
│   └─────────────┘                                    │             │
│        │                                              │             │
│        │ Webhook POST /sms/webhook                   │             │
│        ▼                                              │             │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │                    SMS AGENT                                 │  │
│   │                                                              │  │
│   │  1. Parse intent (Claude NLU)                               │  │
│   │  2. Look up order history (MongoDB)                          │  │
│   │  3. Execute action:                                          │  │
│   │     - REORDER: Fetch last order, trigger procurement         │  │
│   │     - NEW ORDER: Parse items, start sourcing                 │  │
│   │     - APPROVE/DENY: Update pending_approvals, proceed/cancel │  │
│   │     - STATUS: Query current order state                      │  │
│   │  4. Send response SMS                                        │  │
│   │                                                              │  │
│   └─────────────────────────────────────────────────────────────┘  │
│        │                                                            │
│        │ Response SMS                                               │
│        ▼                                                            │
│   BUSINESS OWNER: "✓ Order placed! Tracking: #HGL-2026-0192"      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### SMS Commands & Handlers

```python
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

# Initialize Twilio
twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

@app.post("/sms/webhook")
async def handle_sms(From: str, Body: str):
    """Twilio webhook for incoming SMS"""

    # Parse intent using Claude
    intent = await parse_sms_intent(Body, From)

    if intent["type"] == "reorder":
        result = await handle_reorder(From, intent["ingredient"])
    elif intent["type"] == "new_order":
        result = await handle_new_order(From, intent["items"])
    elif intent["type"] == "approve":
        result = await handle_approval(From, approved=True)
    elif intent["type"] == "deny":
        result = await handle_approval(From, approved=False)
    elif intent["type"] == "status":
        result = await get_order_status(From)
    elif intent["type"] == "budget":
        result = await get_budget_status(From)
    else:
        result = "Commands: ORDER, REORDER, APPROVE, DENY, STATUS, BUDGET, HELP"

    # Send response via TwiML
    response = MessagingResponse()
    response.message(result)
    return str(response)


async def parse_sms_intent(message: str, phone: str) -> dict:
    """Use Claude to parse SMS intent"""

    prompt = f"""Parse this SMS message from a business owner ordering supplies.

MESSAGE: {message}

Return JSON with:
- type: "reorder" | "new_order" | "approve" | "deny" | "status" | "budget" | "help" | "unknown"
- ingredient: string (if reorder)
- items: list of {{name, quantity, unit}} (if new_order)
- confidence: 0-1

JSON:"""

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.content[0].text)


async def handle_reorder(phone: str, ingredient: str) -> str:
    """Handle reorder request"""

    # Find last order for this ingredient
    last_order = db.order_history.find_one(
        {"phone": phone, "ingredient": {"$regex": ingredient, "$options": "i"}},
        sort=[("timestamp", -1)]
    )

    if not last_order:
        return f"No previous order found for {ingredient}. Try: ORDER 500 lbs flour"

    # Create pending approval
    approval_id = db.pending_approvals.insert_one({
        "phone": phone,
        "type": "reorder",
        "order": last_order,
        "expires_at": datetime.now() + timedelta(hours=24)
    }).inserted_id

    return f"Reorder {last_order['quantity']} {last_order['ingredient']} from {last_order['vendor']} @ ${last_order['price']:.2f}? Reply APPROVE or DENY"


async def handle_approval(phone: str, approved: bool) -> str:
    """Handle approval/denial of pending purchase"""

    pending = db.pending_approvals.find_one_and_delete({"phone": phone})

    if not pending:
        return "No pending approval found."

    if approved:
        # Trigger procurement
        await trigger_procurement(pending["order"])
        return f"✓ Approved! Processing order for {pending['order']['ingredient']}..."
    else:
        return "✗ Order cancelled."
```

### SMS Approval Flow for Payments

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SMS PAYMENT APPROVAL FLOW                         │
│                                                                     │
│   EVALUATION AGENT                                                  │
│   "Ready to pay $1,847.50 across 4 vendors"                        │
│        │                                                            │
│        ▼                                                            │
│   ┌─────────────┐                                                  │
│   │ Check if    │                                                  │
│   │ amount >    │ ── YES ──▶ ┌─────────────────────────────────┐  │
│   │ threshold   │            │ CREATE PENDING APPROVAL          │  │
│   └─────────────┘            │ SMS: "⚠️ Large purchase: $1,847  │  │
│        │                     │ Reply APPROVE or DENY"           │  │
│        │ NO                  └─────────────────────────────────┘  │
│        ▼                                    │                      │
│   AUTO-APPROVE                              │ Wait for reply       │
│   (under threshold)                         ▼                      │
│        │                     ┌─────────────────────────────────┐  │
│        │                     │ OWNER REPLIES: "APPROVE"        │  │
│        │                     └─────────────────────────────────┘  │
│        │                                    │                      │
│        └────────────────────────────────────┘                      │
│                              │                                      │
│                              ▼                                      │
│                    x402 AUTHORIZATION + PAYMENT                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**MongoDB Collection:** `sms_conversations`, `pending_approvals`, `sms_logs`

---

## CSV Ingredient Ingestion

### CSV Parser Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CSV INGESTION FLOW                                │
│                                                                     │
│   INPUT SOURCES:                                                    │
│   ┌────────────┐   ┌────────────┐   ┌────────────┐                │
│   │ File Upload│   │ Google     │   │ Email      │                │
│   │ (Dashboard)│   │ Sheets URL │   │ Attachment │                │
│   └─────┬──────┘   └─────┬──────┘   └─────┬──────┘                │
│         │                │                │                        │
│         └────────────────┴────────────────┘                        │
│                          │                                          │
│                          ▼                                          │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │                    CSV PARSER                                │  │
│   │                                                              │  │
│   │  1. Detect format (headers, delimiters)                     │  │
│   │  2. Map columns to schema:                                  │  │
│   │     - ingredient (required)                                 │  │
│   │     - quantity (required)                                   │  │
│   │     - unit (optional, inferred)                            │  │
│   │     - quality (optional)                                    │  │
│   │     - priority (optional)                                   │  │
│   │  3. Validate data types                                     │  │
│   │  4. Normalize units (lbs, kg, units, etc.)                 │  │
│   │  5. Return structured ingredient list                       │  │
│   │                                                              │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                          │                                          │
│                          ▼                                          │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │  STRUCTURED OUTPUT:                                          │  │
│   │  [                                                           │  │
│   │    {"name": "flour", "quantity": "500 lbs", "quality": ...} │  │
│   │    {"name": "eggs", "quantity": "1000 units", ...}          │  │
│   │  ]                                                           │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                          │                                          │
│                          ▼                                          │
│                    SOURCING AGENT                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### CSV Processing Implementation

```python
import csv
from io import StringIO
from typing import List, Dict

class CSVIngestionProcessor:
    """Process CSV files into structured ingredient lists"""

    REQUIRED_COLUMNS = ["ingredient"]
    OPTIONAL_COLUMNS = ["quantity", "unit", "quality", "priority", "notes"]

    # Common column name mappings
    COLUMN_ALIASES = {
        "item": "ingredient",
        "product": "ingredient",
        "name": "ingredient",
        "qty": "quantity",
        "amount": "quantity",
        "grade": "quality",
        "type": "quality"
    }

    async def process_csv(self, csv_content: str) -> List[Dict]:
        """Parse CSV content and return ingredient list"""

        # Detect delimiter
        dialect = csv.Sniffer().sniff(csv_content[:1024])
        reader = csv.DictReader(StringIO(csv_content), dialect=dialect)

        # Normalize column names
        reader.fieldnames = [self._normalize_column(col) for col in reader.fieldnames]

        ingredients = []
        for row in reader:
            ingredient = self._parse_row(row)
            if ingredient:
                ingredients.append(ingredient)

        # Log import
        db.csv_imports.insert_one({
            "timestamp": datetime.now(),
            "row_count": len(ingredients),
            "ingredients": [i["name"] for i in ingredients]
        })

        return ingredients

    def _normalize_column(self, col: str) -> str:
        """Normalize column name to standard schema"""
        col_lower = col.lower().strip()
        return self.COLUMN_ALIASES.get(col_lower, col_lower)

    def _parse_row(self, row: Dict) -> Dict:
        """Parse single row into ingredient dict"""

        if not row.get("ingredient"):
            return None

        # Parse quantity and unit
        quantity, unit = self._parse_quantity(row.get("quantity", "1"))

        return {
            "name": row["ingredient"].strip(),
            "quantity": f"{quantity} {unit}",
            "quality": row.get("quality", "standard").strip(),
            "priority": row.get("priority", "medium").strip(),
            "notes": row.get("notes", "").strip()
        }

    def _parse_quantity(self, qty_str: str) -> tuple:
        """Parse quantity string like '500 lbs' into (500, 'lbs')"""
        import re

        match = re.match(r'(\d+(?:\.\d+)?)\s*(\w+)?', str(qty_str).strip())
        if match:
            quantity = float(match.group(1))
            unit = match.group(2) or "units"
            return quantity, unit

        return 1, "units"
```

### Sample CSV Formats Supported

**Format 1: Full Detail**
```csv
ingredient,quantity,unit,quality,priority
All-purpose flour,500,lbs,commercial grade,high
Eggs,1000,units,cage-free Grade A,high
Butter,100,lbs,unsalted,medium
```

**Format 2: Minimal**
```csv
item,qty
flour,500 lbs
eggs,1000
butter,100 lbs
```

**Format 3: With Notes**
```csv
product,amount,grade,notes
Flour,500 lbs,organic,Need by Friday
Eggs,1000 units,cage-free,Weekly delivery preferred
```

**MongoDB Collection:** `csv_imports`, `ingredient_templates`

---

## Vapi Integration

### Assistant Configuration

```python
vapi_assistant = {
    "name": "Haggl Negotiator",
    "model": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "systemPrompt": """You are a professional procurement agent calling
        on behalf of a small business. Your goals are:
        1. Confirm product availability and current pricing
        2. Negotiate bulk discounts (aim for 10-20% off)
        3. Discuss long-term contract options
        4. Request invoice to be sent to specific email

        Be professional, friendly, and persistent but not pushy."""
    },
    "voice": {
        "provider": "11labs",
        "voiceId": "professional-male"
    },
    "firstMessage": "Hi, I'm calling on behalf of Sweet Dreams Bakery regarding a bulk ingredient order."
}
```

### Call Execution

```python
async def make_negotiation_call(vendor: dict) -> dict:
    """Make concurrent Vapi call to vendor"""

    call = await vapi.calls.create(
        assistant_id=ASSISTANT_ID,
        phone_number=vendor["phone"],
        metadata={
            "vendor": vendor["name"],
            "ingredient": vendor["ingredient"],
            "quantity": vendor["quantity"]
        }
    )

    # Wait for call completion
    result = await vapi.calls.wait(call.id, timeout=300)

    return {
        "call_id": call.id,
        "transcript": result.transcript,
        "outcome": parse_negotiation_outcome(result.transcript),
        "duration": result.duration
    }
```

---

## Exa.ai Integration

### Search Implementation

```python
from exa_py import Exa

exa = Exa(api_key=os.getenv("EXA_API_KEY"))

async def search_suppliers(ingredient: str, location: str) -> list:
    """Search for suppliers using Exa semantic search"""

    query = f"wholesale {ingredient} supplier near {location} pricing bulk order"

    results = exa.search_and_contents(
        query,
        type="neural",
        num_results=10,
        text=True,
        highlights=True
    )

    suppliers = []
    for result in results.results:
        # Extract structured data via Claude
        extracted = await extract_supplier_info(result.text)
        suppliers.append({
            "source_url": result.url,
            "title": result.title,
            **extracted
        })

    return suppliers
```

---

## Concurrent Execution

### Main Orchestrator

```python
import asyncio

async def process_order(order: Order) -> dict:
    """Main orchestrator - runs agents concurrently where possible"""

    # PHASE 1: Concurrent sourcing for all ingredients
    print("[PHASE 1] Sourcing suppliers concurrently...")
    sourcing_tasks = [
        sourcing_agent.search(ingredient)
        for ingredient in order.ingredients
    ]
    all_suppliers = await asyncio.gather(*sourcing_tasks)

    # Flatten and save to MongoDB
    suppliers = [s for batch in all_suppliers for s in batch]
    await db.suppliers.insert_many(suppliers)

    # PHASE 2: Concurrent negotiations with top suppliers
    print("[PHASE 2] Negotiating with vendors concurrently...")
    top_suppliers = select_top_suppliers(suppliers, per_ingredient=3)

    negotiation_tasks = [
        negotiation_agent.call(supplier)
        for supplier in top_suppliers
    ]
    negotiations = await asyncio.gather(*negotiation_tasks)

    # Save negotiations to MongoDB
    await db.negotiations.insert_many(negotiations)

    # PHASE 3: Evaluation (sequential - needs all data)
    print("[PHASE 3] Evaluating and selecting best combination...")
    selection = await evaluation_agent.optimize(
        suppliers=suppliers,
        negotiations=negotiations,
        budget=order.budget
    )

    # Request invoices from selected vendors
    invoice_tasks = [
        evaluation_agent.request_invoice(vendor)
        for vendor in selection.vendors
    ]
    await asyncio.gather(*invoice_tasks)

    # PHASE 4: Payment processing
    print("[PHASE 4] Processing payments via x402...")
    invoices = await db.invoices.find({"status": "pending"}).to_list()

    for invoice in invoices:
        await payment_agent.process(invoice)

    return {
        "suppliers_found": len(suppliers),
        "negotiations_completed": len(negotiations),
        "vendors_selected": len(selection.vendors),
        "total_cost": selection.total_cost,
        "savings": selection.savings
    }
```

---

## File Structure

```
haggl/
├── main.py                    # Entry point & CLI
├── orchestrator.py            # Concurrent execution logic
├── agents/
│   ├── __init__.py
│   ├── sourcing.py           # Exa.ai integration
│   ├── negotiation.py        # Vapi integration
│   ├── evaluation.py         # Scoring & optimization
│   ├── payment.py            # x402 + Computer Use bridge
│   └── sms.py                # SMS agent (Twilio)
├── ingestion/
│   ├── __init__.py
│   ├── csv_parser.py         # CSV ingredient ingestion
│   ├── menu_parser.py        # Menu upload parsing
│   └── validators.py         # Input validation
├── sms/
│   ├── __init__.py
│   ├── handler.py            # SMS webhook handler
│   ├── commands.py           # Command parsing & execution
│   └── approval.py           # SMS approval flow
├── computer_use/
│   ├── __init__.py
│   ├── browser.py            # Playwright browser controller
│   ├── ach_bridge.py         # ACH payment automation
│   └── tools.py              # Computer use tool definitions
├── api/
│   ├── __init__.py
│   ├── server.py             # FastAPI endpoints
│   ├── x402.py               # x402 middleware
│   └── sms_webhook.py        # Twilio SMS webhook
├── utils/
│   ├── __init__.py
│   ├── mongo.py              # MongoDB client
│   └── config.py             # Environment config
├── frontend/                  # Dashboard UI (see frontend docs)
├── screenshots/               # Payment confirmation screenshots
├── .env                       # API keys
├── requirements.txt           # Dependencies
└── README.md                  # Setup guide
```

---

**Architecture Status:** Ready for Implementation