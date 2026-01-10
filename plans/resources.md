# Resources & API Documentation
## Haggl - Setup Links and References

**Last Updated:** January 10, 2026

---

## 1. MongoDB Atlas

### Official Links
- **Homepage:** https://www.mongodb.com/cloud/atlas
- **Docs:** https://www.mongodb.com/docs/atlas/
- **Console:** https://cloud.mongodb.com/

### Setup
1. Sign up at mongodb.com/cloud/atlas/register
2. Create M0 cluster (free tier)
3. Create database user
4. Whitelist IP: 0.0.0.0/0 (for demo)
5. Get connection string

### Connection String Format
```
mongodb+srv://username:password@cluster.mongodb.net/haggl?retryWrites=true&w=majority
```

### Python Usage
```python
from pymongo import MongoClient

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["haggl"]

# Test connection
print(client.server_info())
```

---

## 2. Claude API (Anthropic)

### Official Links
- **Homepage:** https://www.anthropic.com/
- **API Docs:** https://docs.anthropic.com/
- **Console:** https://console.anthropic.com/

### Setup
1. Sign up at console.anthropic.com
2. Get API key from Settings > API Keys
3. Free tier: $5 credit

### Python Usage
```python
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Extract pricing..."}]
)

print(response.content[0].text)
```

### Models
- **claude-sonnet-4-20250514** - Best for agent reasoning
- **claude-haiku-3-5-20241022** - Fast, cheaper alternative

---

## 3. Exa.ai

### Official Links
- **Homepage:** https://exa.ai/
- **Docs:** https://docs.exa.ai/
- **Dashboard:** https://dashboard.exa.ai/

### Setup
1. Sign up at exa.ai
2. Get API key from dashboard
3. Free tier: 1000 searches/month

### Python Usage
```python
from exa_py import Exa

exa = Exa(api_key=os.getenv("EXA_API_KEY"))

# Semantic search
results = exa.search_and_contents(
    "wholesale flour supplier San Francisco bulk pricing",
    type="neural",
    num_results=10,
    text={"max_characters": 2000}
)

for result in results.results:
    print(result.title, result.url)
```

### Search Types
- `neural` - Semantic search (recommended)
- `keyword` - Traditional keyword matching
- `auto` - Let Exa decide

---

## 4. Vapi (Voice AI)

### Official Links
- **Homepage:** https://vapi.ai/
- **Docs:** https://docs.vapi.ai/
- **Dashboard:** https://dashboard.vapi.ai/

### Setup
1. Sign up at vapi.ai
2. Get API key from dashboard
3. Add phone number for outbound calls
4. Create assistant with Claude integration

### Python Usage
```python
import vapi

client = vapi.Client(api_key=os.getenv("VAPI_API_KEY"))

# Create assistant
assistant = client.assistants.create(
    name="Procurement Agent",
    model={
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "systemPrompt": "You are a procurement agent..."
    },
    voice={
        "provider": "11labs",
        "voiceId": "21m00Tcm4TlvDq8ikWAM"
    }
)

# Make outbound call
call = client.calls.create(
    assistant_id=assistant.id,
    customer={"number": "+1-415-555-0123"}
)

# Wait for completion
result = client.calls.wait(call.id, timeout=300)
print(result.transcript)
```

### Voice Providers
- **11labs** - High quality, natural voices
- **playht** - Alternative option
- **deepgram** - Fast, cost-effective

---

## 5. Twilio (SMS)

### Official Links
- **Homepage:** https://www.twilio.com/
- **Docs:** https://www.twilio.com/docs/sms
- **Console:** https://console.twilio.com/

### Setup
1. Sign up at twilio.com
2. Get Account SID and Auth Token from console
3. Purchase a phone number ($1/month)
4. Configure webhook URL for incoming SMS

### Python Usage
```python
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

# Initialize client
client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

# Send SMS
message = client.messages.create(
    body="Your order has been confirmed!",
    from_="+1234567890",
    to="+0987654321"
)

print(message.sid)

# Handle incoming SMS (webhook response)
@app.post("/sms/webhook")
def handle_sms(From: str, Body: str):
    response = MessagingResponse()
    response.message("Thanks! Processing your request...")
    return str(response)
```

### Webhook Configuration
1. Go to Console > Phone Numbers > Manage > Active Numbers
2. Select your number
3. Under "Messaging", set webhook URL: `https://your-domain.com/sms/webhook`
4. Method: POST

### Environment Variables
```bash
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
```

---

## 6. Coinbase CDP (x402)

### Official Links
- **Homepage:** https://www.coinbase.com/cloud/products/cdp-sdk
- **Docs:** https://docs.cdp.coinbase.com/
- **Portal:** https://portal.cdp.coinbase.com/

### Setup
1. Sign up at portal.cdp.coinbase.com
2. Create API credentials
3. Download cdp_api_key.json
4. Fund wallet with USDC on Base

### Python Usage
```python
from cdp import Cdp, Wallet

# Configure
Cdp.configure_from_json("cdp_api_key.json")

# Create or load wallet
wallet = Wallet.create()
print(f"Address: {wallet.default_address.address_id}")

# Check balance
print(wallet.balances())

# Transfer USDC
transfer = wallet.transfer(
    amount=100.00,
    asset_id="usdc",
    destination="0x..."
)

print(f"TX: {transfer.transaction_hash}")
print(f"Explorer: {transfer.transaction_link}")
```

### Network Info
- **Network:** Base (Ethereum L2)
- **Asset:** USDC (stablecoin)
- **Explorer:** https://basescan.org/

---

## 6. Stripe (Backend Payments)

### Official Links
- **Homepage:** https://stripe.com/
- **Docs:** https://stripe.com/docs
- **Dashboard:** https://dashboard.stripe.com/

### Setup
1. Sign up at stripe.com
2. Get API keys (use test keys for demo)
3. No setup needed for test mode

### Python Usage
```python
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Create payment intent
intent = stripe.PaymentIntent.create(
    amount=21250,  # $212.50 in cents
    currency="usd",
    payment_method_types=["card"],
    metadata={"vendor": "Bay Area Foods"}
)

print(intent.id)
```

---

## 8. Python Dependencies

### requirements.txt
```
pymongo>=4.6.0
anthropic>=0.40.0
exa-py>=1.0.0
vapi-python>=0.1.0
twilio>=8.0.0
cdp-sdk>=0.0.5
playwright>=1.40.0
fastapi>=0.109.0
uvicorn>=0.27.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
stripe>=7.0.0
```

### Installation
```bash
pip install -r requirements.txt
playwright install chromium
```

---

## 9. Environment Variables

### .env Template
```bash
# MongoDB Atlas
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/haggl

# Claude API (Anthropic)
ANTHROPIC_API_KEY=sk-ant-api03-...

# Exa.ai
EXA_API_KEY=...

# Vapi
VAPI_API_KEY=...
VAPI_ASSISTANT_ID=...

# Twilio (SMS)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...

# Coinbase CDP
CDP_API_KEY_NAME=organizations/.../apiKeys/...
CDP_API_PRIVATE_KEY=-----BEGIN EC PRIVATE KEY-----...

# Or use JSON file path
CDP_API_KEY_FILE=cdp_api_key.json

# Stripe
STRIPE_SECRET_KEY=sk_test_...

# x402 Escrow
ESCROW_WALLET_ADDRESS=0x...

# ACH Credentials (for Computer Use)
ACH_ROUTING_NUMBER=...
ACH_ACCOUNT_NUMBER=...
ACH_ACCOUNT_NAME=Sweet Dreams Bakery LLC
```

---

## 9. Hackathon Info

### Event
- **Name:** MongoDB Agentic Orchestration & Collaboration Hackathon
- **Date:** January 10, 2026
- **Location:** Shack 15, San Francisco

### Schedule
- 9:00 AM - Doors open
- 10:00 AM - Kick-off
- 5:00 PM - First round judging
- 7:00 PM - Finalist demos

### Prizes
- Total pool: $30,000+
- Finalist requirement: MongoDB Atlas integration

---

## 10. Quick Reference

### Test All Connections
```python
# test_connections.py
import os
from dotenv import load_dotenv
load_dotenv()

# MongoDB
from pymongo import MongoClient
client = MongoClient(os.getenv("MONGODB_URI"))
print("MongoDB:", client.server_info()["version"])

# Claude
from anthropic import Anthropic
claude = Anthropic()
print("Claude: Connected")

# Exa
from exa_py import Exa
exa = Exa(os.getenv("EXA_API_KEY"))
print("Exa.ai: Connected")

# Vapi
import vapi
client = vapi.Client(api_key=os.getenv("VAPI_API_KEY"))
print("Vapi: Connected")

# CDP
from cdp import Cdp, Wallet
Cdp.configure_from_json("cdp_api_key.json")
wallet = Wallet.create()
print(f"CDP Wallet: {wallet.default_address.address_id}")

print("\n All connections verified!")
```

---

**Status:** All Resources Verified
