"""Vonage SMS tool for the Message Agent."""

import os
import logging
from functools import lru_cache

import vonage

from ..schemas import OutgoingSMS

logger = logging.getLogger(__name__)

# Sandbox vs Production endpoints
VONAGE_SANDBOX_URL = "https://messages-sandbox.nexmo.com/v1/messages"
VONAGE_PRODUCTION_URL = "https://api.nexmo.com/v1/messages"


def _get_vonage_config() -> tuple[str | None, str | None, str | None]:
    """Get Vonage configuration from environment."""
    return (
        os.getenv("VONAGE_API_KEY"),
        os.getenv("VONAGE_API_SECRET"),
        os.getenv("VONAGE_PHONE_NUMBER"),
    )


@lru_cache(maxsize=1)
def _get_vonage_client() -> vonage.Client | None:
    """Get or create Vonage client (cached)."""
    api_key, api_secret, _ = _get_vonage_config()
    
    if not api_key or not api_secret:
        logger.warning("Vonage credentials not configured")
        return None
    
    return vonage.Client(key=api_key, secret=api_secret)


async def send_sms(message: OutgoingSMS) -> dict:
    """
    Send an SMS via Vonage.
    
    Args:
        message: OutgoingSMS with to_number and body
        
    Returns:
        dict with message_id, status, or error
    """
    api_key, api_secret, phone_number = _get_vonage_config()
    
    if not api_key or not api_secret:
        return {"error": "Vonage credentials not configured", "message_id": None}
    
    if not phone_number:
        return {"error": "VONAGE_PHONE_NUMBER not configured", "message_id": None}
    
    client = _get_vonage_client()
    if not client:
        return {"error": "Failed to initialize Vonage client", "message_id": None}
    
    try:
        sms = vonage.Sms(client)
        response = sms.send_message({
            "from": phone_number,
            "to": message.to_number.replace("+", ""),  # Vonage doesn't want the +
            "text": message.body,
        })
        
        # Check response status
        if response["messages"][0]["status"] == "0":
            message_id = response["messages"][0]["message-id"]
            logger.info(f"SMS sent to {message.to_number}, ID: {message_id}")
            return {
                "message_id": message_id,
                "status": "sent",
                "error": None,
            }
        else:
            error_text = response["messages"][0].get("error-text", "Unknown error")
            logger.error(f"Failed to send SMS: {error_text}")
            return {
                "error": error_text,
                "message_id": None,
            }
        
    except Exception as e:
        logger.exception(f"Failed to send SMS to {message.to_number}: {e}")
        return {
            "error": str(e),
            "message_id": None,
        }


def verify_webhook_signature(request_body: bytes, signature: str) -> bool:
    """
    Verify that a webhook request came from Vonage.
    
    Args:
        request_body: Raw request body bytes
        signature: X-Vonage-Signature header value
        
    Returns:
        bool indicating if signature is valid
    """
    signature_secret = os.getenv("VONAGE_SIGNATURE_SECRET")
    
    if not signature_secret:
        logger.warning("Cannot verify Vonage signature: SIGNATURE_SECRET not configured")
        return False
    
    try:
        import hashlib
        import hmac
        
        expected_signature = hmac.new(
            signature_secret.encode(),
            request_body,
            hashlib.sha256
        ).hexdigest()
        
        is_valid = hmac.compare_digest(signature, expected_signature)
        
        if not is_valid:
            logger.warning("Invalid Vonage webhook signature")
        
        return is_valid
        
    except Exception as e:
        logger.exception(f"Error verifying Vonage signature: {e}")
        return False
