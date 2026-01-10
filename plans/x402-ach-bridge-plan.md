# x402 Authorization Layer + Legacy Execution Bridge
## Secure Autonomous Payment Authorization & Execution

**Version:** 2.0
**Date:** January 10, 2026
**Status:** Novel Implementation — Ready to Build

**New in v2.0:**
- SMS-based approval flow for large purchases
- Owner can approve/deny payments via text message

---

## Project Context (For Standalone Implementation)

This document is designed to be used independently to build the x402 + ACH payment layer. Below is the context you need.

### What is Haggl?

Haggl is a multi-agent B2B procurement system. A business owner inputs ingredient needs, quantities, and budget. Four agents work concurrently:

```
USER INPUT: "500 lbs flour, 1000 eggs, budget $2,000"
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 1: SOURCING (Exa.ai + Claude)                            │
│  • Semantic search for wholesale suppliers                      │
│  • Extract pricing, MOQs, contact info                          │
│  • Output: List of potential suppliers per ingredient           │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 2: NEGOTIATION (Vapi TTS)                                │
│  • Real phone calls to vendors (concurrent)                     │
│  • Negotiate bulk discounts (10-20% typical)                    │
│  • Request invoices to orders@business.com                      │
│  • Output: Negotiation transcripts, agreed prices               │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 3: EVALUATION (Claude + MongoDB)                         │
│  • Score all suppliers on price/quality/reliability             │
│  • Optimize vendor selection within budget                      │
│  • Request invoices from selected vendors                       │
│  • Output: Selected vendors + invoice list                      │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────┐
        │  THIS DOCUMENT COVERS EVERYTHING BELOW  │
        └─────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  x402 AUTHORIZATION LAYER (This Document - Phase 3.5)          │
│  • Receive invoice list from Evaluation Agent                  │
│  • Validate each invoice against budget                         │
│  • Sign cryptographic authorization (USDC escrow)               │
│  • Output: Authorization tokens with on-chain tx hashes        │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 4: PAYMENT EXECUTION (This Document - Phase 4)          │
│  • Receive AUTHORIZED invoices only                             │
│  • Navigate vendor payment portal (Computer Use)                │
│  • Inject ACH credentials securely                              │
│  • Submit payment, capture confirmation                         │
│  • Output: Payment confirmations + screenshots                  │
└─────────────────────────────────────────────────────────────────┘
```

### What You're Building

This document covers:
1. **x402 Authorization Layer** — Cryptographic budget enforcement between Evaluation and Payment agents
2. **ACH Execution Bridge** — Computer Use automation to execute payments through vendor portals

### Input You'll Receive

From the Evaluation Agent, you receive a list of invoices:

```python
# Invoice structure from Evaluation Agent
invoices = [
    {
        "invoice_id": "INV-2026-0192",
        "vendor": "Bay Area Foods Co",
        "amount_usd": 212.50,
        "payment_url": "https://bayareafoods.com/pay/INV-2026-0192",
        "due_date": "2026-01-15",
        "ingredient": "flour",
        "quantity": "500 lbs"
    },
    {
        "invoice_id": "INV-2026-0193",
        "vendor": "Farm Fresh Eggs",
        "amount_usd": 450.00,
        "payment_url": "https://farmfresh.com/invoice/0193",
        "due_date": "2026-01-16",
        "ingredient": "eggs",
        "quantity": "1000 units"
    }
]

# Budget context
budget = {
    "total_budget": 2000.00,
    "total_invoice_amount": 1847.50,
    "remaining": 152.50
}
```

### Output You'll Produce

```python
# Payment results
payment_results = [
    {
        "invoice_id": "INV-2026-0192",
        "vendor": "Bay Area Foods Co",
        "amount_usd": 212.50,
        "x402_authorization": {
            "tx_hash": "0x8f3e7b2a...",
            "explorer_url": "https://basescan.org/tx/0x8f3e7b2a...",
            "timestamp": "2026-01-10T14:32:00Z"
        },
        "ach_execution": {
            "confirmation_number": "ACH-2026-0192",
            "screenshot_path": "screenshots/INV-2026-0192-confirm.png",
            "status": "completed"
        }
    }
]
```

### Tech Stack Context

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Authorization** | x402 Protocol + Coinbase CDP | Cryptographic budget enforcement |
| **Wallet** | CDP Server Wallet (USDC on Base) | Holds authorization budget |
| **Browser** | Playwright | Payment portal automation |
| **Vision** | Claude API (claude-sonnet-4-20250514) | Analyze payment forms |
| **Database** | MongoDB Atlas | Store payment records |
| **Credentials** | Environment variables (encrypted) | ACH routing/account numbers |

### Dependencies

```bash
pip install cdp-sdk anthropic playwright pymongo python-dotenv
playwright install chromium
```

### Environment Variables Needed

```bash
# Coinbase CDP
CDP_API_KEY_NAME=your_key_name
CDP_API_KEY_PRIVATE_KEY=your_private_key

# Or use JSON config
# cdp_api_key.json

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# MongoDB
MONGODB_URI=mongodb+srv://...

# ACH Credentials (NEVER expose to AI)
ACH_ROUTING_NUMBER=021000021
ACH_ACCOUNT_NUMBER=1234567890
ACH_ACCOUNT_NAME=Sweet Dreams Bakery

# Escrow Wallet
ESCROW_WALLET_ADDRESS=0x...
```

---

## The Correct Mental Model

> **x402 is NOT a payment processor. x402 is a cryptographic "permission slip" that authorizes irreversible real-world actions.**

**Bad framing:** "We modified x402 to do ACH payments."

**Good framing:** "We use x402 to authorize real-world actions that don't have native crypto rails — ACH is one example."

**Best framing:** "x402 becomes the universal authorization layer for agents, even when execution happens off-chain."

---

## Executive Summary

This document outlines a secure architecture where **x402 serves as the authorization and budgeting layer**, with ACH as a legacy execution backend. The separation is critical:

| Layer | Purpose | Technology |
|-------|---------|------------|
| **Authorization** | Budget enforcement, cryptographic approval | x402 + CDP Wallet |
| **Execution** | Legacy payment rails | Computer Use + ACH |

### Core Principles

1. **x402 = Authorization Layer** - Cryptographic permission slips for agents
2. **ACH = Execution Backend** - Legacy rails we bridge to
3. **Credentials never exposed to AI** - Injected securely at runtime
4. **Full audit trail** - On-chain authorization + confirmation screenshots

**Research Finding:** No existing open-source implementation of x402 + ACH bridge exists. This is a novel architecture combining:
- [x402 Protocol](https://github.com/coinbase/x402) (Coinbase) — Authorization layer
- [CDP Server Wallets](https://docs.cdp.coinbase.com/server-wallets/v2/evm-features/spend-permissions) — Budget enforcement
- Claude Computer Use — Legacy execution bridge
- Secure credential vault pattern — Credential isolation

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER ONBOARDING (ONE-TIME)                          │
│                                                                             │
│   1. User creates CDP Server Wallet via Coinbase                           │
│   2. User adds USDC to wallet (this is their "authorization budget")       │
│   3. User securely stores ACH credentials in encrypted vault               │
│   4. User sets spending policies (daily limits, per-tx limits)             │
│                                                                             │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐              │
│   │ CDP Wallet   │     │ Credential   │     │ Policy       │              │
│   │ (USDC)       │     │ Vault        │     │ Engine       │              │
│   │ Budget       │     │ (Encrypted)  │     │ (Limits)     │              │
│   └──────────────┘     └──────────────┘     └──────────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AUTHORIZATION + EXECUTION FLOW                         │
│                                                                             │
│              ┌─────────────────────────────────────────┐                   │
│              │     x402 AUTHORIZATION LAYER            │                   │
│              │                                          │                   │
│   Invoice →  │  Budget Check → Policy Check → Sign    │  → Auth Token     │
│              │                                          │                   │
│              │  "Permission slip for real-world action"│                   │
│              └─────────────────────────────────────────┘                   │
│                                    │                                        │
│                             AUTHORIZED                                      │
│                                    │                                        │
│                                    ▼                                        │
│              ┌─────────────────────────────────────────┐                   │
│              │      LEGACY EXECUTION LAYER             │                   │
│              │                                          │                   │
│   Auth →     │  Browser → Form Fill → Submit → Confirm│  → ACH Payment    │
│   Token      │                                          │                   │
│              │  "Execute via legacy rails (ACH)"       │                   │
│              └─────────────────────────────────────────┘                   │
│                                                                             │
│   RESULT: Vendor receives ACH | We maintain cryptographic authorization   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: User Wallet Setup (One-Time)

### 1.1 CDP Server Wallet Creation

User creates a CDP Server Wallet via Coinbase Developer Platform. This is a self-custodied wallet with:
- TEE (Trusted Execution Environment) protection
- Private keys never exposed - even to Coinbase
- Programmable spending policies

```python
from cdp import Cdp, Wallet

# Initialize CDP
Cdp.configure_from_json("cdp_api_key.json")

# Create wallet for user
wallet = Wallet.create(network_id="base-mainnet")

# Export wallet data for persistence (encrypted)
wallet_data = wallet.export_data()
# Store securely - this allows wallet recovery
```

### 1.2 Funding the Wallet

User adds USDC to their wallet. This is their "payment balance" for autonomous operations.

```
User Bank Account
      │
      ▼ (Coinbase/Circle on-ramp)
┌─────────────────┐
│  USDC on Base   │
│  (User Wallet)  │
│  Balance: $500  │
└─────────────────┘
```

**Funding Options:**
- Coinbase on-ramp (bank → USDC)
- Circle on-ramp
- Direct USDC transfer from another wallet

### 1.3 Spending Policy Configuration

Critical security layer - define what the agent CAN and CANNOT do:

```python
# CDP Wallet Policy Configuration
wallet_policy = {
    "spending_limits": {
        "per_transaction_max": 500.00,      # Max $500 per payment
        "daily_limit": 2000.00,             # Max $2000/day
        "weekly_limit": 5000.00,            # Max $5000/week
    },
    "recipient_rules": {
        "mode": "allowlist",                # Only pay known vendors
        "allowlist": [
            "0xEscrowWallet...",            # Our escrow wallet
        ]
    },
    "transaction_rules": {
        "require_memo": True,               # Must include invoice ID
        "min_confirmation_time": 5,         # 5 second delay for review
    }
}
```

---

## Phase 2: Secure Credential Storage

### 2.1 Credential Vault Architecture

**CRITICAL:** ACH credentials (routing number, account number) are NEVER exposed to the AI agent. They are stored encrypted and injected only at execution time.

```
┌─────────────────────────────────────────────────────────────────┐
│                    CREDENTIAL VAULT                              │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  ENCRYPTED AT REST (AES-256-GCM)                        │   │
│   │                                                          │   │
│   │  {                                                       │   │
│   │    "ach_routing": "encrypted_blob_1",                   │   │
│   │    "ach_account": "encrypted_blob_2",                   │   │
│   │    "ach_name": "encrypted_blob_3",                      │   │
│   │    "encryption_key_id": "aws_kms_key_id"                │   │
│   │  }                                                       │   │
│   │                                                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│   Access: Only via secure credential injector process            │
│   Audit: All access logged with timestamp + purpose              │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Credential Entry (One-Time Setup)

User enters credentials through secure UI (not AI):

```python
# Secure credential storage (runs during setup, NOT during payment)
from cryptography.fernet import Fernet
import os

class CredentialVault:
    def __init__(self):
        # Key from AWS KMS or similar
        self.key = os.getenv("VAULT_ENCRYPTION_KEY")
        self.fernet = Fernet(self.key)

    def store_credentials(self, routing: str, account: str, name: str):
        """One-time credential storage by user (NOT AI)"""
        encrypted = {
            "ach_routing": self.fernet.encrypt(routing.encode()),
            "ach_account": self.fernet.encrypt(account.encode()),
            "ach_name": self.fernet.encrypt(name.encode()),
            "created_at": datetime.now().isoformat(),
            "created_by": "user_manual_entry"  # Audit trail
        }
        # Store in secure database (MongoDB with field-level encryption)
        db.credentials.insert_one(encrypted)

    def get_credentials_for_injection(self, invoice_id: str) -> dict:
        """Decrypt credentials for injection into isolated environment"""
        # Verify authorization first
        if not self._verify_payment_authorized(invoice_id):
            raise SecurityError("Payment not authorized via x402")

        encrypted = db.credentials.find_one()
        return {
            "routing": self.fernet.decrypt(encrypted["ach_routing"]).decode(),
            "account": self.fernet.decrypt(encrypted["ach_account"]).decode(),
            "name": self.fernet.decrypt(encrypted["ach_name"]).decode()
        }
```

### 2.3 Security Properties

| Property | Implementation |
|----------|----------------|
| Encryption at rest | AES-256-GCM via AWS KMS |
| Encryption in transit | TLS 1.3 |
| Access control | x402 authorization required |
| Key management | AWS KMS / HashiCorp Vault |
| Audit logging | Every access logged to MongoDB |
| Credential rotation | User can update anytime |

---

## Phase 3: Invoice Ingestion & Parsing

### 3.1 Invoice Sources

```
┌─────────────────────────────────────────────────────────────┐
│                    INVOICE SOURCES                           │
│                                                              │
│   ┌────────────┐   ┌────────────┐   ┌────────────┐         │
│   │ Email      │   │ PDF Upload │   │ API/Webhook│         │
│   │ Attachment │   │            │   │            │         │
│   └─────┬──────┘   └─────┬──────┘   └─────┬──────┘         │
│         │                │                │                  │
│         └────────────────┴────────────────┘                  │
│                          │                                   │
│                          ▼                                   │
│              ┌───────────────────────┐                      │
│              │   Invoice Processor   │                      │
│              │   (AI OCR + Claude)   │                      │
│              └───────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Invoice Field Extraction

Using Claude's vision capabilities to extract structured data:

```python
from anthropic import Anthropic
import base64

async def extract_invoice_fields(invoice_pdf_path: str) -> dict:
    """Extract invoice data using Claude vision - NO credentials involved"""

    # Read PDF/image
    with open(invoice_pdf_path, "rb") as f:
        pdf_bytes = f.read()
        pdf_b64 = base64.b64encode(pdf_bytes).decode()

    claude = Anthropic()

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_b64
                    }
                },
                {
                    "type": "text",
                    "text": """Extract invoice information. Return JSON only:
{
  "invoice_id": "string",
  "vendor_name": "string",
  "vendor_address": "string",
  "amount_due": number,
  "currency": "USD",
  "due_date": "YYYY-MM-DD",
  "payment_url": "string or null",
  "payment_methods_accepted": ["ACH", "Credit Card", etc],
  "line_items": [{"description": "string", "amount": number}]
}

IMPORTANT: Look for "Pay Online", "Pay Now", or similar links/buttons.
Extract the payment URL if present."""
                }
            ]
        }]
    )

    import json
    return json.loads(response.content[0].text)
```

### 3.3 Payment Link Detection

If no payment URL in invoice, search vendor website:

```python
async def find_payment_link(vendor_name: str, invoice_id: str) -> str:
    """Search for payment portal if not in invoice"""

    # Strategy 1: Check invoice for embedded link
    # Strategy 2: Search vendor website
    # Strategy 3: Use Exa.ai to find payment portal

    from exa_py import Exa
    exa = Exa(os.getenv("EXA_API_KEY"))

    results = exa.search_and_contents(
        f"{vendor_name} pay invoice online portal",
        type="neural",
        num_results=5
    )

    # Use Claude to identify correct payment portal
    for result in results.results:
        if is_legitimate_payment_portal(result.url, vendor_name):
            return result.url

    return None
```

### 3.4 Invoice Validation

Before proceeding, validate the invoice:

```python
async def validate_invoice(invoice: dict) -> tuple[bool, str]:
    """Validate invoice before payment"""

    checks = []

    # Check 1: Amount within limits
    if invoice["amount_due"] > SPENDING_LIMITS["per_transaction_max"]:
        return False, f"Amount ${invoice['amount_due']} exceeds limit"

    # Check 2: Vendor on allowlist (if enabled)
    if VENDOR_ALLOWLIST_ENABLED:
        if invoice["vendor_name"] not in APPROVED_VENDORS:
            return False, f"Vendor {invoice['vendor_name']} not approved"

    # Check 3: Not a duplicate payment
    existing = db.payments.find_one({
        "invoice_id": invoice["invoice_id"],
        "vendor": invoice["vendor_name"]
    })
    if existing:
        return False, f"Invoice {invoice['invoice_id']} already paid"

    # Check 4: Payment URL is HTTPS
    if invoice.get("payment_url"):
        if not invoice["payment_url"].startswith("https://"):
            return False, "Payment URL must be HTTPS"

    # Check 5: Amount matches line items
    line_total = sum(item["amount"] for item in invoice.get("line_items", []))
    if abs(line_total - invoice["amount_due"]) > 0.01:
        return False, "Amount mismatch with line items"

    return True, "Valid"
```

---

## Phase 3.5: SMS Approval Flow (Large Purchases)

### When SMS Approval is Required

For security, large purchases require explicit owner approval via SMS before x402 authorization proceeds:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SMS APPROVAL FLOW                                 │
│                                                                     │
│   EVALUATION AGENT outputs: $1,847.50 across 4 vendors             │
│                          │                                          │
│                          ▼                                          │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │            APPROVAL THRESHOLD CHECK                          │  │
│   │                                                              │  │
│   │  if amount > SMS_APPROVAL_THRESHOLD ($500):                 │  │
│   │     → Require SMS approval                                  │  │
│   │  else:                                                      │  │
│   │     → Auto-approve (proceed to x402)                        │  │
│   │                                                              │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                          │                                          │
│                          ▼                                          │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │            SEND SMS APPROVAL REQUEST                         │  │
│   │                                                              │  │
│   │  SMS → Owner:                                               │  │
│   │  "⚠️ Large purchase requires approval:                       │  │
│   │   $1,847.50 across 4 vendors:                               │  │
│   │   - Bay Area Foods: $212.50 (flour)                         │  │
│   │   - Farm Fresh: $450.00 (eggs)                              │  │
│   │   - ...                                                     │  │
│   │   Reply APPROVE to proceed or DENY to cancel."              │  │
│   │                                                              │  │
│   │  Store in: pending_approvals (TTL: 24 hours)                │  │
│   │                                                              │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                          │                                          │
│                          │ Owner replies: "APPROVE"                 │
│                          ▼                                          │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │            PROCESS APPROVAL                                  │  │
│   │                                                              │  │
│   │  1. Lookup pending_approvals by phone                       │  │
│   │  2. Update status to "approved"                             │  │
│   │  3. Trigger x402 authorization                              │  │
│   │  4. Send confirmation: "✓ Processing payments..."           │  │
│   │                                                              │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                          │                                          │
│                          ▼                                          │
│                    x402 AUTHORIZATION                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### SMS Approval Implementation

```python
from twilio.rest import Client
from datetime import datetime, timedelta

twilio = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
SMS_APPROVAL_THRESHOLD = 500.00  # Require approval above $500


async def check_and_request_approval(invoices: list, total_amount: float, owner_phone: str) -> bool:
    """
    Check if SMS approval is needed and request if so.
    Returns True if auto-approved, False if waiting for SMS.
    """

    if total_amount <= SMS_APPROVAL_THRESHOLD:
        # Auto-approve small purchases
        return True

    # Create approval request
    vendor_summary = "\n".join([
        f"  - {inv['vendor']}: ${inv['amount_usd']:.2f} ({inv['ingredient']})"
        for inv in invoices[:4]  # Show first 4
    ])

    if len(invoices) > 4:
        vendor_summary += f"\n  ... and {len(invoices) - 4} more"

    message = f"""⚠️ Large purchase requires approval:
${total_amount:.2f} across {len(invoices)} vendors:
{vendor_summary}

Reply APPROVE to proceed or DENY to cancel."""

    # Send SMS
    twilio.messages.create(
        body=message,
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        to=owner_phone
    )

    # Store pending approval
    db.pending_approvals.insert_one({
        "phone": owner_phone,
        "type": "payment",
        "invoices": invoices,
        "total_amount": total_amount,
        "status": "pending",
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=24)
    })

    return False  # Waiting for approval


async def process_sms_approval(phone: str, approved: bool) -> dict:
    """Process SMS approval/denial for pending payments."""

    pending = db.pending_approvals.find_one_and_update(
        {"phone": phone, "type": "payment", "status": "pending"},
        {"$set": {"status": "approved" if approved else "denied", "processed_at": datetime.now()}}
    )

    if not pending:
        return {"status": "no_pending", "message": "No pending payment approval found"}

    if approved:
        # Proceed with x402 authorization
        results = []
        for invoice in pending["invoices"]:
            auth_result = await x402_authorize(invoice)
            results.append(auth_result)

        # Send confirmation
        twilio.messages.create(
            body=f"✓ Approved! Processing {len(results)} payments via x402...",
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=phone
        )

        return {"status": "approved", "payments_initiated": len(results)}
    else:
        # Send denial confirmation
        twilio.messages.create(
            body="✗ Payments cancelled. No charges made.",
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=phone
        )

        return {"status": "denied", "message": "Payments cancelled by owner"}
```

### MongoDB Collection: pending_approvals

```python
pending_approvals = {
    "_id": ObjectId(),
    "phone": "+14155551234",
    "type": "payment",  # "payment" | "reorder" | "new_order"
    "invoices": [
        {"invoice_id": "INV-001", "vendor": "Bay Area Foods", "amount_usd": 212.50, ...},
        ...
    ],
    "total_amount": 1847.50,
    "status": "pending",  # "pending" | "approved" | "denied" | "expired"
    "created_at": ISODate(),
    "expires_at": ISODate(),  # TTL index: auto-delete after 24h
    "processed_at": ISODate()  # When approved/denied
}

# TTL index to auto-expire pending approvals
db.pending_approvals.create_index("expires_at", expireAfterSeconds=0)
```

---

## Phase 4: x402 Authorization Layer

### 4.1 Authorization Flow

The x402 protocol provides cryptographic authorization BEFORE any payment executes:

```
┌─────────────────────────────────────────────────────────────────┐
│                    x402 AUTHORIZATION FLOW                       │
│                                                                  │
│   1. Payment Agent requests: POST /authorize-payment            │
│                                                                  │
│   2. Server returns 402 Payment Required:                       │
│      ┌──────────────────────────────────────────────────────┐   │
│      │  HTTP/1.1 402 Payment Required                       │   │
│      │  X-Payment-Amount: 212.50                            │   │
│      │  X-Payment-Currency: USDC                            │   │
│      │  X-Payment-Recipient: 0xEscrowWallet                 │   │
│      │  X-Payment-Memo: INV-2026-0192                       │   │
│      │  X-Payment-Network: base-mainnet                     │   │
│      └──────────────────────────────────────────────────────┘   │
│                                                                  │
│   3. Agent wallet evaluates policies:                           │
│      - Is amount within per-tx limit? ✓                         │
│      - Is daily limit not exceeded? ✓                           │
│      - Is recipient on allowlist? ✓                             │
│      - Is memo format valid? ✓                                  │
│                                                                  │
│   4. Wallet signs USDC transfer to escrow:                      │
│      TX Hash: 0x8f3e7b2a9c1d4e5f...                             │
│                                                                  │
│   5. Agent retries with X-Payment-Signature header              │
│                                                                  │
│   6. Server verifies on-chain transfer, grants authorization    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Implementation

```python
from cdp import Cdp, Wallet
import httpx

class X402Authorizer:
    def __init__(self, wallet: Wallet):
        self.wallet = wallet
        self.escrow_address = os.getenv("ESCROW_WALLET_ADDRESS")

    async def authorize_payment(self, invoice: dict) -> dict:
        """
        x402 authorization - transfers USDC to escrow
        This is the ONLY way to unlock ACH execution
        """

        # Step 1: Validate against spending policies
        policy_check = self._check_policies(invoice)
        if not policy_check["allowed"]:
            raise PolicyViolation(policy_check["reason"])

        # Step 2: Reserve budget atomically
        budget_id = self._reserve_budget(invoice["amount_due"])

        try:
            # Step 3: Execute USDC transfer to escrow
            transfer = self.wallet.transfer(
                amount=invoice["amount_due"],
                asset_id="usdc",
                destination=self.escrow_address,
                # Include invoice ID in memo for audit trail
                memo=f"AUTH:{invoice['invoice_id']}"
            )

            # Wait for on-chain confirmation
            transfer.wait()

            # Step 4: Generate authorization token
            auth_token = self._generate_auth_token(
                invoice_id=invoice["invoice_id"],
                amount=invoice["amount_due"],
                tx_hash=transfer.transaction_hash,
                budget_id=budget_id
            )

            # Step 5: Log authorization
            db.authorizations.insert_one({
                "invoice_id": invoice["invoice_id"],
                "amount": invoice["amount_due"],
                "tx_hash": transfer.transaction_hash,
                "auth_token": auth_token,
                "status": "authorized",
                "timestamp": datetime.now()
            })

            return {
                "status": "authorized",
                "tx_hash": transfer.transaction_hash,
                "auth_token": auth_token,
                "explorer_url": f"https://basescan.org/tx/{transfer.transaction_hash}"
            }

        except Exception as e:
            # Release reserved budget on failure
            self._release_budget(budget_id)
            raise

    def _check_policies(self, invoice: dict) -> dict:
        """Check all spending policies"""

        amount = invoice["amount_due"]

        # Per-transaction limit
        if amount > POLICIES["per_transaction_max"]:
            return {"allowed": False, "reason": "Exceeds per-transaction limit"}

        # Daily limit
        today_spent = self._get_today_spending()
        if today_spent + amount > POLICIES["daily_limit"]:
            return {"allowed": False, "reason": "Would exceed daily limit"}

        # Weekly limit
        week_spent = self._get_week_spending()
        if week_spent + amount > POLICIES["weekly_limit"]:
            return {"allowed": False, "reason": "Would exceed weekly limit"}

        # Duplicate detection
        recent = db.authorizations.find_one({
            "invoice_id": invoice["invoice_id"],
            "timestamp": {"$gte": datetime.now() - timedelta(hours=24)}
        })
        if recent:
            return {"allowed": False, "reason": "Duplicate payment detected"}

        return {"allowed": True}
```

---

## Phase 5: Secure Computer Use Execution

### 5.1 Isolated Execution Environment

**CRITICAL SECURITY:** The Computer Use browser runs in an isolated environment where credentials are injected but NEVER visible to the AI reasoning process.

```
┌─────────────────────────────────────────────────────────────────┐
│               ISOLATED EXECUTION ENVIRONMENT                     │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    SANDBOX CONTAINER                      │   │
│   │                                                           │   │
│   │   ┌─────────────┐    ┌─────────────┐                    │   │
│   │   │ Playwright  │    │ Credential  │                    │   │
│   │   │ Browser     │◄───│ Injector    │                    │   │
│   │   └─────────────┘    └─────────────┘                    │   │
│   │         │                   ▲                            │   │
│   │         │                   │                            │   │
│   │         ▼                   │ (Encrypted channel)        │   │
│   │   ┌─────────────┐          │                            │   │
│   │   │ Screenshot  │    ┌─────┴─────┐                      │   │
│   │   │ (redacted)  │    │ Vault     │                      │   │
│   │   └─────────────┘    │ Service   │                      │   │
│   │         │            └───────────┘                      │   │
│   │         ▼                                                │   │
│   │   ┌─────────────┐                                       │   │
│   │   │ Claude      │    Claude sees: "***" for credentials │   │
│   │   │ (Vision)    │    Claude controls: clicks only       │   │
│   │   └─────────────┘                                       │   │
│   │                                                           │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│   Network: Isolated - only payment portal accessible             │
│   Filesystem: Read-only except screenshots/                      │
│   Credentials: Injected, never in AI context                     │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Credential Injection (NOT AI-Controlled)

The AI tells us WHERE to type, but a separate secure process handles WHAT to type:

```python
class SecureCredentialInjector:
    """
    Handles credential injection WITHOUT exposing values to AI

    The AI:
    - Identifies form fields via vision
    - Returns coordinates/selectors for fields
    - NEVER sees actual credential values

    This injector:
    - Receives field locations from AI
    - Retrieves decrypted credentials from vault
    - Types credentials directly into browser
    - Masks all credential values in logs
    """

    def __init__(self, vault: CredentialVault, browser: BrowserController):
        self.vault = vault
        self.browser = browser

    async def inject_credentials(self, auth_token: str, field_map: dict):
        """
        Inject credentials into identified fields

        field_map from AI (NO credential values):
        {
            "routing_number_field": {"selector": "#routing", "type": "input"},
            "account_number_field": {"selector": "#account", "type": "input"},
            "account_name_field": {"selector": "#name", "type": "input"}
        }
        """

        # Verify authorization before decrypting
        if not self._verify_auth_token(auth_token):
            raise SecurityError("Invalid or expired authorization token")

        # Get credentials (decryption happens here, in secure process)
        creds = self.vault.get_credentials_for_injection(auth_token)

        # Map credential types to values
        injection_map = {
            "routing_number_field": creds["routing"],
            "account_number_field": creds["account"],
            "account_name_field": creds["name"]
        }

        # Inject each credential
        for field_name, selector_info in field_map.items():
            if field_name in injection_map:
                value = injection_map[field_name]

                # Click field
                await self.browser.page.click(selector_info["selector"])

                # Clear existing value
                await self.browser.page.fill(selector_info["selector"], "")

                # Type credential (NOT visible to AI)
                await self.browser.page.fill(
                    selector_info["selector"],
                    value
                )

                # Log injection (masked)
                self._log_injection(field_name, len(value))

    def _log_injection(self, field_name: str, value_length: int):
        """Log injection without exposing values"""
        db.injection_logs.insert_one({
            "field": field_name,
            "value_length": value_length,
            "value_preview": "***",  # Never log actual values
            "timestamp": datetime.now()
        })
```

### 5.3 AI-Controlled Navigation (Credentials Masked)

The AI sees screenshots with credentials REDACTED:

```python
class SecureACHBridge:
    """
    Computer Use bridge where AI navigates but never sees credentials
    """

    def __init__(self):
        self.browser = None
        self.injector = None
        self.vault = CredentialVault()

    async def execute_payment(self, invoice: dict, auth_token: str) -> dict:
        """
        Execute ACH payment with credential isolation

        AI responsibilities:
        - Navigate to payment portal
        - Identify form fields
        - Click submit button
        - Verify confirmation

        Secure injector responsibilities:
        - Type actual credential values
        - Never expose values to AI context
        """

        # Initialize isolated browser
        self.browser = await BrowserController().start(headless=False)
        self.injector = SecureCredentialInjector(self.vault, self.browser)

        try:
            # Step 1: Navigate to payment URL
            await self.browser.navigate(invoice["payment_url"])

            # Step 2: AI navigation loop
            max_steps = 15
            for step in range(max_steps):

                # Take screenshot and REDACT any visible credentials
                screenshot = await self._take_redacted_screenshot()

                # AI analyzes page
                action = await self._get_ai_action(screenshot, step)

                if action["type"] == "identify_form":
                    # AI found form fields - inject credentials securely
                    await self.injector.inject_credentials(
                        auth_token=auth_token,
                        field_map=action["field_map"]
                    )

                elif action["type"] == "click":
                    # AI wants to click something (submit, next, etc.)
                    await self.browser.click(action["x"], action["y"])

                elif action["type"] == "payment_complete":
                    # AI detected confirmation page
                    confirmation = await self._extract_confirmation(screenshot)
                    return {
                        "status": "success",
                        "confirmation_number": confirmation,
                        "screenshot": f"screenshots/{invoice['invoice_id']}-confirm.png"
                    }

                elif action["type"] == "error":
                    return {"status": "error", "message": action["message"]}

                await asyncio.sleep(0.5)

            return {"status": "timeout", "message": "Max steps reached"}

        finally:
            await self.browser.close()

    async def _take_redacted_screenshot(self) -> str:
        """Take screenshot and redact any visible credential values"""

        # Take raw screenshot
        screenshot_bytes = await self.browser.page.screenshot()

        # TODO: Apply redaction for any credential patterns
        # This prevents accidental credential exposure in AI context

        return base64.b64encode(screenshot_bytes).decode()

    async def _get_ai_action(self, screenshot: str, step: int) -> dict:
        """Get next action from AI - credentials never in prompt"""

        claude = Anthropic()

        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": screenshot
                        }
                    },
                    {
                        "type": "text",
                        "text": f"""You are completing an ACH bank payment. Step {step + 1}.

IMPORTANT: You do NOT have access to credentials. A secure system will fill them.
Your job: Identify fields and navigation, NOT enter values.

Analyze the screenshot and return ONE action as JSON:

1. If you see an ACH/bank payment form with empty fields:
{{
  "type": "identify_form",
  "field_map": {{
    "routing_number_field": {{"selector": "CSS_SELECTOR"}},
    "account_number_field": {{"selector": "CSS_SELECTOR"}},
    "account_name_field": {{"selector": "CSS_SELECTOR"}}
  }}
}}

2. If form is filled and you see a submit/pay button:
{{
  "type": "click",
  "x": <x_coordinate>,
  "y": <y_coordinate>,
  "description": "Clicking submit button"
}}

3. If you see a confirmation/success page:
{{
  "type": "payment_complete",
  "confirmation_visible": true
}}

4. If you see an error or problem:
{{
  "type": "error",
  "message": "Description of error"
}}

Return only the JSON, no other text."""
                    }
                ]
            }]
        )

        return json.loads(response.content[0].text)
```

---

## Phase 6: Confirmation & Audit Trail

### 6.1 Payment Verification

After Computer Use completes, verify the payment:

```python
async def verify_payment_completion(
    invoice: dict,
    ach_result: dict,
    auth_token: str
) -> dict:
    """
    Verify payment completed successfully

    Multiple verification layers:
    1. Screenshot shows confirmation
    2. Confirmation number extracted
    3. x402 authorization matched
    """

    verification = {
        "invoice_id": invoice["invoice_id"],
        "vendor": invoice["vendor_name"],
        "amount": invoice["amount_due"],
        "timestamp": datetime.now()
    }

    # Check 1: ACH result status
    if ach_result["status"] != "success":
        verification["verified"] = False
        verification["reason"] = f"ACH execution failed: {ach_result.get('message')}"
        return verification

    # Check 2: Confirmation number present
    if not ach_result.get("confirmation_number"):
        verification["verified"] = False
        verification["reason"] = "No confirmation number extracted"
        return verification

    # Check 3: Screenshot captured
    if not os.path.exists(ach_result.get("screenshot", "")):
        verification["verified"] = False
        verification["reason"] = "Confirmation screenshot not captured"
        return verification

    # Check 4: Match with x402 authorization
    auth = db.authorizations.find_one({"auth_token": auth_token})
    if not auth or auth["invoice_id"] != invoice["invoice_id"]:
        verification["verified"] = False
        verification["reason"] = "Authorization mismatch"
        return verification

    verification["verified"] = True
    verification["confirmation_number"] = ach_result["confirmation_number"]
    verification["x402_tx_hash"] = auth["tx_hash"]
    verification["screenshot_path"] = ach_result["screenshot"]

    return verification
```

### 6.2 Complete Audit Trail

Every step logged to MongoDB:

```python
# MongoDB Collections for Audit Trail

# 1. Invoices received
invoices = {
    "_id": ObjectId(),
    "invoice_id": "INV-2026-0192",
    "vendor": "Bay Area Foods Co",
    "amount": 212.50,
    "payment_url": "https://...",
    "received_at": ISODate(),
    "source": "email",  # email | upload | api
    "status": "pending"  # pending | authorized | paid | failed
}

# 2. x402 Authorizations
authorizations = {
    "_id": ObjectId(),
    "invoice_id": "INV-2026-0192",
    "amount": 212.50,
    "tx_hash": "0x8f3e7b2a...",
    "auth_token": "secure_token_xxx",
    "wallet_address": "0xUser...",
    "escrow_address": "0xEscrow...",
    "policy_checks": {
        "per_tx_limit": "passed",
        "daily_limit": "passed",
        "duplicate_check": "passed"
    },
    "timestamp": ISODate()
}

# 3. Computer Use Executions
executions = {
    "_id": ObjectId(),
    "invoice_id": "INV-2026-0192",
    "auth_token": "secure_token_xxx",
    "steps": [
        {"step": 1, "action": "navigate", "url": "https://..."},
        {"step": 2, "action": "identify_form", "fields": 3},
        {"step": 3, "action": "inject_credentials", "fields_filled": 3},
        {"step": 4, "action": "click_submit"},
        {"step": 5, "action": "confirm_success"}
    ],
    "screenshots": [
        "screenshots/INV-2026-0192-step1.png",
        "screenshots/INV-2026-0192-confirm.png"
    ],
    "duration_seconds": 12.5,
    "timestamp": ISODate()
}

# 4. Final Payment Records
payments = {
    "_id": ObjectId(),
    "invoice_id": "INV-2026-0192",
    "vendor": "Bay Area Foods Co",
    "amount": 212.50,
    "x402_tx_hash": "0x8f3e7b2a...",
    "x402_explorer": "https://basescan.org/tx/0x8f3e7b2a...",
    "ach_confirmation": "ACH-2026-0192-BAYAREA",
    "screenshot_path": "screenshots/INV-2026-0192-confirm.png",
    "verified": True,
    "payment_method": "x402_computer_use_ach",
    "timestamp": ISODate()
}

# 5. Security Events (Anomalies)
security_events = {
    "_id": ObjectId(),
    "type": "policy_violation",  # policy_violation | auth_failure | anomaly
    "invoice_id": "INV-2026-0192",
    "details": "Amount exceeds daily limit",
    "action_taken": "payment_blocked",
    "timestamp": ISODate()
}
```

---

## Phase 7: Security Architecture Summary

### 7.1 Defense in Depth

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                               │
│                                                                  │
│   Layer 1: CDP Wallet Policies                                  │
│   ├── Per-transaction limits                                    │
│   ├── Daily/weekly spending caps                                │
│   ├── Recipient allowlist                                       │
│   └── TEE-enforced signing                                      │
│                                                                  │
│   Layer 2: x402 Authorization                                   │
│   ├── Cryptographic payment proof                               │
│   ├── On-chain audit trail                                      │
│   ├── Escrow-based authorization                                │
│   └── Single-use auth tokens                                    │
│                                                                  │
│   Layer 3: Credential Isolation                                 │
│   ├── Encrypted vault storage                                   │
│   ├── Runtime injection only                                    │
│   ├── AI never sees values                                      │
│   └── AWS KMS key management                                    │
│                                                                  │
│   Layer 4: Execution Sandboxing                                 │
│   ├── Isolated container/VM                                     │
│   ├── Network restrictions                                      │
│   ├── Screenshot redaction                                      │
│   └── Read-only filesystem                                      │
│                                                                  │
│   Layer 5: Monitoring & Alerting                                │
│   ├── Real-time anomaly detection                               │
│   ├── Spending velocity alerts                                  │
│   ├── Failed auth notifications                                 │
│   └── Complete audit logging                                    │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Threat Mitigations

| Threat | Mitigation |
|--------|------------|
| **Infinite payment loops** | Per-tx and daily limits, duplicate detection |
| **Prompt injection** | Credentials never in AI context |
| **Credential theft** | Encrypted vault, runtime injection only |
| **Decimal confusion** | Amount validation against invoice |
| **Frequency drainage** | Rate limiting, spending velocity alerts |
| **Malicious payment portal** | URL validation, HTTPS required |
| **Replay attacks** | Single-use auth tokens |
| **Unauthorized access** | x402 on-chain authorization required |

### 7.3 What the AI CAN and CANNOT Do

| AI CAN | AI CANNOT |
|--------|-----------|
| See payment portal UI | See credential values |
| Identify form field locations | Type credential values |
| Click buttons/links | Access credential vault |
| Read confirmation numbers | Modify spending policies |
| Report errors | Bypass x402 authorization |

---

## Implementation Checklist

### Must Have (Security Critical)
- [ ] CDP Server Wallet with spending policies
- [ ] Encrypted credential vault (AWS KMS)
- [ ] x402 authorization layer
- [ ] Credential injection isolation
- [ ] Complete audit logging

### Should Have
- [ ] Screenshot redaction for credentials
- [ ] Real-time spending alerts
- [ ] Anomaly detection
- [ ] Automated credential rotation

### Nice to Have
- [ ] Multi-signature approvals for large amounts
- [ ] Vendor payment portal verification
- [ ] Machine learning fraud detection

---

## References

**Research Sources:**
- [x402 Protocol - Coinbase](https://github.com/coinbase/x402)
- [CDP Server Wallets - Spending Policies](https://docs.cdp.coinbase.com/server-wallets/v2/evm-features/spend-permissions)
- [Securing x402 - Spending Controls Article](https://dev.to/l_x_1/securing-the-x402-protocol-why-autonomous-agent-payments-need-spending-controls-a90)
- [CDP Wallet Policies](https://www.coinbase.com/developer-platform/discover/launches/policy-engine)
- [Questflow Case Study - CDP + x402](https://www.coinbase.com/developer-platform/discover/case-studies/questflow)
- [Claude Computer Use Security](https://labs.zenity.io/p/claude-in-chrome-a-threat-analysis)
- [Invoice OCR Tools](https://www.koncile.ai/en/ressources/top-10-ocr-tools-for-invoices-2025)

---

**Document Status:** Ready for Implementation
**Novel Architecture:** Yes - No existing open-source implementation found
**Security Review Required:** Yes - Before production deployment
