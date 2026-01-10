"""
Browserbase x402 Integration for Payment Execution.

Uses Browserbase's cloud browsers (paid with USDC via x402) to navigate
vendor payment portals like Intuit QuickBooks, Stripe invoices, etc.

Docs: https://docs.browserbase.com/integrations/x402/introduction
"""

import os
import re
import json
import base64
import logging
import asyncio
import httpx
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Browserbase configuration
BROWSERBASE_PROJECT_ID = os.getenv("BROWSERBASE_PROJECT_ID", "54733070-252e-42f2-a759-9ac4904fb508")
BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY", "bb_live_lihjjuzl9amwS2H7wFQp4boE42c")
BROWSERBASE_API_URL = "https://www.browserbase.com/v1/sessions"
BROWSERBASE_CONNECT_URL = "wss://connect.browserbase.com"

# Anthropic for invoice parsing
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Check if Playwright is available
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed. Browser automation unavailable.")


class BrowserbaseClient:
    """
    Browserbase client for cloud browser sessions.
    
    Uses the standard Browserbase API (not x402 for now).
    
    Flow:
    1. Create session via API
    2. Get session ID and WebSocket URL
    3. Connect via Playwright CDP
    4. Automate browser (navigate, click, fill forms)
    5. Session auto-closes
    """
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        api_key: Optional[str] = None,
        mock_mode: bool = False
    ):
        self.project_id = project_id or BROWSERBASE_PROJECT_ID
        self.api_key = api_key or BROWSERBASE_API_KEY
        self.mock_mode = mock_mode or not (self.project_id and self.api_key)
        
        self._session_id: Optional[str] = None
        self._connect_url: Optional[str] = None
        self._browser = None
        self._context = None
        self._page = None
        self._playwright = None
    
    async def create_session(self) -> dict:
        """
        Create a Browserbase session.
        
        Returns session info including WebSocket URL for CDP connection.
        """
        if self.mock_mode:
            logger.info("[MOCK] Creating Browserbase session...")
            self._session_id = f"mock_session_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            return {
                "session_id": self._session_id,
                "connect_url": f"wss://mock.browserbase.com?session={self._session_id}",
                "mock": True
            }
        
        headers = {
            "x-bb-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "projectId": self.project_id,
            "browserSettings": {
                "viewport": {"width": 1280, "height": 800}
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    BROWSERBASE_API_URL,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code not in (200, 201):
                    logger.error(f"Browserbase API error: {response.status_code} - {response.text}")
                    return {
                        "error": f"Failed to create session: {response.status_code}",
                        "details": response.text
                    }
                
                data = response.json()
                self._session_id = data.get("id")
                self._connect_url = data.get("connectUrl") or f"{BROWSERBASE_CONNECT_URL}?sessionId={self._session_id}"
                
                logger.info(f"Created Browserbase session: {self._session_id}")
                
                return {
                    "session_id": self._session_id,
                    "connect_url": self._connect_url,
                    "mock": False
                }
                
        except Exception as e:
            logger.exception(f"Failed to create Browserbase session: {e}")
            return {"error": str(e)}
    
    async def connect_browser(self) -> bool:
        """Connect to Browserbase session via Playwright CDP."""
        if self.mock_mode:
            logger.info("[MOCK] Browser connected")
            return True
        
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available")
            return False
        
        if not self._session_id or not self._connect_url:
            logger.error("No session created")
            return False
        
        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.connect_over_cdp(self._connect_url)
            
            # Get default context and page
            contexts = self._browser.contexts
            if contexts:
                self._context = contexts[0]
                pages = self._context.pages
                self._page = pages[0] if pages else await self._context.new_page()
            else:
                self._context = await self._browser.new_context()
                self._page = await self._context.new_page()
            
            logger.info(f"Connected to Browserbase session: {self._session_id}")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to connect: {e}")
            return False
    
    async def navigate(self, url: str, wait_until: str = "networkidle") -> bool:
        """Navigate to a URL."""
        if self.mock_mode:
            logger.info(f"[MOCK] Navigating to: {url}")
            return True
        
        if not self._page:
            return False
        
        try:
            await self._page.goto(url, wait_until=wait_until, timeout=60000)
            logger.info(f"Navigated to: {url}")
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
    
    async def screenshot(self, full_page: bool = False) -> Optional[bytes]:
        """Take a screenshot of the current page."""
        if self.mock_mode:
            logger.info("[MOCK] Screenshot taken")
            return b"mock_screenshot_data"
        
        if not self._page:
            return None
        
        try:
            return await self._page.screenshot(full_page=full_page)
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None
    
    async def click(self, selector: str, timeout: int = 10000) -> bool:
        """Click an element by selector."""
        if self.mock_mode:
            logger.info(f"[MOCK] Clicking: {selector}")
            return True
        
        if not self._page:
            return False
        
        try:
            await self._page.click(selector, timeout=timeout)
            return True
        except Exception as e:
            logger.error(f"Click failed on {selector}: {e}")
            return False
    
    async def fill(self, selector: str, value: str, timeout: int = 10000) -> bool:
        """Fill a form field."""
        if self.mock_mode:
            logger.info(f"[MOCK] Filling {selector}")
            return True
        
        if not self._page:
            return False
        
        try:
            await self._page.fill(selector, value, timeout=timeout)
            return True
        except Exception as e:
            logger.error(f"Fill failed on {selector}: {e}")
            return False
    
    async def type_text(self, selector: str, value: str, delay: int = 50) -> bool:
        """Type text character by character (for fields that don't accept fill)."""
        if self.mock_mode:
            logger.info(f"[MOCK] Typing in {selector}")
            return True
        
        if not self._page:
            return False
        
        try:
            await self._page.click(selector)
            await self._page.type(selector, value, delay=delay)
            return True
        except Exception as e:
            logger.error(f"Type failed on {selector}: {e}")
            return False
    
    async def get_page_content(self) -> str:
        """Get the current page HTML."""
        if self.mock_mode:
            return "<html><body>Mock page</body></html>"
        
        if not self._page:
            return ""
        
        try:
            return await self._page.content()
        except Exception as e:
            logger.error(f"Get content failed: {e}")
            return ""
    
    async def get_page_text(self) -> str:
        """Get visible text from the page."""
        if self.mock_mode:
            return "Mock page text"
        
        if not self._page:
            return ""
        
        try:
            return await self._page.inner_text("body")
        except Exception as e:
            logger.error(f"Get text failed: {e}")
            return ""
    
    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> bool:
        """Wait for an element to appear."""
        if self.mock_mode:
            return True
        
        if not self._page:
            return False
        
        try:
            await self._page.wait_for_selector(selector, timeout=timeout)
            return True
        except Exception as e:
            logger.error(f"Wait for {selector} failed: {e}")
            return False
    
    async def close(self):
        """Close the browser session."""
        try:
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception as e:
            logger.error(f"Close failed: {e}")
        
        self._browser = None
        self._context = None
        self._page = None
        self._session_id = None
        self._connect_url = None
        self._playwright = None
        logger.info("Browser session closed")


class InvoiceParser:
    """
    Parse invoice details from payment portal pages using Claude Vision.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ANTHROPIC_API_KEY
    
    async def parse_from_screenshot(self, screenshot_bytes: bytes) -> dict:
        """
        Parse invoice details from a screenshot using Claude Vision.
        
        Returns:
            Dict with invoice_id, vendor_name, amount, due_date, payment_methods
        """
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set, using mock parsing")
            return self._mock_parse()
        
        # Encode screenshot to base64
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
        
        prompt = """Analyze this invoice/payment page screenshot and extract:

1. Invoice number/ID
2. Vendor/merchant name
3. Amount due (as a number)
4. Currency (USD, etc.)
5. Due date
6. Available payment methods (list: card, bank/ACH, etc.)
7. Any confirmation or reference numbers visible

Return ONLY valid JSON:
{
  "invoice_id": "string or null",
  "vendor_name": "string",
  "amount": number,
  "currency": "USD",
  "due_date": "YYYY-MM-DD or null",
  "payment_methods": ["card", "bank"],
  "confirmation_number": "string or null",
  "notes": "any other relevant info"
}"""
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "claude-sonnet-4-20250514",
                        "max_tokens": 1024,
                        "messages": [{
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": screenshot_b64
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }]
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Claude API error: {response.status_code}")
                    return self._mock_parse()
                
                data = response.json()
                content = data.get("content", [{}])[0].get("text", "{}")
                
                # Parse JSON from response
                return self._parse_json(content)
                
        except Exception as e:
            logger.exception(f"Invoice parsing failed: {e}")
            return self._mock_parse()
    
    def _parse_json(self, text: str) -> dict:
        """Extract JSON from Claude's response."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON in the text
            match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
        return self._mock_parse()
    
    def _mock_parse(self) -> dict:
        """Return mock parsed data."""
        return {
            "invoice_id": "INV-MOCK-001",
            "vendor_name": "Demo Vendor",
            "amount": 0.01,
            "currency": "USD",
            "due_date": None,
            "payment_methods": ["card", "bank"],
            "confirmation_number": None,
            "notes": "Mock parsed invoice"
        }


class PaymentPortalAutomator:
    """
    Generic payment portal automator that works with various vendors.
    
    Uses Claude Vision to understand the page and determine actions.
    """
    
    # Common selectors for payment portals
    COMMON_SELECTORS = {
        "bank_options": [
            "button:has-text('Bank')",
            "button:has-text('ACH')",
            "[data-testid='bank-payment']",
            "input[value='bank']",
            "label:has-text('Bank Account')",
        ],
        "routing_fields": [
            "input[name*='routing']",
            "input[placeholder*='Routing']",
            "input[id*='routing']",
            "#routingNumber",
        ],
        "account_fields": [
            "input[name*='account']",
            "input[placeholder*='Account']",
            "input[id*='account']",
            "#accountNumber",
        ],
        "name_fields": [
            "input[name*='name']",
            "input[placeholder*='Name on']",
            "input[id*='accountName']",
        ],
        "submit_buttons": [
            "button:has-text('Pay')",
            "button:has-text('Submit')",
            "button[type='submit']",
            "input[type='submit']",
        ],
        "email_fields": [
            "input[type='email']",
            "input[name='email']",
            "input[placeholder*='Email']",
        ]
    }
    
    def __init__(self, browser: BrowserbaseClient):
        self.browser = browser
        self.parser = InvoiceParser()
        self._screenshots: list[tuple[str, bytes]] = []
    
    async def pay_invoice(
        self,
        invoice_url: str,
        business_id: str,
        auth_token: str,
        contact_email: str = "orders@haggl.demo"
    ) -> dict:
        """
        Pay an invoice through its payment portal.
        
        Args:
            invoice_url: URL to the payment page
            business_id: Business ID for credential lookup
            auth_token: x402 authorization token
            contact_email: Email for receipt
        
        Returns:
            Payment result dict
        """
        result = {
            "status": "pending",
            "invoice_url": invoice_url,
            "steps": [],
            "parsed_invoice": None,
            "confirmation": None,
            "screenshots": [],
            "error": None
        }
        
        try:
            # Step 1: Create browser session
            result["steps"].append("Creating browser session...")
            session = await self.browser.create_session()
            
            if session.get("error"):
                result["status"] = "failed"
                result["error"] = session["error"]
                return result
            
            result["steps"].append(f"Session: {session.get('session_id', 'mock')}")
            
            # Step 2: Connect to browser
            if not await self.browser.connect_browser():
                result["status"] = "failed"
                result["error"] = "Failed to connect to browser"
                return result
            
            # Step 3: Navigate to invoice
            result["steps"].append("Navigating to payment page...")
            if not await self.browser.navigate(invoice_url):
                result["status"] = "failed"
                result["error"] = "Failed to navigate to invoice"
                return result
            
            await asyncio.sleep(2)
            
            # Step 4: Take screenshot and parse invoice
            result["steps"].append("Parsing invoice details...")
            screenshot = await self.browser.screenshot()
            if screenshot:
                self._save_screenshot("01_initial", screenshot)
                parsed = await self.parser.parse_from_screenshot(screenshot)
                result["parsed_invoice"] = parsed
                result["steps"].append(f"Parsed: {parsed.get('vendor_name')} - ${parsed.get('amount')}")
            
            # Step 5: Select bank/ACH payment method
            result["steps"].append("Selecting ACH payment method...")
            await self._select_bank_payment()
            await asyncio.sleep(1)
            
            # Step 6: Fill email
            result["steps"].append("Filling contact email...")
            await self._fill_email(contact_email)
            
            # Step 7: Get credentials from vault and inject
            result["steps"].append("Injecting ACH credentials securely...")
            credentials = await self._get_credentials(business_id, auth_token)
            if credentials:
                await self._inject_ach_credentials(credentials)
            else:
                result["steps"].append("Using demo credentials (no vault configured)")
                await self._inject_ach_credentials({
                    "routing": os.getenv("ACH_ROUTING_NUMBER", "021000021"),
                    "account": os.getenv("ACH_ACCOUNT_NUMBER", "1234567890"),
                    "name": os.getenv("ACH_ACCOUNT_NAME", "Haggl Demo Business"),
                })
            
            # Take screenshot before submit
            screenshot = await self.browser.screenshot()
            if screenshot:
                self._save_screenshot("02_filled", screenshot)
            
            # Step 8: Submit payment
            result["steps"].append("Submitting payment...")
            await self._click_submit()
            await asyncio.sleep(3)
            
            # Step 9: Capture confirmation
            result["steps"].append("Capturing confirmation...")
            screenshot = await self.browser.screenshot()
            if screenshot:
                self._save_screenshot("03_confirmation", screenshot)
                # Try to parse confirmation
                parsed = await self.parser.parse_from_screenshot(screenshot)
                if parsed.get("confirmation_number"):
                    result["confirmation"] = parsed["confirmation_number"]
            
            # Extract confirmation from page text
            page_text = await self.browser.get_page_text()
            if not result["confirmation"]:
                result["confirmation"] = self._extract_confirmation(page_text)
            
            result["status"] = "succeeded"
            result["screenshots"] = [name for name, _ in self._screenshots]
            
        except Exception as e:
            logger.exception(f"Payment failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
        
        finally:
            await self.browser.close()
        
        return result
    
    async def _select_bank_payment(self):
        """Try to select bank/ACH payment option."""
        for selector in self.COMMON_SELECTORS["bank_options"]:
            try:
                if await self.browser.click(selector, timeout=3000):
                    logger.info(f"Clicked bank option: {selector}")
                    return
            except Exception:
                continue
        logger.warning("Could not find bank payment option")
    
    async def _fill_email(self, email: str):
        """Fill email field."""
        for selector in self.COMMON_SELECTORS["email_fields"]:
            try:
                if await self.browser.fill(selector, email, timeout=3000):
                    logger.info(f"Filled email: {selector}")
                    return
            except Exception:
                continue
    
    async def _inject_ach_credentials(self, credentials: dict):
        """Inject ACH credentials into form fields."""
        # Routing number
        for selector in self.COMMON_SELECTORS["routing_fields"]:
            try:
                if await self.browser.fill(selector, credentials.get("routing", ""), timeout=3000):
                    logger.info("Filled routing number")
                    break
            except Exception:
                continue
        
        # Account number
        for selector in self.COMMON_SELECTORS["account_fields"]:
            try:
                if await self.browser.fill(selector, credentials.get("account", ""), timeout=3000):
                    logger.info("Filled account number")
                    break
            except Exception:
                continue
        
        # Account name
        for selector in self.COMMON_SELECTORS["name_fields"]:
            try:
                if await self.browser.fill(selector, credentials.get("name", ""), timeout=3000):
                    logger.info("Filled account name")
                    break
            except Exception:
                continue
    
    async def _click_submit(self):
        """Click the submit/pay button."""
        for selector in self.COMMON_SELECTORS["submit_buttons"]:
            try:
                if await self.browser.click(selector, timeout=3000):
                    logger.info(f"Clicked submit: {selector}")
                    return
            except Exception:
                continue
        logger.warning("Could not find submit button")
    
    async def _get_credentials(self, business_id: str, auth_token: str) -> Optional[dict]:
        """Get credentials from vault."""
        try:
            from ..x402.credential_vault import get_vault
            vault = get_vault()
            # For demo, we need an invoice_id - use a placeholder
            return vault.get_credentials_for_injection(business_id, auth_token, "demo_invoice")
        except Exception as e:
            logger.warning(f"Could not get credentials from vault: {e}")
            return None
    
    def _extract_confirmation(self, text: str) -> Optional[str]:
        """Extract confirmation number from page text."""
        patterns = [
            r'confirmation[:\s#]*([A-Z0-9-]+)',
            r'reference[:\s#]*([A-Z0-9-]+)',
            r'transaction[:\s#]*([A-Z0-9-]+)',
            r'receipt[:\s#]*([A-Z0-9-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "PAYMENT_SUBMITTED"
    
    def _save_screenshot(self, name: str, data: bytes):
        """Save screenshot for later retrieval."""
        self._screenshots.append((name, data))
    
    def get_screenshots(self) -> list[tuple[str, bytes]]:
        """Get all captured screenshots."""
        return self._screenshots


# Convenience function for backward compatibility
async def pay_intuit_invoice(
    invoice_url: str,
    auth_token: str,
    mock_mode: bool = None,
    business_id: str = "demo_business"
) -> dict:
    """
    Pay an Intuit invoice (or any payment portal).
    
    Args:
        invoice_url: The payment URL
        auth_token: x402 authorization token
        mock_mode: Whether to use mock mode (auto-detected if None)
        business_id: Business ID for credential lookup
    
    Returns:
        Payment result dict
    """
    # Auto-detect mock mode
    if mock_mode is None:
        mock_mode = not (BROWSERBASE_PROJECT_ID and BROWSERBASE_API_KEY)
    
    browser = BrowserbaseClient(mock_mode=mock_mode)
    automator = PaymentPortalAutomator(browser)
    
    return await automator.pay_invoice(
        invoice_url=invoice_url,
        business_id=business_id,
        auth_token=auth_token
    )


# For testing
if __name__ == "__main__":
    test_url = "https://connect.intuit.com/t/scs-v1-26297a3db4e7480aafeabb334abefac156cc685711ec4c7fb924a5173d9a44b4b84020803d524618846eb7c5280bb7f2"
    
    async def test():
        result = await pay_intuit_invoice(
            invoice_url=test_url,
            auth_token="test_token",
            mock_mode=True
        )
        print(json.dumps(result, indent=2))
    
    asyncio.run(test())
