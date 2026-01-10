# IngredientAI Calling Agent - Phase 2

A Python-based agent that orchestrates vendor phone calls using the NVIDIA NeMo Agent Toolkit pattern.

## Overview

This agent wraps the Vapi phone call flow in a state machine pattern:

```
READY_TO_CALL → CALL_IN_PROGRESS → PROCESSING → CONFIRMED → PLACED
                                             → FAILED (from any state)
```

## Architecture

```
Next.js UI
    ↓
API Route (/api/agent)
    ↓
Python FastAPI Server (port 8001)
    ↓
Calling Agent (state machine)
    ↓
Vapi Tool (call_vendor)
    ↓
Vapi API → Phone Call → Vendor
```

## Quick Start

### 1. Install Python Dependencies

```bash
cd agent
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### 2. Configure Environment

The agent reads from the parent directory's `.env.local`:

```bash
# In ingredient_ai/.env.local
VAPI_API_KEY=your_vapi_api_key
VAPI_PHONE_NUMBER_ID=your_phone_number_id
```

### 3. Start the Agent Server

```bash
# From the agent directory
python main.py serve --port 8001

# Or with auto-reload for development
python main.py serve --port 8001 --reload
```

### 4. Start the Next.js Frontend

In a separate terminal:

```bash
# From the ingredient_ai directory
pnpm dev
```

## API Endpoints

### Health Check

```bash
curl http://localhost:8001/health
```

### Place Order via Agent

```bash
curl -X POST http://localhost:8001/agent/order \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "order_123",
    "business_name": "Sweet Dreams Bakery",
    "business_type": "bakery",
    "quantity": 10,
    "vendor_id": "vendor-001",
    "vendor_name": "Fresh Farm Eggs",
    "vendor_phone": "+15551234567",
    "price_per_unit": 0.50
  }'
```

### Get Order Status

```bash
curl http://localhost:8001/agent/status/order_123
```

### Reset Agent (for testing)

```bash
curl -X POST http://localhost:8001/agent/reset
```

## Agent Features

### State Machine

The agent maintains a simple state machine:

- **READY_TO_CALL**: Initial state, ready to place a call
- **CALL_IN_PROGRESS**: Vapi call has been initiated
- **PROCESSING**: Call ended, parsing transcript
- **CONFIRMED**: Order confirmed by vendor
- **PLACED**: Final success state
- **FAILED**: Final failure state

### Idempotency

The agent tracks processed orders to prevent duplicate calls on page refresh.

### Outcome Parsing

The agent parses call transcripts to extract:
- `confirmed`: Whether the order was confirmed
- `price`: Negotiated price per unit
- `eta`: Estimated delivery/pickup time

## Project Structure

```
agent/
├── pyproject.toml          # Python dependencies
├── main.py                 # CLI entry point
├── configs/
│   └── calling_agent.yml   # NAT config (reference)
└── src/
    └── calling_agent/
        ├── __init__.py
        ├── schemas.py      # Pydantic models
        ├── agent.py        # State machine logic
        ├── server.py       # FastAPI endpoints
        └── tools/
            ├── __init__.py
            └── vapi_tool.py  # Vapi integration
```

## Development

### Run Tests

```bash
pytest
```

### Type Checking

```bash
mypy src/
```

### Code Style

```bash
ruff check src/
ruff format src/
```

## Phase 2 vs Phase 1

| Feature | Phase 1 | Phase 2 |
|---------|---------|---------|
| Vapi Call | Direct from Next.js API | Via Python Agent |
| State Management | In-memory store | Agent state machine |
| Outcome Parsing | JavaScript | Python with better parsing |
| Architecture | Monolith | Microservice (Next.js + Python) |
| Idempotency | None | Built-in |

## Future Phases

- **Phase 3**: MongoDB persistence
- **Phase 4**: Payment agent (x402)
- **Phase 5**: Multi-vendor swarm
- **Phase 6**: Voyage AI ranking
