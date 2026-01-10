# Haggl

**AI agents that source, negotiate, and pay for your business supplies autonomously.**

Haggl is a multi-agent B2B procurement system. A business owner inputs ingredient needs, quantities, and budget. Four specialized agents work concurrently to find suppliers, negotiate prices via real phone calls, evaluate options, and process payments using the x402 protocol.

## 🚀 Features

### Multi-Agent Architecture

| Agent | Technology | Purpose |
|-------|------------|---------|
| **Sourcing** | Exa.ai + Claude | Semantic search for wholesale suppliers |
| **Negotiation** | Vapi TTS | Real phone calls to negotiate bulk discounts |
| **Evaluation** | Claude + MongoDB | Score and select optimal vendors |
| **Payment** | x402 + Browserbase | Cryptographic authorization + automated execution |

### x402 Payment Authorization

Haggl uses the [x402 protocol](https://github.com/coinbase/x402) for secure, autonomous payment authorization:

- **Budget enforcement** - Per-transaction and daily limits
- **On-chain proof** - USDC transfers to escrow create audit trail
- **Single-use tokens** - Authorization tokens prevent replay attacks
- **AI-safe credentials** - ACH/banking details never exposed to AI

### Browserbase x402 Integration

Cloud browser automation paid with USDC:

- Navigate any vendor payment portal (Intuit, Stripe, etc.)
- Securely inject payment credentials
- Capture confirmation screenshots
- No local browser setup required

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

Create a `.env` file:

```bash
# Vapi (for voice calling)
VAPI_API_KEY=your_vapi_key
VAPI_PHONE_NUMBER_ID=your_phone_id

# CDP (for real x402 - optional, mock mode works without)
CDP_API_KEY_NAME=your_cdp_key
CDP_API_KEY_PRIVATE_KEY=your_private_key
CDP_NETWORK=base-sepolia

# Browserbase (for real browser automation - optional)
BROWSERBASE_PROJECT_ID=your_project_id

# ACH Credentials (stored securely, never exposed to AI)
ACH_ROUTING_NUMBER=021000021
ACH_ACCOUNT_NUMBER=1234567890
ACH_ACCOUNT_NAME=Your Business Name

# MongoDB (for production)
MONGODB_URI=mongodb+srv://...

# Anthropic (for Claude vision)
ANTHROPIC_API_KEY=sk-ant-...
```

## 🎮 Quick Start

### Demo: x402 Payment Flow

```bash
# Run the x402 authorization + mock payment demo
python demo_x402.py
```

Output:
```
📊 BUDGET: $2000.00
📋 INVOICES TO PAY: 3

[PHASE 1] x402 AUTHORIZATION...
   ✅ AUTHORIZED
   🔗 TX Hash: 0x66830777fb34b2a4630e38e2d3a3e597...
   🌐 Explorer: https://sepolia.basescan.org/tx/0x...

[PHASE 2] PAYMENT EXECUTION...
   ✅ Payment SUCCEEDED
   🧾 Confirmation: ch_c8b18a7b09f520a894fa5fd0
```

### Demo: Real Invoice Payment (Intuit)

```bash
# Pay a real Intuit QuickBooks invoice
python demo_intuit_payment.py "https://connect.intuit.com/t/..."
```

### Start the API Server

```bash
# x402 Payment Agent (port 8002)
python demo_x402.py serve --port 8002

# Calling Agent (port 8001)
python main.py serve --port 8001
```

## 🔌 API Endpoints

### x402 Payment Agent (`localhost:8002`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/x402/authorize` | POST | Request payment authorization |
| `/x402/pay` | POST | Execute authorized payment |
| `/x402/authorize-and-pay` | POST | Both in one call |
| `/x402/status/{invoice_id}` | GET | Check payment status |
| `/x402/spending` | GET | View spending summary |
| `/x402/wallet` | GET | View wallet info |

### Calling Agent (`localhost:8001`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agent/order` | POST | Place order via voice call |
| `/agent/status/{order_id}` | GET | Check order status |
| `/health` | GET | Health check |

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
   │  (Exa.ai)   │    │   (Vapi)    │    │  (Claude)   │
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
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 BROWSERBASE x402 EXECUTION                       │
│                                                                  │
│  • Pay for cloud browser with USDC                              │
│  • Navigate vendor payment portal                                │
│  • Secure credential injection (AI never sees values)           │
│  • Submit payment, capture confirmation                          │
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
└─────────────────────────────────────────────────────────────────┘
```

### Defense in Depth

1. **CDP Wallet Policies** - TEE-enforced spending limits
2. **x402 Authorization** - On-chain audit trail
3. **Credential Vault** - Encrypted, runtime injection only
4. **Execution Sandbox** - Isolated browser environment
5. **Monitoring** - Real-time anomaly detection

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
│   ├── x402/                # Authorization layer
│   │   ├── authorizer.py    # Budget enforcement
│   │   ├── wallet.py        # CDP wallet integration
│   │   └── schemas.py       # Pydantic models
│   │
│   └── payment_agent/       # Payment execution
│       ├── executor.py      # Mock Stripe/ACH
│       ├── browserbase.py   # Browserbase x402
│       └── server.py        # FastAPI endpoints
│
├── plans/                   # Architecture docs
├── configs/                 # Agent configs
├── demo_x402.py            # x402 demo script
├── demo_intuit_payment.py  # Intuit invoice demo
└── main.py                 # Entry point
```

## 🧪 Testing

```bash
# Run x402 demo (no credentials needed)
python demo_x402.py

# Run Intuit payment demo
python demo_intuit_payment.py

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

## 📚 Resources

- [x402 Protocol](https://github.com/coinbase/x402) - Coinbase payment authorization
- [Browserbase x402](https://docs.browserbase.com/integrations/x402/introduction) - Cloud browser sessions
- [CDP Wallets](https://docs.cdp.coinbase.com/server-wallets/v2/evm-features/spend-permissions) - Spending policies
- [Vapi](https://vapi.ai) - Voice AI for phone calls

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

Built for hackathon demos. x402 authorization + Browserbase execution = true autonomous agent payments.
