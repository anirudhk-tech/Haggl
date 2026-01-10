# Tech Stack
## Haggl - Technical Dependencies

**Version:** 2.0
**Date:** January 10, 2026

---

## Core Stack Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                           HAGGL                                  │
├─────────────────────────────────────────────────────────────────┤
│  Frontend    │  Web Dashboard (React) + CLI                    │
├──────────────┼──────────────────────────────────────────────────┤
│  Backend     │  Python 3.10+ / FastAPI                         │
├──────────────┼──────────────────────────────────────────────────┤
│  Database    │  MongoDB Atlas (Free M0)                        │
├──────────────┼──────────────────────────────────────────────────┤
│  AI/LLM      │  Claude API (Anthropic)                         │
├──────────────┼──────────────────────────────────────────────────┤
│  Search      │  Exa.ai (Semantic)                              │
├──────────────┼──────────────────────────────────────────────────┤
│  Voice       │  Vapi (TTS + Phone)                             │
├──────────────┼──────────────────────────────────────────────────┤
│  SMS         │  Twilio (Text ordering & approvals)             │
├──────────────┼──────────────────────────────────────────────────┤
│  Payments    │  x402 + Computer Use (ACH Bridge)               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Python Dependencies

### requirements.txt
```
# Database
pymongo>=4.6.0

# AI/LLM
anthropic>=0.40.0

# Search
exa-py>=1.0.0

# Voice AI
vapi-python>=0.1.0

# SMS (Twilio)
twilio>=8.0.0

# Payments (x402 + Computer Use ACH Bridge)
cdp-sdk>=0.0.5
playwright>=1.40.0    # Browser automation for ACH payments

# API Framework
fastapi>=0.109.0
uvicorn>=0.27.0
python-multipart>=0.0.6  # For file uploads (CSV)

# Utilities
python-dotenv>=1.0.0
```

### Installation
```bash
pip install pymongo anthropic exa-py vapi-python twilio cdp-sdk playwright fastapi uvicorn python-multipart python-dotenv
playwright install chromium  # Install browser for computer use
```

---

## Component Details

### 1. MongoDB Atlas
**Purpose:** Agent state, coordination, logging

**Why MongoDB:**
- Flexible schema for diverse data
- Vector Search for semantic matching
- Change Streams for real-time updates
- Free M0 tier for hackathon

**Collections:**
| Collection | Purpose |
|------------|---------|
| `suppliers` | Vendor database |
| `negotiations` | Call transcripts |
| `invoices` | Received invoices |
| `payments` | Payment records |
| `decisions` | Selection logic |

**Advanced Features Used:**
- Vector Search (supplier similarity)
- TTL Indexes (auto-expire negotiations)
- Time Series (payment analytics)

---

### 2. Claude API (Anthropic)
**Purpose:** Reasoning, extraction, decisions

**Model:** claude-sonnet-4-20250514

**Use Cases:**
- Parse negotiation transcripts
- Generate evaluation justifications
- Analyze invoice data

**Cost:** ~$0.003 per 1K input tokens, ~$0.015 per 1K output

---

### 3. Exa.ai
**Purpose:** Semantic supplier search

**Why Exa:**
- Neural search (not just keywords)
- Content extraction built-in
- Better for finding B2B suppliers
- 1000 free searches/month

**Search Types:**
- `neural` - Semantic understanding
- `keyword` - Traditional matching

---

### 4. Vapi
**Purpose:** Voice AI for phone negotiations

**Why Vapi:**
- Real outbound phone calls
- Claude integration for intelligence
- 11labs for natural voice
- Transcript capture

**Components:**
- Assistant (conversation logic)
- Voice (TTS provider)
- Call (execution)

---

### 5. Twilio (SMS)
**Purpose:** SMS-based ordering and approvals

**Why Twilio:**
- Industry-standard SMS gateway
- Webhook support for incoming messages
- Programmable messaging
- Global reach
- No app required for users

**Features Used:**
- Inbound SMS webhooks
- Outbound SMS for notifications
- Message history

**SMS Capabilities:**
| Command | Action |
|---------|--------|
| `ORDER [items]` | Start new order |
| `REORDER [item]` | Repeat previous order |
| `APPROVE` | Approve pending purchase |
| `DENY` | Reject pending purchase |
| `STATUS` | Check order status |
| `BUDGET` | Check remaining budget |

**Integration:**
```python
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# Send SMS
client.messages.create(
    body="✓ Order approved! Processing...",
    from_="+1234567890",
    to="+1987654321"
)

# Receive SMS (webhook response)
response = MessagingResponse()
response.message("Order received!")
```

---

### 6. x402 + Computer Use (ACH Bridge)
**Purpose:** Autonomous payment authorization + execution via browser

**Why x402 + Computer Use:**
- x402 provides authorization layer (spending limits, audit trail)
- Computer Use executes actual ACH payments via browser
- Works with ANY vendor payment portal (no API integration needed)
- Visual demo - shows AI actually navigating and paying
- On-chain audit trail via x402

**Flow:**
```
Invoice (with payment URL)
        ↓
x402 Authorization (USDC escrow)
        ↓
Computer Use ACH Bridge:
  1. Open browser (Playwright)
  2. Navigate to invoice payment portal
  3. Claude analyzes page, identifies ACH form
  4. Fill ACH details (routing #, account #)
  5. Submit payment
  6. Capture confirmation
        ↓
Log transaction to MongoDB
```

**Network:** Base (Ethereum L2) for x402
**Asset:** USDC (stablecoin) for authorization

### 6. Claude Computer Use
**Purpose:** Browser automation for ACH payment execution

**Why Computer Use:**
- Works with any vendor's payment portal
- No vendor API integration needed
- Visually impressive for demo
- Claude reasons about UI elements

**Components:**
- Playwright (browser automation)
- Claude API (vision + reasoning)
- Screenshot capture for verification

---

## API Costs (Hackathon Estimate)

| Service | Free Tier | Hackathon Usage | Cost |
|---------|-----------|-----------------|------|
| MongoDB Atlas | M0 (free) | 500MB | $0 |
| Claude API | $5 credit | ~150K tokens (incl. vision) | ~$3 |
| Exa.ai | 1000 searches | ~50 searches | $0 |
| Vapi | Trial credits | ~20 calls | $0-10 |
| CDP/x402 | Free | Gas only | ~$0.50 |
| Playwright | Free | Local browser | $0 |

**Total Estimate:** $4-15 for full hackathon

---

## File Structure

```
ingredient-ai/
├── main.py                    # Entry point & CLI
├── orchestrator.py            # Concurrent execution
├── agents/
│   ├── __init__.py
│   ├── sourcing.py           # Exa.ai integration
│   ├── negotiation.py        # Vapi integration
│   ├── evaluation.py         # Scoring & optimization
│   └── payment.py            # x402 + Computer Use ACH bridge
├── computer_use/
│   ├── __init__.py
│   ├── browser.py            # Playwright browser controller
│   ├── ach_bridge.py         # ACH payment automation
│   └── tools.py              # Computer use tool definitions
├── api/
│   ├── __init__.py
│   ├── server.py             # FastAPI endpoints
│   └── x402.py               # x402 middleware
├── utils/
│   ├── __init__.py
│   ├── mongo.py              # MongoDB client
│   └── config.py             # Environment config
├── .env                       # API keys (gitignored)
├── cdp_api_key.json          # CDP credentials (gitignored)
├── requirements.txt           # Dependencies
└── README.md                  # Setup guide
```

---

## Environment Setup

### .env
```bash
# MongoDB Atlas
MONGODB_URI=mongodb+srv://...

# Claude API
ANTHROPIC_API_KEY=sk-ant-...

# Exa.ai
EXA_API_KEY=...

# Vapi
VAPI_API_KEY=...

# Twilio (SMS)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...

# Coinbase CDP (or use JSON file)
CDP_API_KEY_FILE=cdp_api_key.json

# x402 Config
ESCROW_WALLET_ADDRESS=0x...

# ACH Bank Details (for Computer Use payments)
ACH_ROUTING_NUMBER=...
ACH_ACCOUNT_NUMBER=...
ACH_ACCOUNT_NAME=Sweet Dreams Bakery LLC
```

---

## Why This Stack?

### Minimal Complexity
- 9 total dependencies
- No heavy frameworks (LangChain, LangGraph)
- Simple Python async for concurrency

### Hackathon Optimized
- All free tiers available
- Fast setup (<30 min)
- Easy to debug

### Real Capabilities
- Real phone calls (Vapi)
- Real payments (x402 + Computer Use ACH)
- Real search (Exa.ai)
- Real AI (Claude)
- Real browser automation (Playwright)

### MongoDB Central
- All agent state in MongoDB
- Coordination via shared collections
- Full audit trail

---

## Quick Start

```bash
# 1. Clone and setup
git clone <repo>
cd ingredient-ai
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Test connections
python test_connections.py

# 5. Run demo
python main.py \
  --ingredients "flour" "eggs" "butter" \
  --quantities "500 lbs" "1000 units" "100 lbs" \
  --budget 2000
```

---

**Stack Status:** Production-Ready for Demo