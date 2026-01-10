# Haggl

**AI agents that source, negotiate, and pay for your business supplies autonomously.**

Haggl is a multi-agent B2B procurement system. A business owner inputs ingredient needs, quantities, and budget. Four specialized agents work concurrently to find suppliers, negotiate prices via real phone calls, evaluate options, and process payments using the x402 protocol.

## 🚀 Features

### Multi-Agent Architecture

| Agent | Technology | Purpose |
|-------|------------|---------|
| **Sourcing** | Exa.ai + Claude | Semantic search for wholesale suppliers |
| **Negotiation** | Vapi TTS | Real phone calls to negotiate bulk discounts |
| **Evaluation** | Voyage AI + Claude | Score and select optimal vendors |
| **Payment** | x402 + Browserbase | Cryptographic authorization + automated execution |
| **Message** | OpenAI + Vonage | SMS-based conversational ordering |

### x402 Payment Authorization

Haggl uses the [x402 protocol](https://github.com/coinbase/x402) for secure, autonomous payment authorization:

- **Budget enforcement** - Per-transaction and daily limits
- **On-chain proof** - USDC transfers to escrow create audit trail
- **Single-use tokens** - Authorization tokens prevent replay attacks
- **AI-safe credentials** - ACH/banking details never exposed to AI
- **Escrow management** - Funds locked until payment confirmed, then released to vendor

### Browserbase Integration

Cloud browser automation for real payment portal navigation:

- Navigate any vendor payment portal (Intuit QuickBooks, Stripe, etc.)
- Claude Vision parses invoice details from screenshots
- Securely inject ACH credentials from encrypted vault
- Capture confirmation screenshots
- No local browser setup required

### Encrypted Credential Vault

AES-256-GCM encrypted storage for sensitive payment credentials:

- ACH routing/account numbers encrypted at rest
- MongoDB Atlas storage with field-level encryption
- Credentials decrypted only at moment of injection
- AI agents NEVER see credential values
- Full audit logging for compliance

## 📦 Installation

```bash
# Clone the repo
git clone https://github.com/anirudhk-tech/Haggl.git
cd Haggl

# Install dependencies
pip install -e .

# Or with uv
uv sync
```

### Optional Dependencies

```bash
# For real CDP wallet integration
pip install cdp-sdk

# For browser automation
pip install playwright
playwright install chromium

# Full production stack
pip install -e ".[full]"
```

## 🔧 Configuration

Copy `env.example` to `.env` and fill in your values:

```bash
cp env.example .env
```

Key configuration:

```bash
# MongoDB Atlas (for credential vault and escrow tracking)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net
MONGODB_DB=haggl

# Credential Vault Encryption
VAULT_MASTER_KEY=your-secure-master-key-at-least-32-chars

# Browserbase (cloud browser automation)
BROWSERBASE_PROJECT_ID=54733070-252e-42f2-a759-9ac4904fb508
BROWSERBASE_API_KEY=bb_live_your_key_here

# Anthropic Claude (invoice parsing)
ANTHROPIC_API_KEY=sk-ant-...

# CDP (for real x402 - optional, mock mode works without)
CDP_API_KEY_NAME=your_cdp_key
CDP_API_KEY_PRIVATE_KEY=your_private_key

# Demo ACH Credentials
ACH_ROUTING_NUMBER=021000021
ACH_ACCOUNT_NUMBER=1234567890
ACH_ACCOUNT_NAME=Your Business Name
```

## 🎮 Quick Start

### Demo: Full Payment Flow

```bash
# Run the complete x402 + escrow + payment demo
python demo_full_flow.py
```

Output:
```
======================================================================
🚀 HAGGL x402 FULL PAYMENT FLOW DEMO
======================================================================

📋 Invoice Details:
   ID: INV-20260110203600
   Vendor: Acme Supplies Inc.
   Amount: $150.0
   Budget: $500.0 remaining of $1000.0

----------------------------------------------------------------------
📦 STEP 1: Store ACH Credentials in Encrypted Vault
----------------------------------------------------------------------
   ✅ Credentials stored: cred_79d5da94056b5a99
   📄 Stored info: ****0021 / ****9012

----------------------------------------------------------------------
🔐 STEP 2: x402 Authorization (Creates Escrow Lock)
----------------------------------------------------------------------
   ✅ Authorization granted!
   🔑 Auth Token: QfgJTJaKwcVvWDxETKSk...
   📜 TX Hash: 0x8f95e8c4af7d63a2b2...
   🏦 Escrow: 0xMockEscrow...
   💰 Escrow Lock: escrow_8c65d6598bde2766
   💵 Amount Locked: $150.0 USDC

----------------------------------------------------------------------
💳 STEP 3: Payment Execution
----------------------------------------------------------------------
   ✅ Payment Status: processing
   🏦 Method: mock_ach
   📝 ACH Transfer ID: ach_82f2ab1a8b8ff16b
   📋 Confirmation: ACH-INV-20260110203600-9522948D

----------------------------------------------------------------------
🔓 STEP 4: Release Escrow to Vendor
----------------------------------------------------------------------
   ✅ Escrow Released!
   📋 Release ID: release_15396c94508d5d9a
   💵 Amount: $150.0 USDC
```

### Demo: Real Browser Payment

```bash
# Pay a real Intuit QuickBooks invoice using Browserbase
python demo_full_flow.py --real
```

### Start the API Server

```bash
# Start the main server (includes all agents)
uvicorn src.server:app --reload --port 8000
```

## 🔌 API Endpoints

### x402 Payment Agent

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/x402/authorize` | POST | Request payment authorization |
| `/x402/pay` | POST | Execute authorized payment |
| `/x402/authorize-and-pay` | POST | Both in one call |
| `/x402/status/{invoice_id}` | GET | Check payment status |
| `/x402/spending` | GET | View spending summary |
| `/x402/wallet` | GET | View wallet info |

### Credential Vault

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/vault/credentials` | POST | Store encrypted ACH credentials |
| `/vault/credentials/{business_id}` | GET | Get masked credential info |
| `/vault/credentials/{business_id}` | DELETE | Delete credentials |

### Escrow Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/escrow/release` | POST | Release escrow to vendor |
| `/escrow/stats` | GET | Get escrow statistics |
| `/escrow/{invoice_id}` | GET | Get escrow for invoice |

### Browser Automation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/browser/pay-invoice` | POST | Pay invoice via browser |
| `/browser/parse-invoice` | POST | Parse invoice from URL |

### Calling Agent

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agent/order` | POST | Place order via voice call |
| `/agent/status/{order_id}` | GET | Check order status |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                               │
│              "500 lbs flour, 1000 eggs, budget $2000"           │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │  SOURCING   │    │ NEGOTIATION │    │ EVALUATION  │
   │  (Exa.ai)   │    │   (Vapi)    │    │ (Voyage AI) │
   │             │    │             │    │             │
   │ Find 10+    │    │ Real phone  │    │ Score &     │
   │ suppliers   │    │ calls       │    │ optimize    │
   └─────────────┘    └─────────────┘    └─────────────┘
          │                   │                   │
          └───────────────────┴───────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    x402 AUTHORIZATION                            │
│                                                                  │
│  • Budget check (per-tx, daily limits)                          │
│  • USDC → Escrow (on-chain proof)                               │
│  • Generate single-use auth token                                │
│  • Create escrow lock in MongoDB                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CREDENTIAL VAULT                               │
│                                                                  │
│  • AES-256-GCM encrypted ACH credentials                        │
│  • MongoDB Atlas storage                                         │
│  • Decrypted only at injection time                             │
│  • Full audit logging                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 BROWSERBASE EXECUTION                            │
│                                                                  │
│  • Cloud browser session                                         │
│  • Navigate vendor payment portal                                │
│  • Claude Vision parses invoice                                  │
│  • Secure credential injection (AI never sees values)           │
│  • Submit payment, capture confirmation                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ESCROW RELEASE                                │
│                                                                  │
│  • Verify payment confirmation                                   │
│  • Release USDC to vendor                                        │
│  • Update MongoDB records                                        │
│  • Generate audit trail                                          │
└─────────────────────────────────────────────────────────────────┘
```

## 🔐 Security

### Credential Isolation

```
┌─────────────────────────────────────────────────────────────────┐
│  AI AGENT CAN:                    │  AI AGENT CANNOT:           │
│  ─────────────                    │  ────────────────           │
│  • See payment portal UI          │  • See credential values    │
│  • Identify form field locations  │  • Type credential values   │
│  • Click buttons/links            │  • Access credential vault  │
│  • Read confirmation numbers      │  • Modify spending policies │
│  • Report errors                  │  • Bypass x402 authorization│
│  • Parse invoice amounts          │  • Release escrow directly  │
└─────────────────────────────────────────────────────────────────┘
```

### Defense in Depth

1. **CDP Wallet Policies** - TEE-enforced spending limits
2. **x402 Authorization** - On-chain audit trail
3. **Credential Vault** - AES-256-GCM encrypted, runtime injection only
4. **Escrow Management** - Funds locked until payment confirmed
5. **Execution Sandbox** - Isolated browser environment
6. **MongoDB Audit Log** - Full trail of all operations

## 📁 Project Structure

```
Haggl/
├── src/
│   ├── calling_agent/       # Vapi voice calling
│   │   ├── agent.py         # Call orchestration
│   │   ├── server.py        # FastAPI endpoints
│   │   └── tools/
│   │       └── vapi_tool.py # Vapi integration
│   │
│   ├── sourcing_agent/      # Vendor discovery
│   │   ├── agent.py         # Exa.ai search
│   │   └── tools/
│   │       ├── exa_tool.py  # Exa.ai API
│   │       └── extractor.py # Claude extraction
│   │
│   ├── evaluation_agent/    # Vendor scoring
│   │   ├── agent.py         # Voyage AI embeddings
│   │   └── fine_tune.py     # Preference learning
│   │
│   ├── message_agent/       # SMS ordering
│   │   ├── agent.py         # Conversation handler
│   │   └── tools/
│   │       └── vonage_tool.py
│   │
│   ├── x402/                # Authorization layer
│   │   ├── authorizer.py    # Budget enforcement
│   │   ├── wallet.py        # CDP wallet integration
│   │   ├── credential_vault.py  # Encrypted ACH storage
│   │   ├── escrow.py        # Escrow management
│   │   ├── mongodb.py       # Database setup
│   │   └── schemas.py       # Pydantic models
│   │
│   ├── payment_agent/       # Payment execution
│   │   ├── executor.py      # Mock Stripe/ACH
│   │   ├── browserbase.py   # Cloud browser automation
│   │   └── server.py        # FastAPI endpoints
│   │
│   └── server.py            # Main FastAPI app
│
├── plans/                   # Architecture docs
├── configs/                 # Agent configs
├── demo_full_flow.py       # Complete demo script
├── env.example             # Environment template
└── main.py                 # Entry point
```

## 🧪 Testing

```bash
# Run full payment flow demo (no credentials needed)
python demo_full_flow.py

# Run with real Browserbase sessions
python demo_full_flow.py --real

# Run with pytest
pytest
```

## 🌐 Testnet Setup

For real x402 transactions on Base Sepolia:

1. **Get CDP credentials** at [portal.cdp.coinbase.com](https://portal.cdp.coinbase.com)
2. **Download** `cdp_api_key.json`
3. **Request testnet USDC** via CDP Faucet API

```python
from cdp import CdpClient

cdp = CdpClient.from_json("cdp_api_key.json")
account = cdp.evm.create_account(network="base-sepolia")

# Get testnet USDC (free)
cdp.evm.request_faucet(address=account.address, network="base-sepolia", token="usdc")
```

## 🗄️ MongoDB Atlas Setup

1. Create a free cluster at [cloud.mongodb.com](https://cloud.mongodb.com)
2. Create a database user with read/write access
3. Whitelist your IP address
4. Copy the connection string to `MONGODB_URI`

Collections created automatically:
- `credentials` - Encrypted ACH credentials
- `escrow_locks` - Active escrow records
- `escrow_releases` - Completed releases
- `authorizations` - x402 authorization records
- `payments` - Payment execution records
- `audit_log` - Security audit trail

## 📚 Resources

- [x402 Protocol](https://github.com/coinbase/x402) - Coinbase payment authorization
- [Browserbase](https://browserbase.com) - Cloud browser automation
- [CDP Wallets](https://docs.cdp.coinbase.com/server-wallets/v2/evm-features/spend-permissions) - Spending policies
- [Vapi](https://vapi.ai) - Voice AI for phone calls
- [Voyage AI](https://www.voyageai.com) - Embedding models
- [MongoDB Atlas](https://www.mongodb.com/atlas) - Cloud database

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

Built for hackathon demos. x402 authorization + encrypted vault + Browserbase execution = true autonomous agent payments.
