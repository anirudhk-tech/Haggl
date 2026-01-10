"""Vonage WhatsApp tool for the Message Agent."""

import os
import logging
import httpx

from ..schemas import OutgoingSMS

logger = logging.getLogger(__name__)

# Sandbox vs Production endpoints
VONAGE_SANDBOX_URL = "https://messages-sandbox.nexmo.com/v1/messages"
VONAGE_PRODUCTION_URL = "https://api.nexmo.com/v1/messages"


def _get_vonage_config() -> dict:
    """Get Vonage configuration from environment."""
    return {
        "api_key": os.getenv("VONAGE_API_KEY"),
        "api_secret": os.getenv("VONAGE_API_SECRET"),
        "whatsapp_number": os.getenv("VONAGE_WHATSAPP_NUMBER"),
        "sandbox": os.getenv("VONAGE_SANDBOX", "true").lower() == "true",
    }


async def send_sms(message: OutgoingSMS) -> dict:
    """
    Send a WhatsApp message via Vonage Messages API.
    
    Uses sandbox endpoint by default. Set VONAGE_SANDBOX=false for production.
    
    Args:
        message: OutgoingSMS with to_number and body
        
    Returns:
        dict with message_id, status, or error
    """
    config = _get_vonage_config()
    
    api_key = config["api_key"]
    api_secret = config["api_secret"]
    whatsapp_number = config["whatsapp_number"]
    use_sandbox = config["sandbox"]
    
    if not api_key or not api_secret:
        return {"error": "Vonage API credentials not configured", "message_id": None}
    
    if not whatsapp_number:
        return {"error": "VONAGE_WHATSAPP_NUMBER not configured", "message_id": None}
    
    # Choose endpoint
    url = VONAGE_SANDBOX_URL if use_sandbox else VONAGE_PRODUCTION_URL
    
    # Remove + from phone numbers
    to_number = message.to_number.replace("+", "")
    from_number = whatsapp_number.replace("+", "")
    
    logger.info(f"Sending WhatsApp to {to_number}")
    
    # Build request payload
    payload = {
        "from": from_number,
        "to": to_number,
        "message_type": "text",
        "text": message.body,
        "channel": "whatsapp",
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                auth=(api_key, api_secret),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=30.0,
            )
            
            if response.status_code in (200, 201, 202):
                data = response.json()
                message_uuid = data.get("message_uuid")
                logger.info(f"WhatsApp sent to {message.to_number}, ID: {message_uuid}")
                return {
                    "message_id": message_uuid,
                    "status": "sent",
                    "error": None,
                }
            else:
                error_text = response.text
                logger.error(f"Vonage API error {response.status_code}: {error_text}")
                return {
                    "error": f"Vonage API error {response.status_code}: {error_text}",
                    "message_id": None,
                }
                
    except Exception as e:
        logger.exception(f"Failed to send WhatsApp to {message.to_number}: {e}")
        return {
            "error": str(e),
            "message_id": None,
        }


def verify_webhook_signature(request_body: bytes, signature: str) -> bool:
    """
    Verify that a webhook request came from Vonage.
    
    Args:
        request_body: Raw request body bytes
        signature: Signature header value
        
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
