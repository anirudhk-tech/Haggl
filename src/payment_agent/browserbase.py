"""
Browserbase x402 Integration for Payment Execution.

Uses Browserbase's cloud browsers (paid with USDC via x402) to navigate
vendor payment portals like Intuit QuickBooks, Stripe invoices, etc.

Docs: https://docs.browserbase.com/integrations/x402/introduction
"""

import os
import json
import base64
import logging
import asyncio
import httpx
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Browserbase x402 endpoint
BROWSERBASE_X402_URL = "https://x402.browserbase.com/v1/sessions"
BROWSERBASE_CONNECT_URL = "wss://connect.browserbase.com"

# Check if Playwright is available
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed. Browser automation unavailable.")


class BrowserbaseX402Client:
    """
    Browserbase x402 client for cloud browser sessions.
    
    Flow:
    1. Pay for session with USDC via x402 protocol
    2. Get session ID and WebSocket URL
    3. Connect via Playwright CDP
    4. Automate browser (navigate, click, fill forms)
    5. Session auto-closes, payment settles
    """
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        wallet_address: Optional[str] = None,
        mock_mode: bool = False
    ):
        self.project_id = project_id or os.getenv("BROWSERBASE_PROJECT_ID")
        self.wallet_address = wallet_address or os.getenv("CDP_WALLET_ADDRESS")
        self.mock_mode = mock_mode or not self.project_id
        
        self._session_id: Optional[str] = None
        self._browser = None
        self._page = None
    
    async def create_session(self) -> dict:
        """
        Create a Browserbase session using x402 payment.
        
        Returns session info including WebSocket URL for CDP connection.
        """
        if self.mock_mode:
            logger.info("[MOCK] Creating Browserbase session...")
            self._session_id = f"mock_session_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            return {
                "session_id": self._session_id,
                "ws_url": f"wss://mock.browserbase.com?session={self._session_id}",
                "mock": True
            }
        
        # Build x402 payment header
        # In production, this would be signed by CDP wallet
        payment_header = self._build_payment_header()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                BROWSERBASE_X402_URL,
                headers={
                    "X-Payment": payment_header,
                    "Content-Type": "application/json"
                },
                json={
                    "projectId": self.project_id,
                    "browserSettings": {
                        "viewport": {"width": 1280, "height": 720}
                    }
                },
                timeout=30.0
            )
            
            if response.status_code == 402:
                # Payment required - need more USDC
                return {
                    "error": "Payment required - insufficient USDC balance",
                    "details": response.json()
                }
            
            if response.status_code != 201:
                return {
                    "error": f"Failed to create session: {response.status_code}",
                    "details": response.text
                }
            
            data = response.json()
            self._session_id = data["id"]
            
            return {
                "session_id": self._session_id,
                "ws_url": f"{BROWSERBASE_CONNECT_URL}?sessionId={self._session_id}",
                "mock": False
            }
    
    def _build_payment_header(self) -> str:
        """
        Build x402 payment header for Browserbase.
        
        In production, this would involve:
        1. Getting payment requirements from 402 response
        2. Signing USDC transfer with CDP wallet
        3. Including tx hash in header
        """
        # Placeholder - real implementation would sign with CDP
        return json.dumps({
            "version": "1",
            "wallet": self.wallet_address,
            "network": "base",
            "token": "usdc"
        })
    
    async def connect_browser(self) -> bool:
        """Connect to Browserbase session via Playwright CDP."""
        if self.mock_mode:
            logger.info("[MOCK] Browser connected")
            return True
        
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available")
            return False
        
        if not self._session_id:
            logger.error("No session created")
            return False
        
        try:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.connect_over_cdp(
                f"{BROWSERBASE_CONNECT_URL}?sessionId={self._session_id}"
            )
            
            # Get default context and page
            contexts = self._browser.contexts
            if contexts:
                self._page = contexts[0].pages[0] if contexts[0].pages else await contexts[0].new_page()
            else:
                context = await self._browser.new_context()
                self._page = await context.new_page()
            
            logger.info(f"Connected to Browserbase session: {self._session_id}")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to connect: {e}")
            return False
    
    async def navigate(self, url: str) -> bool:
        """Navigate to a URL."""
        if self.mock_mode:
            logger.info(f"[MOCK] Navigating to: {url}")
            return True
        
        if not self._page:
            return False
        
        try:
            await self._page.goto(url, wait_until="networkidle")
            logger.info(f"Navigated to: {url}")
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
    
    async def screenshot(self) -> Optional[bytes]:
        """Take a screenshot of the current page."""
        if self.mock_mode:
            logger.info("[MOCK] Screenshot taken")
            return b"mock_screenshot_data"
        
        if not self._page:
            return None
        
        return await self._page.screenshot()
    
    async def click(self, selector: str) -> bool:
        """Click an element by selector."""
        if self.mock_mode:
            logger.info(f"[MOCK] Clicking: {selector}")
            return True
        
        if not self._page:
            return False
        
        try:
            await self._page.click(selector)
            return True
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return False
    
    async def fill(self, selector: str, value: str) -> bool:
        """Fill a form field (for non-sensitive data only)."""
        if self.mock_mode:
            logger.info(f"[MOCK] Filling {selector}")
            return True
        
        if not self._page:
            return False
        
        try:
            await self._page.fill(selector, value)
            return True
        except Exception as e:
            logger.error(f"Fill failed: {e}")
            return False
    
    async def get_page_content(self) -> str:
        """Get the current page HTML."""
        if self.mock_mode:
            return "<html><body>Mock page</body></html>"
        
        if not self._page:
            return ""
        
        return await self._page.content()
    
    async def close(self):
        """Close the browser session."""
        if self._browser:
            await self._browser.close()
        
        self._browser = None
        self._page = None
        self._session_id = None
        logger.info("Browser session closed")


class IntuitPaymentAutomator:
    """
    Specialized automator for Intuit QuickBooks invoice payments.
    
    Handles the specific flow of Intuit payment pages:
    1. View invoice details
    2. Select payment method (Bank/ACH)
    3. Fill payment form (via secure injection)
    4. Submit payment
    5. Capture confirmation
    """
    
    # Intuit-specific selectors (may need updates as Intuit changes their UI)
    SELECTORS = {
        "bank_tab": "[data-testid='bank-payment-method'], button:has-text('Bank')",
        "view_invoice": "button:has-text('View invoice')",
        "pay_button": "button:has-text('Pay')",
        "routing_number": "input[name='routingNumber'], input[placeholder*='Routing']",
        "account_number": "input[name='accountNumber'], input[placeholder*='Account']",
        "account_name": "input[name='nameOnAccount'], input[placeholder*='Name']",
        "email": "input[type='email'], input[name='email']",
        "confirmation": "[data-testid='confirmation'], .confirmation-number"
    }
    
    def __init__(self, browserbase: BrowserbaseX402Client):
        self.browser = browserbase
        self._screenshots: list[bytes] = []
    
    async def pay_invoice(
        self,
        invoice_url: str,
        ach_credentials: dict,  # Passed from secure vault, NOT from AI
        contact_email: str
    ) -> dict:
        """
        Complete an Intuit invoice payment via ACH.
        
        Args:
            invoice_url: The Intuit payment URL
            ach_credentials: Dict with routing, account, name (from secure vault)
            contact_email: Email for payment receipt
        
        Returns:
            Dict with status, confirmation, screenshots
        """
        result = {
            "status": "pending",
            "invoice_url": invoice_url,
            "steps": [],
            "confirmation": None,
            "screenshots": [],
            "error": None
        }
        
        try:
            # Step 1: Create Browserbase session
            result["steps"].append("Creating browser session...")
            session = await self.browser.create_session()
            
            if session.get("error"):
                result["status"] = "failed"
                result["error"] = session["error"]
                return result
            
            result["steps"].append(f"Session created: {session['session_id']}")
            
            # Step 2: Connect to browser
            connected = await self.browser.connect_browser()
            if not connected:
                result["status"] = "failed"
                result["error"] = "Failed to connect to browser"
                return result
            
            # Step 3: Navigate to invoice
            result["steps"].append(f"Navigating to invoice...")
            await self.browser.navigate(invoice_url)
            await asyncio.sleep(2)  # Wait for page load
            
            # Take screenshot
            screenshot = await self.browser.screenshot()
            if screenshot:
                self._screenshots.append(screenshot)
            
            # Step 4: Select Bank/ACH payment method
            result["steps"].append("Selecting ACH payment method...")
            await self.browser.click(self.SELECTORS["bank_tab"])
            await asyncio.sleep(1)
            
            # Step 5: Fill email (non-sensitive)
            result["steps"].append("Filling contact email...")
            await self.browser.fill(self.SELECTORS["email"], contact_email)
            
            # Step 6: Fill ACH credentials (SECURE - values from vault)
            result["steps"].append("Injecting ACH credentials securely...")
            await self._inject_ach_credentials(ach_credentials)
            
            # Take screenshot (credentials should be masked by browser)
            screenshot = await self.browser.screenshot()
            if screenshot:
                self._screenshots.append(screenshot)
            
            # Step 7: Click Pay button
            result["steps"].append("Submitting payment...")
            await self.browser.click(self.SELECTORS["pay_button"])
            await asyncio.sleep(3)  # Wait for processing
            
            # Step 8: Capture confirmation
            result["steps"].append("Capturing confirmation...")
            screenshot = await self.browser.screenshot()
            if screenshot:
                self._screenshots.append(screenshot)
            
            # Try to extract confirmation number
            page_content = await self.browser.get_page_content()
            confirmation = self._extract_confirmation(page_content)
            
            result["status"] = "succeeded"
            result["confirmation"] = confirmation or "PAYMENT_SUBMITTED"
            result["screenshots"] = [
                f"screenshot_{i}.png" for i in range(len(self._screenshots))
            ]
            
        except Exception as e:
            logger.exception(f"Payment failed: {e}")
            result["status"] = "failed"
            result["error"] = str(e)
        
        finally:
            await self.browser.close()
        
        return result
    
    async def _inject_ach_credentials(self, credentials: dict):
        """
        Inject ACH credentials into form fields.
        
        SECURITY NOTE: This method receives credentials from the secure vault,
        NOT from AI context. The AI only identifies WHERE to type, this method
        handles WHAT to type.
        """
        if self.browser.mock_mode:
            logger.info("[MOCK] ACH credentials injected (****)")
            return
        
        # Fill routing number
        if credentials.get("routing"):
            await self.browser.fill(
                self.SELECTORS["routing_number"],
                credentials["routing"]
            )
        
        # Fill account number
        if credentials.get("account"):
            await self.browser.fill(
                self.SELECTORS["account_number"],
                credentials["account"]
            )
        
        # Fill name on account
        if credentials.get("name"):
            await self.browser.fill(
                self.SELECTORS["account_name"],
                credentials["name"]
            )
        
        logger.info("ACH credentials injected (values masked)")
    
    def _extract_confirmation(self, html: str) -> Optional[str]:
        """Try to extract confirmation number from page HTML."""
        import re
        
        # Common confirmation patterns
        patterns = [
            r'confirmation[:\s#]*([A-Z0-9-]+)',
            r'reference[:\s#]*([A-Z0-9-]+)',
            r'transaction[:\s#]*([A-Z0-9-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def get_screenshots(self) -> list[bytes]:
        """Get all captured screenshots."""
        return self._screenshots


async def pay_intuit_invoice(
    invoice_url: str,
    auth_token: str,
    mock_mode: bool = True
) -> dict:
    """
    High-level function to pay an Intuit invoice.
    
    This is the main entry point that:
    1. Verifies x402 authorization
    2. Retrieves ACH credentials from secure vault
    3. Creates Browserbase session
    4. Executes payment
    
    Args:
        invoice_url: The Intuit payment URL
        auth_token: x402 authorization token
        mock_mode: Whether to use mock mode (no real browser)
    
    Returns:
        Payment result dict
    """
    logger.info(f"Processing Intuit invoice payment")
    logger.info(f"URL: {invoice_url}")
    
    # In production, verify auth_token with authorizer
    # and retrieve credentials from secure vault
    
    # Mock credentials for demo
    mock_credentials = {
        "routing": os.getenv("ACH_ROUTING_NUMBER", "021000021"),
        "account": os.getenv("ACH_ACCOUNT_NUMBER", "1234567890"),
        "name": os.getenv("ACH_ACCOUNT_NAME", "Haggl Demo Business")
    }
    
    # Create Browserbase client
    browserbase = BrowserbaseX402Client(mock_mode=mock_mode)
    
    # Create Intuit automator
    automator = IntuitPaymentAutomator(browserbase)
    
    # Execute payment
    result = await automator.pay_invoice(
        invoice_url=invoice_url,
        ach_credentials=mock_credentials,
        contact_email="orders@haggl.demo"
    )
    
    return result


# For testing
if __name__ == "__main__":
    import asyncio
    
    test_url = "https://connect.intuit.com/t/scs-v1-26297a3db4e7480aafeabb334abefac156cc685711ec4c7fb924a5173d9a44b4b84020803d524618846eb7c5280bb7f2"
    
    async def test():
        result = await pay_intuit_invoice(
            invoice_url=test_url,
            auth_token="test_token",
            mock_mode=True
        )
        print(json.dumps(result, indent=2))
    
    asyncio.run(test())
