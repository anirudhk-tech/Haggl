# Haggl Architecture

## Overview

Haggl is a multi-agent AI system designed to automate procurement for small businesses. This document describes the high-level architecture, data flows, and design decisions.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │   Next.js App   │    │  WhatsApp/SMS   │    │   REST Client   │         │
│  │   (Dashboard)   │    │    (Vonage)     │    │    (Postman)    │         │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘         │
│           │                      │                      │                   │
│           └──────────────────────┼──────────────────────┘                   │
│                                  │                                          │
│                          ┌───────▼───────┐                                  │
│                          │   SSE Stream  │                                  │
│                          │  /events/stream│                                 │
│                          └───────────────┘                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                      ┌─────────────────────┐                                │
│                      │   FastAPI Server    │                                │
│                      │   (src/server.py)   │                                │
│                      └─────────┬───────────┘                                │
│                                │                                            │
│   ┌────────────────────────────┼────────────────────────────┐              │
│   │                            │                            │              │
│   ▼                            ▼                            ▼              │
│ /webhooks/*              /orders/*                    /events/*            │
│ (Vonage, Vapi)          (CRUD, Approve)              (SSE Stream)          │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            AGENT LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    │
│  │   Message   │   │  Sourcing   │   │   Calling   │   │ Evaluation  │    │
│  │    Agent    │──▶│    Agent    │──▶│    Agent    │──▶│    Agent    │    │
│  │  (Vonage)   │   │  (Exa.ai)   │   │   (Vapi)    │   │ (Voyage AI) │    │
│  └─────────────┘   └─────────────┘   └─────────────┘   └──────┬──────┘    │
│                                                                │           │
│                                                                ▼           │
│                                                        ┌─────────────┐    │
│                                                        │   Payment   │    │
│                                                        │    Agent    │    │
│                                                        │  (Stripe)   │    │
│                                                        └─────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        MongoDB Atlas                                 │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ vendors  │ │  orders  │ │  calls   │ │ convos   │ │businesses│  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Agent Architecture

### Agent Communication Pattern

```
┌──────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATION FLOW                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User Request: "I need 12 dozen eggs"                           │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────┐                                                │
│  │   Message   │  1. Parse intent (OpenAI function calling)     │
│  │    Agent    │  2. Extract: product="eggs", qty=12, unit="doz"│
│  └──────┬──────┘                                                │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │  Sourcing   │  3. Search Exa.ai for vendors                  │
│  │    Agent    │  4. Return top 3 vendors with metadata         │
│  └──────┬──────┘                                                │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │   Calling   │  5. Call 3 vendors in parallel (asyncio)       │
│  │    Agent    │  6. Negotiate pricing via Vapi voice AI        │
│  └──────┬──────┘  7. Collect transcripts and quotes             │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │ Evaluation  │  8. Score vendors on price, quality, reliability│
│  │    Agent    │  9. Apply learned preferences (Voyage AI)      │
│  └──────┬──────┘  10. Return best vendor                        │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │   Payment   │  11. User approves                              │
│  │    Agent    │  12. Execute payment (mock/real)               │
│  └──────┬──────┘  13. Confirm order                             │
│         │                                                        │
│         ▼                                                        │
│  Response: "Order confirmed! $XX.XX from [Vendor]"              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

| Agent | Purpose | External APIs | Key Features |
|-------|---------|---------------|--------------|
| **Message Agent** | User communication | Vonage (WhatsApp/SMS) | OpenAI function calling, conversation history |
| **Sourcing Agent** | Vendor discovery | Exa.ai | Semantic search, vendor metadata extraction |
| **Calling Agent** | Price negotiation | Vapi | Voice AI, parallel calls, transcript capture |
| **Evaluation Agent** | Vendor selection | Voyage AI | Preference learning, multi-criteria scoring |
| **Payment Agent** | Transaction execution | Stripe, Browserbase | Mock payments, ACH automation |

## Data Models

### Core Entities

```python
# Order Lifecycle
class OrderDocument:
    order_id: str           # UUID
    business_id: str        # Reference to business
    product: str            # "eggs"
    quantity: int           # 12
    unit: str               # "dozen"
    status: OrderStatus     # pending → calling → evaluating → approved → paid
    vendor_id: str | None   # Selected vendor
    price: float | None     # Final price
    created_at: datetime
    updated_at: datetime

# Call Record
class CallDocument:
    call_id: str            # Vapi call ID
    order_id: str           # Reference to order
    vendor_id: str          # Reference to vendor
    status: CallStatus      # initiated → connected → completed → failed
    transcript: str | None  # Full conversation
    quoted_price: float | None
    duration_seconds: int
    created_at: datetime

# Vendor Profile
class VendorDocument:
    vendor_id: str
    name: str
    phone: str
    products: list[str]
    quality_score: float    # 0-100
    reliability_score: float
    certifications: list[str]
    embedding: list[float]  # 1536-dim vector
```

### Event Schema

```python
class AgentEvent:
    event_type: EventType   # stage_change, log, call_update, etc.
    stage: AgentStage       # sourcing, calling, evaluating, etc.
    order_id: str | None
    message: str
    data: dict | None
    timestamp: datetime
```

## Event-Driven Architecture

### Server-Sent Events (SSE)

The frontend subscribes to real-time updates via SSE:

```
GET /events/stream?order_id=xxx

event: stage_change
data: {"stage": "sourcing", "message": "Finding vendors..."}

event: call_update
data: {"vendor_name": "Farm Fresh", "status": "connected"}

event: approval_required
data: {"best_vendor": {...}, "price": 45.00}
```

### Event Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Backend │────▶│EventBus │────▶│  SSE    │────▶│Frontend │
│ Agents  │emit │ Queue   │push │ Stream  │recv │  React  │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
```

## Concurrency Model

### Parallel Vendor Calling

```python
async def place_orders_parallel(vendors: list[VendorInfo]) -> list[CallResult]:
    """Call up to 3 vendors simultaneously."""
    
    tasks = [
        call_single_vendor(vendor, product, quantity)
        for vendor in vendors[:3]
    ]
    
    # Execute all calls in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return [r for r in results if not isinstance(r, Exception)]
```

### Background Task Processing

Long-running operations run in background tasks:

```python
@app.post("/orders/create")
async def create_order(request: CreateOrderRequest):
    order_id = str(uuid.uuid4())
    
    # Return immediately
    asyncio.create_task(
        process_order_flow(order_id, request)
    )
    
    return {"order_id": order_id, "status": "processing"}
```

## Security Architecture

### Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────▶│  Server  │────▶│ MongoDB  │
│          │JWT  │ Validate │     │  Query   │
└──────────┘     └──────────┘     └──────────┘
```

### Webhook Verification

```python
def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify Vonage webhook signatures."""
    expected = hmac.new(
        VONAGE_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## Deployment Architecture

### Production Setup

```
┌─────────────────────────────────────────────────────────────┐
│                        CLOUDFLARE                            │
│                     (CDN + DDoS Protection)                  │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
       ┌──────────┐    ┌──────────┐    ┌──────────┐
       │ Frontend │    │ Backend  │    │ Backend  │
       │ (Vercel) │    │ (Fly.io) │    │ (Fly.io) │
       └──────────┘    └────┬─────┘    └────┬─────┘
                            │               │
                            └───────┬───────┘
                                    ▼
                          ┌─────────────────┐
                          │  MongoDB Atlas  │
                          │   (M10+ Cluster)│
                          └─────────────────┘
```

### Environment Configuration

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | ✅ |
| `VAPI_API_KEY` | Vapi.ai API key | ✅ |
| `VONAGE_API_KEY` | Vonage API key | ✅ |
| `MONGODB_URI` | MongoDB connection string | ✅ |
| `EXA_API_KEY` | Exa.ai API key | ✅ |
| `VOYAGE_API_KEY` | Voyage AI key | Optional |

## Performance Considerations

### Optimization Strategies

1. **Connection Pooling**: MongoDB driver maintains connection pool
2. **Async I/O**: All network calls use `httpx` async client
3. **Event Batching**: SSE events are buffered before sending
4. **Caching**: Vendor embeddings cached in memory (hot data)

### Scalability Path

- **Horizontal**: Add more backend instances behind load balancer
- **Vertical**: Increase MongoDB cluster tier
- **Async Workers**: Move heavy processing to Celery/RQ workers

## Future Architecture

### Planned Enhancements

1. **Vector Search**: Native MongoDB Atlas Vector Search for vendors
2. **Multi-tenancy**: Business isolation at database level
3. **Webhook Queue**: Redis-backed webhook processing queue
4. **Agent Memory**: Long-term memory via vector database
5. **A/B Testing**: Feature flags for agent behavior variants
