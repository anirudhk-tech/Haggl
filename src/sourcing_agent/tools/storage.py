"""Local JSON storage utilities for the Sourcing Agent."""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# Storage path relative to this file
STORAGE_PATH = Path(__file__).parent.parent / "data" / "vendors.json"


def load_vendors() -> dict:
    """
    Load vendors from local JSON file.

    Returns:
        dict: The stored vendor data, or empty dict if file doesn't exist
    """
    try:
        if STORAGE_PATH.exists():
            with open(STORAGE_PATH, "r") as f:
                data = json.load(f)
                return data if data else _get_empty_storage()
        return _get_empty_storage()
    except json.JSONDecodeError as e:
        logger.warning(f"Error decoding vendors.json: {e}, returning empty storage")
        return _get_empty_storage()
    except Exception as e:
        logger.error(f"Error loading vendors: {e}")
        return _get_empty_storage()


def save_vendors(data: dict) -> None:
    """
    Save vendors to local JSON file.

    Args:
        data: The vendor data to save
    """
    try:
        # Ensure the directory exists
        STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Update last_updated timestamp
        data["last_updated"] = datetime.utcnow().isoformat()

        with open(STORAGE_PATH, "w") as f:
            json.dump(data, f, indent=2, default=str)

        logger.info(f"Saved vendor data to {STORAGE_PATH}")
    except Exception as e:
        logger.error(f"Error saving vendors: {e}")
        raise


def add_vendor_results(request_id: str, results: list[dict], location: dict) -> None:
    """
    Append new vendor results to storage.

    Args:
        request_id: Unique request identifier
        results: List of VendorResult dicts
        location: UserLocation dict
    """
    data = load_vendors()

    # Store request results
    if "requests" not in data:
        data["requests"] = {}

    data["requests"][request_id] = {
        "timestamp": datetime.utcnow().isoformat(),
        "location": location,
        "results": results,
    }

    # Index vendors by ingredient for quick lookup
    if "vendors_by_ingredient" not in data:
        data["vendors_by_ingredient"] = {}

    for result in results:
        ingredient = result.get("ingredient", "unknown").lower()
        vendors = result.get("vendors", [])

        if ingredient not in data["vendors_by_ingredient"]:
            data["vendors_by_ingredient"][ingredient] = []

        # Add new vendors (avoid duplicates by source_url)
        existing_urls = {v.get("source_url") for v in data["vendors_by_ingredient"][ingredient]}
        for vendor in vendors:
            if vendor.get("source_url") not in existing_urls:
                data["vendors_by_ingredient"][ingredient].append(vendor)
                existing_urls.add(vendor.get("source_url"))

    save_vendors(data)
    logger.info(f"Added results for request {request_id}")


def get_vendors_by_ingredient(ingredient: str) -> list[dict]:
    """
    Retrieve cached vendors for an ingredient.

    Args:
        ingredient: The ingredient name to look up

    Returns:
        List of vendor dicts for that ingredient
    """
    data = load_vendors()
    vendors_by_ingredient = data.get("vendors_by_ingredient", {})
    return vendors_by_ingredient.get(ingredient.lower(), [])


def get_request_results(request_id: str) -> dict | None:
    """
    Get results for a specific request.

    Args:
        request_id: The request ID to look up

    Returns:
        Request data dict or None if not found
    """
    data = load_vendors()
    requests = data.get("requests", {})
    return requests.get(request_id)


def clear_storage() -> None:
    """Clear all stored vendor data."""
    save_vendors(_get_empty_storage())
    logger.info("Cleared all vendor storage")


def _get_empty_storage() -> dict:
    """Get an empty storage structure."""
    return {
        "last_updated": datetime.utcnow().isoformat(),
        "requests": {},
        "vendors_by_ingredient": {},
    }
