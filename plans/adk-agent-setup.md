# Agent Development Kit (ADK) Setup Guide
## Haggl - NVIDIA NeMo Agent Toolkit Configuration

**Version:** 2.1
**Date:** January 10, 2026
**Framework:** NVIDIA NeMo Agent Toolkit (NAT)

---

## Overview

This guide covers setting up the 4 Haggl agents using **NVIDIA NeMo Agent Toolkit (NAT)**, an open-source library for connecting, evaluating, and accelerating teams of AI agents.

### Why NeMo Agent Toolkit?

| Feature | Benefit |
|---------|---------|
| **Framework Agnostic** | Works with LangChain, LlamaIndex, CrewAI, or raw Python |
| **YAML Configuration** | Rapid prototyping without code changes |
| **Multi-Agent Orchestration** | Built-in coordination and routing |
| **Profiling & Observability** | Track tokens, timings, bottlenecks |
| **MCP Support** | Model Context Protocol for remote tools |
| **Production Ready** | Rate limiting, auth, REST API server |

---

## Installation

```bash
# Create virtual environment (Python 3.11, 3.12, or 3.13 required)
python -m venv .venv_nat
source .venv_nat/bin/activate

# Install NeMo Agent Toolkit with all plugins
pip install "nvidia-nat[all]"

# Additional dependencies for Haggl
pip install anthropic pymongo exa-py httpx playwright pydantic twilio
playwright install chromium

# Verify installation
nat --help
```

---

## Project Structure

```
haggl/
├── pyproject.toml
├── configs/
│   ├── sourcing.yml          # Sourcing agent config
│   ├── negotiation.yml       # Negotiation agent config
│   ├── evaluation.yml        # Evaluation agent config
│   ├── payment.yml           # Payment agent config
│   ├── sms.yml               # SMS agent config
│   └── orchestrator.yml      # Multi-agent orchestrator
├── src/
│   └── haggl/
│       ├── __init__.py
│       ├── register.py       # Tool registration
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── exa_tools.py      # Sourcing tools (Exa.ai)
│       │   ├── vapi_tools.py     # Negotiation tools (Vapi)
│       │   ├── mongo_tools.py    # Database tools
│       │   ├── payment_tools.py  # x402 authorization
│       │   ├── browser_tools.py  # Computer Use (ACH)
│       │   ├── sms_tools.py      # SMS tools (Twilio)
│       │   └── csv_tools.py      # CSV ingestion tools
│       └── schemas/
│           ├── __init__.py
│           └── inputs.py         # Pydantic input schemas
├── frontend/                     # Dashboard UI
└── main.py
```

### Create Project Scaffold

```bash
# Create NAT workflow project
nat workflow create haggl

# Navigate to project
cd haggl
```

---

## Input Schemas (Pydantic)

```python
# src/haggl/schemas/inputs.py
from pydantic import BaseModel, Field


# =====================
# Sourcing Agent Schemas
# =====================

class SearchSuppliersInput(BaseModel):
    ingredient: str = Field(
        description="Ingredient to search for (e.g., 'all-purpose flour')"
    )
    location: str = Field(
        description="Geographic location (e.g., 'San Francisco, CA')"
    )
    quantity: str = Field(
        description="Quantity needed (e.g., '500 lbs')"
    )


class ExtractSupplierInfoInput(BaseModel):
    text: str = Field(
        description="Raw text from supplier webpage"
    )
    ingredient: str = Field(
        description="Target ingredient for extraction context"
    )


# =====================
# Negotiation Agent Schemas
# =====================

class MakePhoneCallInput(BaseModel):
    phone_number: str = Field(
        description="Phone number to call (e.g., '+1-415-555-0123')"
    )
    vendor_name: str = Field(
        description="Name of the vendor"
    )
    ingredient: str = Field(
        description="Ingredient being discussed"
    )
    quantity: str = Field(
        description="Quantity needed"
    )
    target_price: float = Field(
        description="Target price per unit to negotiate"
    )


class GetCallTranscriptInput(BaseModel):
    call_id: str = Field(
        description="Vapi call ID to retrieve"
    )


class ParseNegotiationInput(BaseModel):
    transcript: str = Field(
        description="Call transcript to analyze"
    )
    original_price: float = Field(
        description="Original price per unit before negotiation"
    )


# =====================
# Evaluation Agent Schemas
# =====================

class SaveDecisionInput(BaseModel):
    selected_vendors: list = Field(
        description="List of selected vendor objects"
    )
    total_cost: float = Field(
        description="Total cost of selected vendors"
    )
    budget: float = Field(
        description="Budget constraint"
    )
    justification: str = Field(
        description="Reasoning for vendor selection"
    )


# =====================
# Payment Agent Schemas
# =====================

class X402AuthorizeInput(BaseModel):
    invoice_id: str = Field(
        description="Invoice ID to authorize"
    )
    amount: float = Field(
        description="Amount in USD"
    )
    vendor: str = Field(
        description="Vendor name"
    )


class OpenBrowserInput(BaseModel):
    url: str = Field(
        description="URL to navigate to"
    )


class ClickElementInput(BaseModel):
    x: int = Field(description="X coordinate")
    y: int = Field(description="Y coordinate")


class TypeTextInput(BaseModel):
    text: str = Field(
        description="Text to type (non-sensitive fields only)"
    )


class InjectCredentialsInput(BaseModel):
    routing_selector: str = Field(
        description="CSS selector for routing number field"
    )
    account_selector: str = Field(
        description="CSS selector for account number field"
    )
    name_selector: str = Field(
        description="CSS selector for account name field"
    )
```

---

## Tool Implementations

### Sourcing Tools (Exa.ai)

```python
# src/haggl/tools/exa_tools.py
import os
import json
from exa_py import Exa
from anthropic import Anthropic

from nat.data_models.function import FunctionBaseConfig, register_function
from nat.data_models.function_info import FunctionInfo
from nat.builder import Builder

from ..schemas.inputs import SearchSuppliersInput, ExtractSupplierInfoInput


# =====================
# Configuration Classes
# =====================

class SearchSuppliersConfig(FunctionBaseConfig, name="search_suppliers"):
    """Search for wholesale suppliers using Exa.ai semantic search."""
    pass


class ExtractSupplierInfoConfig(FunctionBaseConfig, name="extract_supplier_info"):
    """Extract structured supplier info from raw text using Claude."""
    pass


# =====================
# Tool Implementations
# =====================

@register_function(config_type=SearchSuppliersConfig)
async def search_suppliers_tool(config: SearchSuppliersConfig, builder: Builder):
    """Register Exa.ai supplier search tool."""

    exa = Exa(os.getenv("EXA_API_KEY"))

    async def _search_suppliers(ingredient: str, location: str, quantity: str) -> str:
        """Search for wholesale suppliers using Exa.ai."""

        query = f"wholesale {ingredient} supplier {location} bulk pricing commercial"

        results = exa.search_and_contents(
            query,
            type="neural",
            num_results=10,
            text={"max_characters": 2000}
        )

        suppliers = []
        for result in results.results:
            suppliers.append({
                "url": result.url,
                "title": result.title,
                "text": result.text[:500] if result.text else ""
            })

        return json.dumps({
            "ingredient": ingredient,
            "location": location,
            "quantity": quantity,
            "suppliers_found": len(suppliers),
            "suppliers": suppliers
        }, indent=2)

    yield FunctionInfo.from_fn(
        _search_suppliers,
        input_schema=SearchSuppliersInput,
        description="Search for wholesale suppliers using Exa.ai semantic search"
    )


@register_function(config_type=ExtractSupplierInfoConfig)
async def extract_supplier_info_tool(config: ExtractSupplierInfoConfig, builder: Builder):
    """Register Claude-based supplier info extraction tool."""

    claude = Anthropic()

    async def _extract_supplier_info(text: str, ingredient: str) -> str:
        """Extract structured supplier data using Claude."""

        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""Extract supplier info from this text for {ingredient}:

{text}

Return ONLY valid JSON:
{{
  "vendor_name": "string",
  "phone": "string or null",
  "email": "string or null",
  "price_per_unit": number or null,
  "unit": "string (lb, unit, etc.)",
  "moq": number or null,
  "certifications": ["array of strings"]
}}"""
            }]
        )

        return response.content[0].text

    yield FunctionInfo.from_fn(
        _extract_supplier_info,
        input_schema=ExtractSupplierInfoInput,
        description="Extract structured supplier info from raw text using Claude"
    )
```

### Negotiation Tools (Vapi TTS)

```python
# src/haggl/tools/vapi_tools.py
import os
import json
import httpx
from anthropic import Anthropic

from nat.data_models.function import FunctionBaseConfig, register_function
from nat.data_models.function_info import FunctionInfo
from nat.builder import Builder

from ..schemas.inputs import MakePhoneCallInput, GetCallTranscriptInput, ParseNegotiationInput


VAPI_API_KEY = os.getenv("VAPI_API_KEY")


class MakePhoneCallConfig(FunctionBaseConfig, name="make_phone_call"):
    """Make outbound phone call via Vapi TTS for negotiation."""
    pass


class GetCallTranscriptConfig(FunctionBaseConfig, name="get_call_transcript"):
    """Get transcript from completed Vapi call."""
    pass


class ParseNegotiationConfig(FunctionBaseConfig, name="parse_negotiation"):
    """Parse negotiation outcome from call transcript."""
    pass


@register_function(config_type=MakePhoneCallConfig)
async def make_phone_call_tool(config: MakePhoneCallConfig, builder: Builder):
    """Register Vapi phone call tool."""

    async def _make_phone_call(
        phone_number: str,
        vendor_name: str,
        ingredient: str,
        quantity: str,
        target_price: float
    ) -> str:
        """Make Vapi phone call for negotiation."""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.vapi.ai/call",
                headers={"Authorization": f"Bearer {VAPI_API_KEY}"},
                json={
                    "assistant": {
                        "model": {
                            "provider": "anthropic",
                            "model": "claude-sonnet-4-20250514",
                            "systemPrompt": f"""You are calling {vendor_name} on behalf of Sweet Dreams Bakery.

Goals:
1. Confirm availability of {ingredient}
2. Get current pricing for {quantity}
3. Negotiate bulk discount (target: ${target_price}/unit)
4. Request invoice to orders@sweetdreamsbakery.com

Be professional and friendly. Aim for 10-20% discount."""
                        },
                        "voice": {
                            "provider": "11labs",
                            "voiceId": "21m00Tcm4TlvDq8ikWAM"
                        }
                    },
                    "customer": {"number": phone_number}
                },
                timeout=30.0
            )

            call_data = response.json()

            return json.dumps({
                "status": "call_initiated",
                "call_id": call_data.get("id"),
                "vendor": vendor_name,
                "ingredient": ingredient
            }, indent=2)

    yield FunctionInfo.from_fn(
        _make_phone_call,
        input_schema=MakePhoneCallInput,
        description="Make outbound phone call to vendor via Vapi TTS"
    )


@register_function(config_type=GetCallTranscriptConfig)
async def get_call_transcript_tool(config: GetCallTranscriptConfig, builder: Builder):
    """Register Vapi transcript retrieval tool."""

    async def _get_call_transcript(call_id: str) -> str:
        """Get call transcript from Vapi."""

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.vapi.ai/call/{call_id}",
                headers={"Authorization": f"Bearer {VAPI_API_KEY}"},
                timeout=30.0
            )

            call = response.json()

            return json.dumps({
                "call_id": call_id,
                "status": call.get("status"),
                "duration": call.get("duration"),
                "transcript": call.get("transcript", "No transcript available")
            }, indent=2)

    yield FunctionInfo.from_fn(
        _get_call_transcript,
        input_schema=GetCallTranscriptInput,
        description="Get transcript from completed Vapi call"
    )


@register_function(config_type=ParseNegotiationConfig)
async def parse_negotiation_tool(config: ParseNegotiationConfig, builder: Builder):
    """Register negotiation outcome parser."""

    claude = Anthropic()

    async def _parse_negotiation(transcript: str, original_price: float) -> str:
        """Parse negotiation outcome from transcript."""

        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": f"""Analyze this negotiation call transcript:

{transcript}

Original price: ${original_price}/unit

Return ONLY valid JSON:
{{
  "status": "success" | "partial" | "failed",
  "negotiated_price": number or null,
  "discount_pct": number,
  "terms": "string describing terms",
  "invoice_requested": boolean
}}"""
            }]
        )

        return response.content[0].text

    yield FunctionInfo.from_fn(
        _parse_negotiation,
        input_schema=ParseNegotiationInput,
        description="Parse negotiation outcome from call transcript"
    )
```

### MongoDB Tools

```python
# src/haggl/tools/mongo_tools.py
import os
import json
from pymongo import MongoClient

from nat.data_models.function import FunctionBaseConfig, register_function
from nat.data_models.function_info import FunctionInfo
from nat.builder import Builder

from ..schemas.inputs import SaveDecisionInput


# MongoDB connection
db = None


def get_db():
    global db
    if db is None:
        client = MongoClient(os.getenv("MONGODB_URI"))
        db = client["haggl"]
    return db


class GetAllSuppliersConfig(FunctionBaseConfig, name="get_all_suppliers"):
    """Retrieve all suppliers from MongoDB."""
    pass


class GetAllNegotiationsConfig(FunctionBaseConfig, name="get_all_negotiations"):
    """Retrieve all negotiation results from MongoDB."""
    pass


class SaveDecisionConfig(FunctionBaseConfig, name="save_decision"):
    """Save vendor selection decision to MongoDB."""
    pass


class GetPendingInvoicesConfig(FunctionBaseConfig, name="get_pending_invoices"):
    """Get pending invoices from MongoDB."""
    pass


@register_function(config_type=GetAllSuppliersConfig)
async def get_all_suppliers_tool(config: GetAllSuppliersConfig, builder: Builder):
    """Register supplier retrieval tool."""

    async def _get_all_suppliers() -> str:
        """Fetch all suppliers from MongoDB."""
        suppliers = list(get_db().suppliers.find({}, {"_id": 0}))
        return json.dumps({
            "count": len(suppliers),
            "suppliers": suppliers
        }, indent=2)

    yield FunctionInfo.from_fn(
        _get_all_suppliers,
        description="Retrieve all suppliers from MongoDB"
    )


@register_function(config_type=GetAllNegotiationsConfig)
async def get_all_negotiations_tool(config: GetAllNegotiationsConfig, builder: Builder):
    """Register negotiations retrieval tool."""

    async def _get_all_negotiations() -> str:
        """Fetch all negotiation results from MongoDB."""
        negotiations = list(get_db().negotiations.find({}, {"_id": 0}))
        return json.dumps({
            "count": len(negotiations),
            "negotiations": negotiations
        }, indent=2)

    yield FunctionInfo.from_fn(
        _get_all_negotiations,
        description="Retrieve all negotiation results from MongoDB"
    )


@register_function(config_type=SaveDecisionConfig)
async def save_decision_tool(config: SaveDecisionConfig, builder: Builder):
    """Register decision saving tool."""

    async def _save_decision(
        selected_vendors: list,
        total_cost: float,
        budget: float,
        justification: str
    ) -> str:
        """Save vendor selection decision to MongoDB."""

        decision = {
            "selected_vendors": selected_vendors,
            "total_cost": total_cost,
            "budget": budget,
            "savings": budget - total_cost,
            "justification": justification
        }

        result = get_db().decisions.insert_one(decision)

        return json.dumps({
            "status": "saved",
            "decision_id": str(result.inserted_id),
            "total_cost": total_cost,
            "budget": budget,
            "savings": budget - total_cost
        }, indent=2)

    yield FunctionInfo.from_fn(
        _save_decision,
        input_schema=SaveDecisionInput,
        description="Save vendor selection decision to MongoDB"
    )


@register_function(config_type=GetPendingInvoicesConfig)
async def get_pending_invoices_tool(config: GetPendingInvoicesConfig, builder: Builder):
    """Register pending invoices retrieval tool."""

    async def _get_pending_invoices() -> str:
        """Get pending invoices from MongoDB."""
        invoices = list(get_db().invoices.find({"status": "pending"}, {"_id": 0}))
        return json.dumps({
            "count": len(invoices),
            "invoices": invoices
        }, indent=2)

    yield FunctionInfo.from_fn(
        _get_pending_invoices,
        description="Get pending invoices from MongoDB"
    )
```

### Payment Tools (x402 + Browser)

```python
# src/haggl/tools/payment_tools.py
import os
import json
import base64
from cdp import Cdp, Wallet

from nat.data_models.function import FunctionBaseConfig, register_function
from nat.data_models.function_info import FunctionInfo
from nat.builder import Builder

from ..schemas.inputs import X402AuthorizeInput


Cdp.configure_from_json("cdp_api_key.json")
ESCROW_WALLET = os.getenv("ESCROW_WALLET_ADDRESS")


class CheckWalletBalanceConfig(FunctionBaseConfig, name="check_wallet_balance"):
    """Check CDP wallet USDC balance."""
    pass


class X402AuthorizeConfig(FunctionBaseConfig, name="x402_authorize"):
    """Authorize payment via x402 protocol (USDC to escrow)."""
    pass


@register_function(config_type=CheckWalletBalanceConfig)
async def check_wallet_balance_tool(config: CheckWalletBalanceConfig, builder: Builder):
    """Register wallet balance check tool."""

    async def _check_wallet_balance() -> str:
        """Check CDP wallet balance."""
        try:
            with open(".wallet_data", "r") as f:
                wallet = Wallet.import_data(f.read())
            balance = wallet.balances()
            return json.dumps({
                "status": "success",
                "balances": {k: str(v) for k, v in balance.items()}
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": str(e)
            }, indent=2)

    yield FunctionInfo.from_fn(
        _check_wallet_balance,
        description="Check CDP wallet USDC balance"
    )


@register_function(config_type=X402AuthorizeConfig)
async def x402_authorize_tool(config: X402AuthorizeConfig, builder: Builder):
    """Register x402 authorization tool."""

    async def _x402_authorize(invoice_id: str, amount: float, vendor: str) -> str:
        """Authorize payment via x402 (USDC transfer to escrow)."""
        try:
            with open(".wallet_data", "r") as f:
                wallet = Wallet.import_data(f.read())

            transfer = wallet.transfer(
                amount=amount,
                asset_id="usdc",
                destination=ESCROW_WALLET,
                memo=f"AUTH:{invoice_id}"
            )
            transfer.wait()

            return json.dumps({
                "status": "authorized",
                "invoice_id": invoice_id,
                "amount": amount,
                "vendor": vendor,
                "tx_hash": transfer.transaction_hash
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "status": "failed",
                "error": str(e)
            }, indent=2)

    yield FunctionInfo.from_fn(
        _x402_authorize,
        input_schema=X402AuthorizeInput,
        description="Authorize payment via x402 protocol (USDC to escrow)"
    )
```

### Browser Tools (Computer Use for ACH)

```python
# src/haggl/tools/browser_tools.py
import os
import json
import base64
from playwright.async_api import async_playwright

from nat.data_models.function import FunctionBaseConfig, register_function
from nat.data_models.function_info import FunctionInfo
from nat.builder import Builder

from ..schemas.inputs import OpenBrowserInput, ClickElementInput, TypeTextInput, InjectCredentialsInput


# Global browser state
_browser = None
_page = None


class OpenBrowserConfig(FunctionBaseConfig, name="open_browser"):
    """Open browser and navigate to URL."""
    pass


class TakeScreenshotConfig(FunctionBaseConfig, name="take_screenshot"):
    """Take screenshot of current page."""
    pass


class ClickElementConfig(FunctionBaseConfig, name="click_element"):
    """Click at specified coordinates."""
    pass


class TypeTextConfig(FunctionBaseConfig, name="type_text"):
    """Type text (for non-sensitive fields only)."""
    pass


class InjectCredentialsConfig(FunctionBaseConfig, name="inject_credentials"):
    """Securely inject ACH credentials (values hidden from AI)."""
    pass


class CloseBrowserConfig(FunctionBaseConfig, name="close_browser"):
    """Close the browser."""
    pass


@register_function(config_type=OpenBrowserConfig)
async def open_browser_tool(config: OpenBrowserConfig, builder: Builder):
    """Register browser opening tool."""

    async def _open_browser(url: str) -> str:
        """Open browser to URL."""
        global _browser, _page

        playwright = await async_playwright().start()
        _browser = await playwright.chromium.launch(headless=False)
        _page = await _browser.new_page()
        await _page.goto(url)

        return json.dumps({
            "status": "opened",
            "url": url
        }, indent=2)

    yield FunctionInfo.from_fn(
        _open_browser,
        input_schema=OpenBrowserInput,
        description="Open browser and navigate to URL"
    )


@register_function(config_type=TakeScreenshotConfig)
async def take_screenshot_tool(config: TakeScreenshotConfig, builder: Builder):
    """Register screenshot tool."""

    async def _take_screenshot() -> str:
        """Take screenshot of current page."""
        global _page

        if not _page:
            return json.dumps({"error": "No browser open"})

        screenshot = await _page.screenshot()
        b64 = base64.b64encode(screenshot).decode()

        # Return as base64 for Claude vision
        return json.dumps({
            "type": "screenshot",
            "format": "base64_png",
            "data": b64[:100] + "...",  # Truncated for display
            "full_data_available": True
        }, indent=2)

    yield FunctionInfo.from_fn(
        _take_screenshot,
        description="Take screenshot of current page for visual analysis"
    )


@register_function(config_type=ClickElementConfig)
async def click_element_tool(config: ClickElementConfig, builder: Builder):
    """Register click tool."""

    async def _click_element(x: int, y: int) -> str:
        """Click at coordinates."""
        global _page

        if not _page:
            return json.dumps({"error": "No browser open"})

        await _page.mouse.click(x, y)

        return json.dumps({
            "status": "clicked",
            "x": x,
            "y": y
        }, indent=2)

    yield FunctionInfo.from_fn(
        _click_element,
        input_schema=ClickElementInput,
        description="Click at specified coordinates"
    )


@register_function(config_type=TypeTextConfig)
async def type_text_tool(config: TypeTextConfig, builder: Builder):
    """Register text typing tool."""

    async def _type_text(text: str) -> str:
        """Type text (non-sensitive only)."""
        global _page

        if not _page:
            return json.dumps({"error": "No browser open"})

        await _page.keyboard.type(text)

        return json.dumps({
            "status": "typed",
            "text": text
        }, indent=2)

    yield FunctionInfo.from_fn(
        _type_text,
        input_schema=TypeTextInput,
        description="Type text (for non-sensitive fields only)"
    )


@register_function(config_type=InjectCredentialsConfig)
async def inject_credentials_tool(config: InjectCredentialsConfig, builder: Builder):
    """Register secure credential injection tool."""

    async def _inject_credentials(
        routing_selector: str,
        account_selector: str,
        name_selector: str
    ) -> str:
        """
        Inject ACH credentials securely.

        CRITICAL: AI provides CSS selectors only.
        Actual credential values are retrieved from secure vault.
        AI NEVER sees the credential values.
        """
        global _page

        if not _page:
            return json.dumps({"error": "No browser open"})

        # Get credentials from secure environment (NOT from AI)
        routing = os.getenv("ACH_ROUTING_NUMBER")
        account = os.getenv("ACH_ACCOUNT_NUMBER")
        name = os.getenv("ACH_ACCOUNT_NAME")

        if not all([routing, account, name]):
            return json.dumps({
                "status": "error",
                "message": "ACH credentials not configured"
            }, indent=2)

        # Inject credentials directly (values never exposed to AI)
        await _page.fill(routing_selector, routing)
        await _page.fill(account_selector, account)
        await _page.fill(name_selector, name)

        return json.dumps({
            "status": "credentials_injected",
            "fields_filled": 3,
            "note": "Credential values hidden from AI for security"
        }, indent=2)

    yield FunctionInfo.from_fn(
        _inject_credentials,
        input_schema=InjectCredentialsInput,
        description="Securely inject ACH credentials (AI provides selectors, values hidden)"
    )


@register_function(config_type=CloseBrowserConfig)
async def close_browser_tool(config: CloseBrowserConfig, builder: Builder):
    """Register browser closing tool."""

    async def _close_browser() -> str:
        """Close the browser."""
        global _browser, _page

        if _browser:
            await _browser.close()
            _browser = None
            _page = None

        return json.dumps({
            "status": "closed"
        }, indent=2)

    yield FunctionInfo.from_fn(
        _close_browser,
        description="Close the browser"
    )
```

### SMS Tools (Twilio)

```python
# src/haggl/tools/sms_tools.py
import os
import json
from twilio.rest import Client
from anthropic import Anthropic

from nat.data_models.function import FunctionBaseConfig, register_function
from nat.data_models.function_info import FunctionInfo
from nat.builder import Builder

from pydantic import BaseModel, Field


# =====================
# Schemas
# =====================

class ParseSMSInput(BaseModel):
    message: str = Field(description="SMS message to parse")
    phone: str = Field(description="Phone number of sender")


class SendSMSInput(BaseModel):
    to: str = Field(description="Recipient phone number")
    message: str = Field(description="Message to send")


class HandleApprovalInput(BaseModel):
    phone: str = Field(description="Phone number of approver")
    approved: bool = Field(description="Whether to approve or deny")


class GetOrderHistoryInput(BaseModel):
    phone: str = Field(description="Phone number to look up")
    ingredient: str = Field(description="Ingredient to find", default=None)


# =====================
# Tool Implementations
# =====================

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE_NUMBER")


class ParseSMSConfig(FunctionBaseConfig, name="parse_sms"):
    """Parse SMS message intent using Claude."""
    pass


class SendSMSConfig(FunctionBaseConfig, name="send_sms"):
    """Send SMS via Twilio."""
    pass


class HandleApprovalConfig(FunctionBaseConfig, name="handle_approval"):
    """Handle SMS approval/denial of pending purchase."""
    pass


class GetOrderHistoryConfig(FunctionBaseConfig, name="get_order_history"):
    """Get order history for reordering."""
    pass


@register_function(config_type=ParseSMSConfig)
async def parse_sms_tool(config: ParseSMSConfig, builder: Builder):
    """Register SMS parsing tool."""

    claude = Anthropic()

    async def _parse_sms(message: str, phone: str) -> str:
        """Parse SMS intent using Claude."""

        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": f"""Parse this SMS from a business owner ordering supplies.

MESSAGE: {message}

Return JSON:
{{
  "type": "reorder" | "new_order" | "approve" | "deny" | "status" | "help",
  "ingredient": "string or null",
  "items": [{{"name": "string", "quantity": "string"}}] or null,
  "confidence": 0-1
}}

JSON:"""
            }]
        )

        return response.content[0].text

    yield FunctionInfo.from_fn(
        _parse_sms,
        input_schema=ParseSMSInput,
        description="Parse SMS message intent using Claude NLU"
    )


@register_function(config_type=SendSMSConfig)
async def send_sms_tool(config: SendSMSConfig, builder: Builder):
    """Register SMS sending tool."""

    twilio = Client(TWILIO_SID, TWILIO_AUTH)

    async def _send_sms(to: str, message: str) -> str:
        """Send SMS via Twilio."""

        msg = twilio.messages.create(
            body=message,
            from_=TWILIO_PHONE,
            to=to
        )

        return json.dumps({
            "status": "sent",
            "sid": msg.sid,
            "to": to
        }, indent=2)

    yield FunctionInfo.from_fn(
        _send_sms,
        input_schema=SendSMSInput,
        description="Send SMS message via Twilio"
    )


@register_function(config_type=HandleApprovalConfig)
async def handle_approval_tool(config: HandleApprovalConfig, builder: Builder):
    """Register approval handling tool."""

    from pymongo import MongoClient
    db = MongoClient(os.getenv("MONGODB_URI"))["haggl"]

    async def _handle_approval(phone: str, approved: bool) -> str:
        """Handle SMS approval/denial."""

        pending = db.pending_approvals.find_one_and_delete({"phone": phone})

        if not pending:
            return json.dumps({
                "status": "no_pending",
                "message": "No pending approval found"
            })

        if approved:
            # Move to processing queue
            db.orders.insert_one({
                **pending["order"],
                "status": "approved",
                "approved_at": datetime.now()
            })

            return json.dumps({
                "status": "approved",
                "order": pending["order"]
            })
        else:
            return json.dumps({
                "status": "denied",
                "message": "Order cancelled"
            })

    yield FunctionInfo.from_fn(
        _handle_approval,
        input_schema=HandleApprovalInput,
        description="Handle SMS approval or denial of pending purchase"
    )


@register_function(config_type=GetOrderHistoryConfig)
async def get_order_history_tool(config: GetOrderHistoryConfig, builder: Builder):
    """Register order history lookup tool."""

    from pymongo import MongoClient
    db = MongoClient(os.getenv("MONGODB_URI"))["haggl"]

    async def _get_order_history(phone: str, ingredient: str = None) -> str:
        """Get order history for reordering."""

        query = {"phone": phone}
        if ingredient:
            query["ingredient"] = {"$regex": ingredient, "$options": "i"}

        orders = list(db.order_history.find(
            query,
            sort=[("timestamp", -1)],
            limit=5
        ))

        # Convert ObjectId to string
        for order in orders:
            order["_id"] = str(order["_id"])

        return json.dumps({
            "count": len(orders),
            "orders": orders
        }, indent=2)

    yield FunctionInfo.from_fn(
        _get_order_history,
        input_schema=GetOrderHistoryInput,
        description="Get order history for a phone number, optionally filtered by ingredient"
    )
```

### CSV Tools

```python
# src/haggl/tools/csv_tools.py
import csv
import re
from io import StringIO
from typing import List, Dict

from nat.data_models.function import FunctionBaseConfig, register_function
from nat.data_models.function_info import FunctionInfo
from nat.builder import Builder

from pydantic import BaseModel, Field


class ParseCSVInput(BaseModel):
    csv_content: str = Field(description="CSV content as string")


class ParseCSVConfig(FunctionBaseConfig, name="parse_csv"):
    """Parse CSV content into structured ingredient list."""
    pass


@register_function(config_type=ParseCSVConfig)
async def parse_csv_tool(config: ParseCSVConfig, builder: Builder):
    """Register CSV parsing tool."""

    COLUMN_ALIASES = {
        "item": "ingredient",
        "product": "ingredient",
        "name": "ingredient",
        "qty": "quantity",
        "amount": "quantity",
        "grade": "quality",
        "type": "quality"
    }

    def _normalize_column(col: str) -> str:
        col_lower = col.lower().strip()
        return COLUMN_ALIASES.get(col_lower, col_lower)

    def _parse_quantity(qty_str: str) -> tuple:
        match = re.match(r'(\d+(?:\.\d+)?)\s*(\w+)?', str(qty_str).strip())
        if match:
            return float(match.group(1)), match.group(2) or "units"
        return 1, "units"

    async def _parse_csv(csv_content: str) -> str:
        """Parse CSV into ingredient list."""

        try:
            dialect = csv.Sniffer().sniff(csv_content[:1024])
        except csv.Error:
            dialect = csv.excel

        reader = csv.DictReader(StringIO(csv_content), dialect=dialect)

        if reader.fieldnames:
            reader.fieldnames = [_normalize_column(c) for c in reader.fieldnames]

        ingredients = []
        for row in reader:
            if not row.get("ingredient"):
                continue

            quantity, unit = _parse_quantity(row.get("quantity", "1"))

            ingredients.append({
                "name": row["ingredient"].strip(),
                "quantity": f"{quantity} {unit}",
                "quality": row.get("quality", "standard").strip() if row.get("quality") else "standard",
                "priority": row.get("priority", "medium").strip() if row.get("priority") else "medium"
            })

        return json.dumps({
            "status": "success",
            "count": len(ingredients),
            "ingredients": ingredients
        }, indent=2)

    yield FunctionInfo.from_fn(
        _parse_csv,
        input_schema=ParseCSVInput,
        description="Parse CSV content into structured ingredient list"
    )
```

---

## Tool Registration

```python
# src/haggl/register.py
"""
Register all Haggl tools with NeMo Agent Toolkit.
"""

# Import all tool modules to trigger registration
from .tools import exa_tools
from .tools import vapi_tools
from .tools import mongo_tools
from .tools import payment_tools
from .tools import browser_tools
from .tools import sms_tools
from .tools import csv_tools
```

---

## Agent Configurations (YAML)

### Agent 1: Sourcing Agent

```yaml
# configs/sourcing.yml
functions:
  search_suppliers:
    _type: haggl/search_suppliers
  extract_supplier_info:
    _type: haggl/extract_supplier_info

llms:
  sourcing_llm:
    _type: litellm
    model_name: anthropic/claude-sonnet-4-20250514
    api_key: $ANTHROPIC_API_KEY
    temperature: 0.3

workflow:
  _type: react_agent
  llm_name: sourcing_llm
  tool_names: [search_suppliers, extract_supplier_info]
  verbose: true
  max_iterations: 10
  system_prompt: |
    You are a B2B procurement sourcing specialist.

    Your task is to find wholesale suppliers for ingredients.

    For each ingredient:
    1. Use search_suppliers to find potential vendors
    2. Use extract_supplier_info to get structured data from results
    3. Return a comprehensive list of suppliers with pricing

    Focus on:
    - Commercial/wholesale suppliers (not retail)
    - Suppliers that ship to the target location
    - Competitive pricing and quality certifications
    - Extracting phone numbers and emails for follow-up
```

### Agent 2: Negotiation Agent

```yaml
# configs/negotiation.yml
functions:
  make_phone_call:
    _type: haggl/make_phone_call
  get_call_transcript:
    _type: haggl/get_call_transcript
  parse_negotiation:
    _type: haggl/parse_negotiation

llms:
  negotiation_llm:
    _type: litellm
    model_name: anthropic/claude-sonnet-4-20250514
    api_key: $ANTHROPIC_API_KEY
    temperature: 0.5

workflow:
  _type: react_agent
  llm_name: negotiation_llm
  tool_names: [make_phone_call, get_call_transcript, parse_negotiation]
  verbose: true
  max_iterations: 15
  system_prompt: |
    You are a professional B2B procurement negotiator.

    Your task is to negotiate prices with suppliers via phone calls.

    Negotiation strategies:
    - "We're ordering {quantity}, what's your bulk pricing?"
    - "Another supplier quoted ${price}, can you match?"
    - "If we commit to monthly orders, what discount?"

    Process:
    1. Make phone call with negotiation goals
    2. Wait for call completion, then get transcript
    3. Parse negotiation outcome from transcript
    4. Report results including discount achieved

    Always:
    - Be professional and friendly
    - Aim for 10-20% discount
    - Request invoice to orders@sweetdreamsbakery.com
```

### Agent 3: Evaluation Agent

```yaml
# configs/evaluation.yml
functions:
  get_all_suppliers:
    _type: haggl/get_all_suppliers
  get_all_negotiations:
    _type: haggl/get_all_negotiations
  save_decision:
    _type: haggl/save_decision

llms:
  evaluation_llm:
    _type: litellm
    model_name: anthropic/claude-sonnet-4-20250514
    api_key: $ANTHROPIC_API_KEY
    temperature: 0.2

workflow:
  _type: react_agent
  llm_name: evaluation_llm
  tool_names: [get_all_suppliers, get_all_negotiations, save_decision]
  verbose: true
  max_iterations: 10
  system_prompt: |
    You are a procurement evaluation specialist.

    Your task is to select the best suppliers within budget.

    Scoring factors:
    - Price: 35% weight (lower is better)
    - Quality: 30% weight (certifications, reviews)
    - Negotiation Success: 20% weight (discount achieved)
    - Reliability: 15% weight (based on available data)

    Process:
    1. Get all suppliers from database
    2. Get all negotiation results
    3. Score each supplier on multi-factor criteria
    4. Select best combination within budget constraint
    5. Save decision with detailed justification

    CRITICAL: Total cost must NOT exceed budget.
```

### Agent 4: Payment Agent

```yaml
# configs/payment.yml
functions:
  check_wallet_balance:
    _type: haggl/check_wallet_balance
  x402_authorize:
    _type: haggl/x402_authorize
  get_pending_invoices:
    _type: haggl/get_pending_invoices
  open_browser:
    _type: haggl/open_browser
  take_screenshot:
    _type: haggl/take_screenshot
  click_element:
    _type: haggl/click_element
  type_text:
    _type: haggl/type_text
  inject_credentials:
    _type: haggl/inject_credentials
  close_browser:
    _type: haggl/close_browser

llms:
  payment_llm:
    _type: litellm
    model_name: anthropic/claude-sonnet-4-20250514
    api_key: $ANTHROPIC_API_KEY
    temperature: 0.1

workflow:
  _type: react_agent
  llm_name: payment_llm
  tool_names:
    - check_wallet_balance
    - x402_authorize
    - get_pending_invoices
    - open_browser
    - take_screenshot
    - click_element
    - type_text
    - inject_credentials
    - close_browser
  verbose: true
  max_iterations: 25
  system_prompt: |
    You are a secure payment execution agent.

    Your task is to process invoice payments using x402 + ACH.

    CRITICAL SECURITY RULES:
    - You do NOT have access to ACH credential values
    - Use inject_credentials tool to fill ACH form fields securely
    - Identify CSS selectors for form fields, then call inject_credentials
    - NEVER attempt to type credentials directly

    Payment flow:
    1. Check wallet balance first
    2. Get pending invoices from database
    3. For each invoice with a payment_url:
       a. Authorize via x402 (USDC to escrow)
       b. Open browser to payment URL
       c. Take screenshot to analyze form
       d. Identify ACH form field selectors
       e. Call inject_credentials with selectors
       f. Click submit/pay button
       g. Take confirmation screenshot
    4. Close browser when complete

    Report results for each payment.
```

---

## Multi-Agent Orchestrator

```yaml
# configs/orchestrator.yml
functions:
  # Import all agent tools
  search_suppliers:
    _type: haggl/search_suppliers
  extract_supplier_info:
    _type: haggl/extract_supplier_info
  make_phone_call:
    _type: haggl/make_phone_call
  get_call_transcript:
    _type: haggl/get_call_transcript
  parse_negotiation:
    _type: haggl/parse_negotiation
  get_all_suppliers:
    _type: haggl/get_all_suppliers
  get_all_negotiations:
    _type: haggl/get_all_negotiations
  save_decision:
    _type: haggl/save_decision
  check_wallet_balance:
    _type: haggl/check_wallet_balance
  x402_authorize:
    _type: haggl/x402_authorize
  get_pending_invoices:
    _type: haggl/get_pending_invoices
  open_browser:
    _type: haggl/open_browser
  take_screenshot:
    _type: haggl/take_screenshot
  click_element:
    _type: haggl/click_element
  inject_credentials:
    _type: haggl/inject_credentials
  close_browser:
    _type: haggl/close_browser

llms:
  orchestrator_llm:
    _type: litellm
    model_name: anthropic/claude-sonnet-4-20250514
    api_key: $ANTHROPIC_API_KEY
    temperature: 0.3

workflow:
  _type: react_agent
  llm_name: orchestrator_llm
  tool_names:
    - search_suppliers
    - extract_supplier_info
    - make_phone_call
    - get_call_transcript
    - parse_negotiation
    - get_all_suppliers
    - get_all_negotiations
    - save_decision
    - check_wallet_balance
    - x402_authorize
    - get_pending_invoices
    - open_browser
    - take_screenshot
    - click_element
    - inject_credentials
    - close_browser
  verbose: true
  max_iterations: 50
  system_prompt: |
    You are the Haggl Orchestrator.

    You coordinate a complete B2B procurement workflow with 4 phases:

    PHASE 1: SOURCING
    - Search for suppliers for each ingredient
    - Extract structured data from results
    - Build supplier database

    PHASE 2: NEGOTIATION
    - Make concurrent phone calls to top suppliers
    - Negotiate bulk discounts (target 10-20%)
    - Parse negotiation outcomes

    PHASE 3: EVALUATION
    - Score all suppliers on price, quality, negotiation success
    - Select optimal combination within budget
    - Save decision with justification

    PHASE 4: PAYMENT
    - Check wallet balance
    - Authorize via x402
    - Execute ACH payments via browser
    - Verify confirmations

    Execute phases in order. Report progress after each phase.
```

---

## Main Entry Point

```python
# main.py
import os
import asyncio
import argparse

# Ensure tools are registered
import src.haggl.register


async def run_orchestrator(ingredients: list, location: str, budget: float):
    """Run the full Haggl orchestration workflow."""
    import subprocess

    # Build input prompt
    ingredient_list = "\n".join([
        f"- {ing['name']}: {ing['quantity']}"
        for ing in ingredients
    ])

    prompt = f"""Execute complete procurement workflow:

INGREDIENTS NEEDED:
{ingredient_list}

LOCATION: {location}
BUDGET: ${budget}

Execute all 4 phases:
1. Source suppliers for each ingredient
2. Negotiate with top suppliers (aim for 10-20% discount)
3. Evaluate and select best combination within budget
4. Process payments via x402 + ACH

Report progress and final results."""

    # Run NAT orchestrator
    result = subprocess.run(
        [
            "nat", "run",
            "--config_file", "configs/orchestrator.yml",
            "--input", prompt
        ],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print("ERRORS:", result.stderr)

    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Haggl Procurement System")
    parser.add_argument("--ingredients", nargs="+", required=True,
                        help="Ingredient names")
    parser.add_argument("--quantities", nargs="+", required=True,
                        help="Quantities for each ingredient")
    parser.add_argument("--budget", type=float, required=True,
                        help="Budget in USD")
    parser.add_argument("--location", default="San Francisco, CA",
                        help="Delivery location")

    args = parser.parse_args()

    if len(args.ingredients) != len(args.quantities):
        print("ERROR: Number of ingredients must match number of quantities")
        return

    ingredients = [
        {"name": ing, "quantity": qty}
        for ing, qty in zip(args.ingredients, args.quantities)
    ]

    print("=" * 60)
    print("INGREDIENTAI - Autonomous B2B Procurement")
    print("=" * 60)
    print(f"Ingredients: {', '.join(args.ingredients)}")
    print(f"Location: {args.location}")
    print(f"Budget: ${args.budget}")
    print("=" * 60)
    print()

    asyncio.run(run_orchestrator(ingredients, args.location, args.budget))


if __name__ == "__main__":
    main()
```

---

## Running the System

### Environment Setup

```bash
# Set required environment variables
export ANTHROPIC_API_KEY=sk-ant-...
export MONGODB_URI=mongodb+srv://...
export EXA_API_KEY=...
export VAPI_API_KEY=...
export ESCROW_WALLET_ADDRESS=0x...

# ACH credentials (securely stored, never exposed to AI)
export ACH_ROUTING_NUMBER=...
export ACH_ACCOUNT_NUMBER=...
export ACH_ACCOUNT_NAME=...
```

### Install Local Package

```bash
cd ingredient-ai
pip install -e .
```

### Run Individual Agents

```bash
# Run sourcing agent only
nat run --config_file configs/sourcing.yml \
  --input "Find suppliers for all-purpose flour, 500 lbs, San Francisco CA"

# Run negotiation agent only
nat run --config_file configs/negotiation.yml \
  --input "Negotiate with Bay Area Foods Co for flour"

# Run evaluation agent only
nat run --config_file configs/evaluation.yml \
  --input "Evaluate suppliers and select best within $2000 budget"

# Run payment agent only
nat run --config_file configs/payment.yml \
  --input "Process pending invoices via ACH"
```

### Run Full Orchestration

```bash
# Run complete workflow
python main.py \
  --ingredients "flour" "eggs" "butter" \
  --quantities "500 lbs" "1000 units" "100 lbs" \
  --budget 2000 \
  --location "San Francisco, CA"
```

### Serve as REST API

```bash
# Start API server
nat serve --config_file configs/orchestrator.yml --port 8000

# Make request
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{
      "role": "user",
      "content": "Source and order flour, eggs, butter for $2000"
    }],
    "stream": false
  }'
```

---

## Profiling & Observability

### Enable Profiling

```bash
# Run with profiling
nat run --config_file configs/orchestrator.yml \
  --input "Your query" \
  --profile

# View profiling results
nat profile view
```

### Phoenix Integration

```yaml
# Add to any config file
observability:
  _type: phoenix
  endpoint: http://localhost:6006
```

### Weave Integration

```yaml
observability:
  _type: weave
  project_name: ingredient-ai
```

---

## Production Deployment

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  ingredient-ai:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - MONGODB_URI=${MONGODB_URI}
      - EXA_API_KEY=${EXA_API_KEY}
      - VAPI_API_KEY=${VAPI_API_KEY}
      - ESCROW_WALLET_ADDRESS=${ESCROW_WALLET_ADDRESS}
      - ACH_ROUTING_NUMBER=${ACH_ROUTING_NUMBER}
      - ACH_ACCOUNT_NUMBER=${ACH_ACCOUNT_NUMBER}
      - ACH_ACCOUNT_NAME=${ACH_ACCOUNT_NAME}
    command: nat serve --config_file configs/orchestrator.yml --port 8000

  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  phoenix:
    image: arizephoenix/phoenix
    ports:
      - "6006:6006"

volumes:
  mongo_data:
```

---

## References

- [NVIDIA NeMo Agent Toolkit GitHub](https://github.com/NVIDIA/NeMo-Agent-Toolkit)
- [NVIDIA NeMo Agent Toolkit Documentation](https://docs.nvidia.com/nemo/agent-toolkit/latest/)
- [DeepLearning.AI Course: Making Agents Reliable](https://www.deeplearning.ai/short-courses/nvidia-nat-making-agents-reliable/)
- [NeMo Guardrails](https://developer.nvidia.com/nemo-guardrails)
- [x402 Protocol](https://x402.org/)

---

**Document Status:** Ready for Implementation
**Framework:** NVIDIA NeMo Agent Toolkit v1.4+
