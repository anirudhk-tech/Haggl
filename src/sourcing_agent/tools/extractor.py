"""Claude-based data extraction and distance estimation for the Sourcing Agent."""

import os
import re
import json
import logging
from typing import Optional
from datetime import datetime
import httpx
from dotenv import load_dotenv

from ..schemas import (
    ExtractedVendor,
    VendorPricing,
    VendorQuantity,
    VendorReview,
    UserLocation,
    ExaSearchResult,
)

load_dotenv()
logger = logging.getLogger(__name__)

# Claude API configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1"

# Extraction prompt template
EXTRACTION_PROMPT = """You are extracting vendor/supplier information from a web page for a B2B procurement platform.

INGREDIENT BEING SOURCED: {ingredient_name}
PAGE URL: {page_url}

PAGE CONTENT:
{page_content}

Extract the following information in JSON format. If a field cannot be found, use null.

Required fields:
1. vendor_name: The company/business name
2. website: The vendor's website URL (use the page URL if not found)
3. phone: Contact phone number (format: +1-XXX-XXX-XXXX if possible)
4. email: Contact email address
5. address: Physical/shipping address
6. pricing:
   - price_per_unit: Price per unit as a number (e.g., 2.50)
   - unit: Unit of measurement (lb, kg, dozen, case, etc.)
   - currency: Currency code (USD)
   - bulk_discount_available: true/false
7. quantity:
   - available_quantity: Amount available (null if not specified)
   - unit: Unit for quantity
   - moq: Minimum Order Quantity as a number
   - moq_unit: Unit for MOQ
8. reviews:
   - rating: Rating out of 5 (e.g., 4.5)
   - review_count: Number of reviews
   - review_source: Where reviews are from (Google, Yelp, BBB, etc.)
9. certifications: List of certifications (e.g., ["FDA", "Organic", "USDA", "Kosher"])
10. extraction_confidence: How confident you are in this extraction (0.0-1.0)

Return ONLY valid JSON matching this exact structure:
{{
  "vendor_name": "string",
  "website": "string or null",
  "phone": "string or null",
  "email": "string or null",
  "address": "string or null",
  "pricing": {{
    "price_per_unit": number or null,
    "unit": "string or null",
    "currency": "USD",
    "bulk_discount_available": boolean
  }},
  "quantity": {{
    "available_quantity": number or null,
    "unit": "string or null",
    "moq": number or null,
    "moq_unit": "string or null"
  }},
  "reviews": {{
    "rating": number or null,
    "review_count": number or null,
    "review_source": "string or null"
  }},
  "certifications": ["string"],
  "extraction_confidence": number
}}

JSON Output:"""


# State distance estimates (in miles)
# For same-state distances, use approximate averages
STATE_DISTANCES = {
    # Same state
    ("CA", "CA"): 150,
    ("TX", "TX"): 200,
    ("NY", "NY"): 100,
    ("FL", "FL"): 150,
    # Default same-state
    "same_state": 100,

    # Neighboring states (examples)
    ("CA", "NV"): 300,
    ("CA", "AZ"): 400,
    ("CA", "OR"): 350,
    ("NY", "NJ"): 50,
    ("NY", "PA"): 150,
    ("NY", "CT"): 75,
    ("TX", "OK"): 250,
    ("TX", "LA"): 300,
    ("TX", "NM"): 400,
    ("FL", "GA"): 300,
    ("FL", "AL"): 350,

    # Default for other combinations
    "default": 500,
}


async def extract_vendor_info(
    search_result: ExaSearchResult,
    ingredient_name: str,
    user_location: UserLocation,
) -> Optional[ExtractedVendor]:
    """
    Use Claude to extract structured vendor information from web content.

    Args:
        search_result: The Exa search result containing page content
        ingredient_name: The ingredient being sourced
        user_location: User's location for distance calculation

    Returns:
        ExtractedVendor with all extracted fields, or None if extraction fails
    """
    page_content = search_result.text or " ".join(search_result.highlights)

    if not page_content:
        logger.warning(f"No content to extract from {search_result.url}")
        return _create_minimal_vendor(search_result, ingredient_name)

    # If we don't have Claude API key, use fallback extraction
    if not ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set, using fallback extraction")
        return _fallback_extract(search_result, ingredient_name, user_location)

    prompt = EXTRACTION_PROMPT.format(
        ingredient_name=ingredient_name,
        page_url=search_result.url,
        page_content=page_content[:4000],  # Limit content length
    )

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{ANTHROPIC_BASE_URL}/messages",
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 1024,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                },
            )
            response.raise_for_status()
            data = response.json()

            # Extract the text content from Claude's response
            content = data.get("content", [])
            if not content:
                logger.warning("Empty response from Claude")
                return _fallback_extract(search_result, ingredient_name, user_location)

            text = content[0].get("text", "")

            # Parse the JSON from Claude's response
            vendor_data = _parse_json_response(text)
            if not vendor_data:
                logger.warning(f"Failed to parse Claude response for {search_result.url}")
                return _fallback_extract(search_result, ingredient_name, user_location)

            # Calculate distance
            distance = estimate_distance(
                vendor_data.get("address"),
                user_location,
            )

            # Build the ExtractedVendor
            pricing = None
            if vendor_data.get("pricing"):
                pricing = VendorPricing(**vendor_data["pricing"])

            quantity = None
            if vendor_data.get("quantity"):
                quantity = VendorQuantity(**vendor_data["quantity"])

            reviews = None
            if vendor_data.get("reviews"):
                reviews = VendorReview(**vendor_data["reviews"])

            return ExtractedVendor(
                vendor_name=vendor_data.get("vendor_name") or search_result.title or "Unknown Vendor",
                website=vendor_data.get("website") or search_result.url,
                phone=vendor_data.get("phone"),
                email=vendor_data.get("email"),
                address=vendor_data.get("address"),
                pricing=pricing,
                quantity=quantity,
                reviews=reviews,
                distance_miles=distance,
                certifications=vendor_data.get("certifications", []),
                source_url=search_result.url,
                extraction_confidence=vendor_data.get("extraction_confidence", 0.5),
                extracted_at=datetime.utcnow().isoformat(),
            )

    except httpx.HTTPStatusError as e:
        logger.error(f"Claude API error: {e.response.status_code} - {e.response.text}")
        return _fallback_extract(search_result, ingredient_name, user_location)
    except Exception as e:
        logger.error(f"Error extracting vendor info: {e}")
        return _fallback_extract(search_result, ingredient_name, user_location)


def estimate_distance(
    vendor_address: Optional[str],
    user_location: UserLocation,
) -> Optional[float]:
    """
    Estimate shipping distance based on state/city matching.

    Args:
        vendor_address: The vendor's address string
        user_location: User's location

    Returns:
        Estimated distance in miles, or None if cannot determine
    """
    if not vendor_address:
        return None

    # Try to extract state from address
    vendor_state = _extract_state(vendor_address)
    if not vendor_state:
        return STATE_DISTANCES["default"]

    user_state = user_location.state.upper()
    vendor_state = vendor_state.upper()

    # Check if same city (rough match)
    if user_location.city.lower() in vendor_address.lower():
        return 15.0  # Same city estimate

    # Same state
    if vendor_state == user_state:
        return STATE_DISTANCES.get((user_state, user_state), STATE_DISTANCES["same_state"])

    # Check for specific state pair distances
    pair = (user_state, vendor_state)
    reverse_pair = (vendor_state, user_state)

    if pair in STATE_DISTANCES:
        return STATE_DISTANCES[pair]
    if reverse_pair in STATE_DISTANCES:
        return STATE_DISTANCES[reverse_pair]

    # Default for unknown pairs
    return STATE_DISTANCES["default"]


def _extract_state(address: str) -> Optional[str]:
    """Extract state abbreviation from address string."""
    # Common US state abbreviations
    states = [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    ]

    # Look for state abbreviation pattern (e.g., "CA" or ", CA")
    for state in states:
        pattern = rf'\b{state}\b'
        if re.search(pattern, address.upper()):
            return state

    return None


def _parse_json_response(text: str) -> Optional[dict]:
    """Parse JSON from Claude's response text."""
    try:
        # Try direct JSON parse first
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find JSON object in text
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def _fallback_extract(
    search_result: ExaSearchResult,
    ingredient_name: str,
    user_location: UserLocation,
) -> ExtractedVendor:
    """
    Fallback extraction using regex patterns when Claude is unavailable.
    """
    content = search_result.text or " ".join(search_result.highlights)

    # Try to extract phone number
    phone_match = re.search(
        r'(?:\+1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
        content
    )
    phone = None
    if phone_match:
        phone = f"+1-{phone_match.group(1)}-{phone_match.group(2)}-{phone_match.group(3)}"

    # Try to extract email
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
    email = email_match.group(0) if email_match else None

    # Try to extract price
    price_match = re.search(r'\$\s*(\d+(?:\.\d{2})?)\s*(?:per|/)\s*(\w+)', content, re.IGNORECASE)
    pricing = None
    if price_match:
        pricing = VendorPricing(
            price_per_unit=float(price_match.group(1)),
            unit=price_match.group(2),
            currency="USD",
            bulk_discount_available=False,
        )

    # Try to extract MOQ
    moq_match = re.search(
        r'(?:minimum|min)\.?\s*(?:order|qty)\.?\s*(?:quantity)?(?:\s*[:=])?\s*(\d+)',
        content,
        re.IGNORECASE
    )
    quantity = None
    if moq_match:
        quantity = VendorQuantity(moq=float(moq_match.group(1)))

    return ExtractedVendor(
        vendor_name=search_result.title or "Unknown Vendor",
        website=search_result.url,
        phone=phone,
        email=email,
        address=None,
        pricing=pricing,
        quantity=quantity,
        reviews=None,
        distance_miles=estimate_distance(None, user_location),
        certifications=[],
        source_url=search_result.url,
        extraction_confidence=0.3,  # Lower confidence for fallback
        extracted_at=datetime.utcnow().isoformat(),
    )


def _create_minimal_vendor(
    search_result: ExaSearchResult,
    ingredient_name: str,
) -> ExtractedVendor:
    """Create a minimal vendor entry when we have no content."""
    return ExtractedVendor(
        vendor_name=search_result.title or "Unknown Vendor",
        website=search_result.url,
        phone=None,
        email=None,
        address=None,
        pricing=None,
        quantity=None,
        reviews=None,
        distance_miles=None,
        certifications=[],
        source_url=search_result.url,
        extraction_confidence=0.1,
        extracted_at=datetime.utcnow().isoformat(),
    )
