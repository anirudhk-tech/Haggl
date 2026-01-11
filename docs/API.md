# Haggl API Reference

## Base URL

```
Development: http://localhost:8001
Production:  https://api.haggl.com
```

## Authentication

Currently, the API uses API key authentication for external services (Vonage, Vapi webhooks). Business endpoints use `business_id` for identification.

---

## Orders API

### Create Order

Start a new procurement flow.

```http
POST /orders/create
Content-Type: application/json
```

**Request Body:**
```json
{
  "business_id": "uuid",
  "items": [
    {
      "product": "eggs",
      "quantity": 12,
      "unit": "dozen"
    }
  ],
  "phone_number": "+15551234567",
  "delivery_date": "2026-01-15",
  "delivery_address": "123 Main St, Austin, TX"
}
```

**Response:**
```json
{
  "order_id": "uuid",
  "status": "processing"
}
```

### Get Pending Approvals

Fetch orders awaiting user approval.

```http
GET /orders/pending
```

**Response:**
```json
{
  "pending_approvals": [
    {
      "order_id": "uuid",
      "product": "eggs",
      "quantity": 12,
      "unit": "dozen",
      "best_vendor": {
        "name": "Farm Fresh Eggs",
        "price": 45.00,
        "quality_score": 92
      },
      "created_at": "2026-01-11T10:30:00Z"
    }
  ]
}
```

### Approve Order

Approve a pending order and trigger payment.

```http
POST /orders/approve
Content-Type: application/json
```

**Request Body:**
```json
{
  "order_id": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Order approved, processing payment"
}
```

---

## Events API

### Stream Events (SSE)

Subscribe to real-time agent events.

```http
GET /events/stream?order_id=uuid
Accept: text/event-stream
```

**Event Types:**

| Event | Description |
|-------|-------------|
| `stage_change` | Agent stage transition |
| `log` | Agent log message |
| `call_update` | Vendor call status update |
| `vendor_update` | Vendor data received |
| `approval_required` | Order ready for approval |
| `payment_update` | Payment status change |

**Example Event:**
```
event: call_update
data: {"stage":"calling","order_id":"uuid","message":"Connected to Farm Fresh","data":{"vendor_name":"Farm Fresh","status":"connected"}}
```

### Get Recent Events

Fetch historical events.

```http
GET /events/recent?limit=50
```

**Response:**
```json
{
  "events": [
    {
      "event_type": "stage_change",
      "stage": "sourcing",
      "order_id": "uuid",
      "message": "Finding vendors for eggs...",
      "timestamp": "2026-01-11T10:30:00Z"
    }
  ]
}
```

### Test Event (Debug)

Emit a test event for debugging.

```http
POST /events/test
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Test event",
  "order_id": "uuid"
}
```

---

## Business API

### Complete Onboarding

Register a new business.

```http
POST /onboarding/complete
Content-Type: application/json
```

**Request Body:**
```json
{
  "business_name": "Acme Bakery",
  "business_type": "bakery",
  "location": "Austin, TX",
  "phone": "+15551234567",
  "selected_products": ["eggs", "flour", "butter"]
}
```

**Response:**
```json
{
  "success": true,
  "business_id": "uuid"
}
```

### Get Business Profile

```http
GET /business/{business_id}
```

**Response:**
```json
{
  "business_id": "uuid",
  "business_name": "Acme Bakery",
  "business_type": "bakery",
  "location": "Austin, TX",
  "phone": "+15551234567",
  "onboarding_complete": true,
  "selected_products": ["eggs", "flour", "butter"]
}
```

### Get Business by Phone

```http
GET /business/by-phone/{phone}
```

---

## Webhooks

### Vonage Inbound (WhatsApp/SMS)

```http
POST /webhooks/vonage/inbound
GET /webhooks/vonage/inbound
```

Receives incoming messages from Vonage. Supports both POST (JSON) and GET (query params).

**POST Body:**
```json
{
  "from": {"number": "15551234567"},
  "to": {"number": "12193674151"},
  "message": {"content": {"text": "I need eggs"}}
}
```

### Vonage Status

```http
POST /webhooks/vonage/status
```

Receives message delivery status updates.

### Vapi Webhook

```http
POST /calling/webhook
```

Receives Vapi call events (call started, ended, transcript, etc.).

---

## Messaging API

### Get Conversation History

```http
GET /messaging/history/{phone_number}
```

**Response:**
```json
{
  "phone_number": "+15551234567",
  "history": [
    {
      "role": "user",
      "content": "I need eggs",
      "timestamp": "2026-01-11T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "I found 3 vendors...",
      "timestamp": "2026-01-11T10:30:05Z"
    }
  ]
}
```

### Reset Conversation

```http
POST /messaging/reset/{phone_number}
```

### Reset All Conversations

```http
POST /messaging/reset
```

---

## Calling API

### Initiate Call (Direct)

Manually trigger a vendor call.

```http
POST /calling/call
Content-Type: application/json
```

**Request Body:**
```json
{
  "phone_number": "+15551234567",
  "vendor_name": "Farm Fresh",
  "business_name": "Acme Bakery",
  "items": [
    {"product": "eggs", "quantity": 12, "unit": "dozen"}
  ],
  "delivery_address": "123 Main St"
}
```

### Get Agent State

```http
GET /calling/state
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR"
}
```

**HTTP Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/orders/create` | 10/min |
| `/events/stream` | 5 connections |
| `/webhooks/*` | Unlimited |

---

## SDKs

Coming soon:
- Python SDK
- TypeScript SDK
- CLI tool
