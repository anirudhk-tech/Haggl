"""Vendor storage operations."""

import logging
from datetime import datetime
from typing import Optional
import uuid

from .database import get_collection
from .schemas import VendorDocument, VendorEmbedding

logger = logging.getLogger(__name__)

COLLECTION = "vendors"
EMBEDDINGS_COLLECTION = "vendor_embeddings"


def save_vendor(vendor: VendorDocument) -> bool:
    """
    Save or update a vendor document.
    
    Args:
        vendor: VendorDocument to save
        
    Returns:
        True if successful
    """
    collection = get_collection(COLLECTION)
    if collection is None:
        logger.warning("No database connection - vendor not saved")
        return False
    
    try:
        vendor.updated_at = datetime.utcnow()
        collection.update_one(
            {"vendor_id": vendor.vendor_id},
            {"$set": vendor.model_dump()},
            upsert=True
        )
        logger.info(f"Saved vendor: {vendor.vendor_id} ({vendor.name})")
        return True
    except Exception as e:
        logger.error(f"Failed to save vendor: {e}")
        return False


def get_vendor_by_id(vendor_id: str) -> Optional[VendorDocument]:
    """Get a vendor by ID."""
    collection = get_collection(COLLECTION)
    if collection is None:
        return None
    
    try:
        doc = collection.find_one({"vendor_id": vendor_id})
        if doc:
            doc.pop("_id", None)
            return VendorDocument(**doc)
        return None
    except Exception as e:
        logger.error(f"Failed to get vendor: {e}")
        return None


def get_vendors_by_ingredient(ingredient: str, limit: int = 10) -> list[VendorDocument]:
    """
    Get vendors that supply a specific ingredient.
    
    Args:
        ingredient: Ingredient name (case-insensitive)
        limit: Max vendors to return
        
    Returns:
        List of VendorDocuments
    """
    collection = get_collection(COLLECTION)
    if collection is None:
        return []
    
    try:
        cursor = collection.find(
            {"ingredient": {"$regex": ingredient, "$options": "i"}}
        ).limit(limit)
        
        vendors = []
        for doc in cursor:
            doc.pop("_id", None)
            vendors.append(VendorDocument(**doc))
        
        logger.info(f"Found {len(vendors)} vendors for {ingredient}")
        return vendors
    except Exception as e:
        logger.error(f"Failed to get vendors by ingredient: {e}")
        return []


def save_vendor_embedding(embedding: VendorEmbedding) -> bool:
    """
    Save a vendor embedding for vector search.
    
    Args:
        embedding: VendorEmbedding to save
        
    Returns:
        True if successful
    """
    collection = get_collection(EMBEDDINGS_COLLECTION)
    if collection is None:
        logger.warning("No database connection - embedding not saved")
        return False
    
    try:
        collection.update_one(
            {"vendor_id": embedding.vendor_id},
            {"$set": embedding.model_dump()},
            upsert=True
        )
        logger.info(f"Saved embedding for vendor: {embedding.vendor_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to save embedding: {e}")
        return False


def search_vendors_by_embedding(
    query_embedding: list[float],
    ingredient: Optional[str] = None,
    limit: int = 5
) -> list[dict]:
    """
    Search vendors using vector similarity.
    
    Note: For production, use MongoDB Atlas Vector Search.
    This is a simple cosine similarity fallback.
    
    Args:
        query_embedding: Query vector
        ingredient: Optional filter by ingredient
        limit: Max results
        
    Returns:
        List of vendor dicts with similarity scores
    """
    collection = get_collection(EMBEDDINGS_COLLECTION)
    if collection is None:
        return []
    
    try:
        # Build query filter
        query = {}
        if ingredient:
            query["ingredient"] = {"$regex": ingredient, "$options": "i"}
        
        # Get all embeddings (for small datasets)
        # For production, use Atlas Vector Search index
        cursor = collection.find(query)
        
        results = []
        for doc in cursor:
            # Calculate cosine similarity
            doc_embedding = doc.get("embedding", [])
            if len(doc_embedding) == len(query_embedding):
                similarity = _cosine_similarity(query_embedding, doc_embedding)
                results.append({
                    "vendor_id": doc["vendor_id"],
                    "ingredient": doc.get("ingredient"),
                    "similarity": similarity,
                })
        
        # Sort by similarity and limit
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:limit]
        
    except Exception as e:
        logger.error(f"Failed to search embeddings: {e}")
        return []


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    import math
    
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)


def save_sourced_vendors(
    ingredient: str,
    vendors: list[dict],
    source: str = "exa"
) -> int:
    """
    Bulk save vendors from sourcing agent.
    
    Args:
        ingredient: The ingredient these vendors supply
        vendors: List of vendor dicts from sourcing
        source: Source of the data (exa, manual, etc.)
        
    Returns:
        Number of vendors saved
    """
    saved = 0
    for v in vendors:
        vendor_id = v.get("vendor_id") or f"vendor-{uuid.uuid4().hex[:8]}"
        
        vendor = VendorDocument(
            vendor_id=vendor_id,
            name=v.get("name", "Unknown Vendor"),
            ingredient=ingredient,
            phone=v.get("phone"),
            email=v.get("email"),
            website=v.get("website"),
            source_url=v.get("source_url"),
            certifications=v.get("certifications", []),
            # Evaluation scores
            quality_score=v.get("quality_score", 50.0),
            reliability_score=v.get("reliability_score", 50.0),
        )
        
        # Add location if present
        if any(k in v for k in ["address", "city", "state", "distance_miles"]):
            from .schemas import VendorLocation
            vendor.location = VendorLocation(
                address=v.get("address"),
                city=v.get("city"),
                state=v.get("state"),
                distance_miles=v.get("distance_miles"),
            )
        
        # Add pricing if present
        if v.get("price_per_unit") or v.get("unit"):
            from .schemas import VendorPricing
            vendor.pricing = VendorPricing(
                price_per_unit=v.get("price_per_unit"),
                unit=v.get("unit"),
            )
        
        # Add reviews if present
        if v.get("rating"):
            from .schemas import VendorReviews
            vendor.reviews = VendorReviews(
                rating=v.get("rating"),
            )
        
        if save_vendor(vendor):
            saved += 1
    
    logger.info(f"Saved {saved}/{len(vendors)} vendors for {ingredient}")
    return saved
