# Evaluation Agent
## Voyage AI Fine-Tuned Vendor Selection System

**Version:** 1.0
**Date:** January 10, 2026
**Framework:** Voyage AI Fine-Tuning

---

## Overview

The Evaluation Agent is a **personalized vendor selection system** that learns the unique preferences of each business owner. Using Voyage AI's fine-tuning capabilities, the agent adapts to individual taste profiles across four key dimensions: **Quality, Affordability, Shipping, and Reliability**.

### Key Features

| Feature | Description |
|---------|-------------|
| **Personalized Scoring** | Fine-tuned model learns owner's specific preferences |
| **4-Dimension Analysis** | Quality, Affordability, Shipping (distance), Reliability |
| **Interactive Feedback** | Up/down voting on radar chart updates model weights |
| **Continuous Learning** | Loss function updates model based on feedback |
| **Fast Training** | Complete fine-tuning in <1 hour |

---

## File Structure

```
src/evaluation_agent/
├── __init__.py              # Module exports
├── agent.py                 # Main EvaluationAgent class
├── schemas.py               # Pydantic models
├── tools/
│   ├── __init__.py          # Tool exports
│   ├── voyage_tool.py       # Voyage AI fine-tuning & inference
│   └── mongo_tool.py        # MongoDB operations for preferences
└── evaluation-agent.md      # This documentation
```

---

## The Four Parameters

```
                         QUALITY
                           100%
                            │
                            │
                      ●─────┼─────●
                     ╱      │      ╲
                    ╱       │       ╲
                   ╱        │        ╲
                  ╱         │         ╲
    RELIABILITY ●───────────┼───────────● AFFORDABILITY
                  ╲         │         ╱
                   ╲        │        ╱
                    ╲       │       ╱
                     ╲      │      ╱
                      ●─────┼─────●
                            │
                            │
                         SHIPPING
                          (Distance)
```

### Parameter Definitions

| Parameter | Weight Range | Description | Data Sources |
|-----------|-------------|-------------|--------------|
| **Quality** | 0-100 | Product grade, certifications, reviews | FDA certs, organic labels, user reviews |
| **Affordability** | 0-100 | Price competitiveness, discounts achieved | Base price, negotiated price, market avg |
| **Shipping** | 0-100 | Delivery distance, speed, cost | Distance calc, shipping rates, delivery time |
| **Reliability** | 0-100 | On-time delivery, order accuracy, consistency | Historical data, vendor track record |

---

## Voyage AI Fine-Tuning

### Why Voyage AI?

| Feature | Benefit |
|---------|---------|
| **Fast Fine-Tuning** | Complete training in <1 hour |
| **Lightweight Models** | voyage-lite-02-instruct as base |
| **Embedding Quality** | State-of-the-art retrieval embeddings |
| **Cost Efficient** | Pay-per-use, no GPU infrastructure needed |
| **API-First** | Simple REST API for training and inference |

### Model Selection

**Base Model:** `voyage-lite-02-instruct`

| Model | Parameters | Training Time | Use Case |
|-------|------------|---------------|----------|
| voyage-lite-02-instruct | ~350M | 15-30 min | **Selected** - Fast, lightweight |
| voyage-02 | ~1B | 30-45 min | Higher accuracy, more compute |
| voyage-large-2 | ~2B | 45-60 min | Maximum accuracy |

---

## Implementation Files

---

### `__init__.py`

```python
"""Haggl Evaluation Agent - Personalized Vendor Selection with Voyage AI"""

__version__ = "0.1.0"

from .agent import EvaluationAgent, get_evaluation_agent

__all__ = ["EvaluationAgent", "get_evaluation_agent"]
```

---

### `schemas.py`

```python
"""Pydantic schemas for the Evaluation Agent."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class EvaluationParameter(str, Enum):
    """The four evaluation parameters."""
    QUALITY = "quality"
    AFFORDABILITY = "affordability"
    SHIPPING = "shipping"
    RELIABILITY = "reliability"


class FeedbackDirection(str, Enum):
    """Direction of user feedback."""
    UP = "up"
    DOWN = "down"


class PreferenceWeights(BaseModel):
    """Current preference weights for a business."""
    quality: float = Field(default=0.30, ge=0.05, le=0.60)
    affordability: float = Field(default=0.35, ge=0.05, le=0.60)
    shipping: float = Field(default=0.15, ge=0.05, le=0.60)
    reliability: float = Field(default=0.20, ge=0.05, le=0.60)

    def normalize(self) -> "PreferenceWeights":
        """Normalize weights to sum to 1.0."""
        total = self.quality + self.affordability + self.shipping + self.reliability
        return PreferenceWeights(
            quality=self.quality / total,
            affordability=self.affordability / total,
            shipping=self.shipping / total,
            reliability=self.reliability / total,
        )


class VendorScores(BaseModel):
    """Scores for a vendor across all parameters."""
    quality: float = Field(ge=0, le=100)
    affordability: float = Field(ge=0, le=100)
    shipping: float = Field(ge=0, le=100)
    reliability: float = Field(ge=0, le=100)


class VendorEvaluation(BaseModel):
    """Complete evaluation result for a vendor."""
    vendor_id: str
    vendor_name: str
    scores: VendorScores
    embedding_score: float = Field(ge=0, le=1)
    parameter_score: float = Field(ge=0, le=1)
    final_score: float = Field(ge=0, le=1)
    rank: Optional[int] = None


class FeedbackRequest(BaseModel):
    """User feedback on a vendor evaluation."""
    vendor_id: str
    parameter: EvaluationParameter
    direction: FeedbackDirection


class FeedbackRecord(BaseModel):
    """Stored feedback record."""
    business_id: str
    vendor_id: str
    parameter: EvaluationParameter
    direction: FeedbackDirection
    weights_before: PreferenceWeights
    weights_after: PreferenceWeights
    timestamp: str


class BusinessPreferences(BaseModel):
    """Complete preferences for a business."""
    business_id: str
    weights: PreferenceWeights
    voyage_model_id: Optional[str] = None
    total_feedback_count: int = 0
    training_status: str = "pending"  # pending | training | completed | failed


class EvaluationRequest(BaseModel):
    """Request to evaluate vendors."""
    business_id: str
    budget: float = Field(gt=0)
    ingredients: list[str] = Field(min_length=1)


class EvaluationResponse(BaseModel):
    """Response from vendor evaluation."""
    selected_vendors: list[VendorEvaluation]
    total_cost: float
    budget: float
    savings: float
    weights_used: PreferenceWeights
```

---

### `agent.py`

```python
"""
Evaluation Agent - Personalized Vendor Selection with Voyage AI

Scores and selects vendors based on business owner's learned preferences
across four dimensions: Quality, Affordability, Shipping, Reliability.
"""

import os
import logging
from typing import Optional
from datetime import datetime

from .schemas import (
    EvaluationParameter,
    FeedbackDirection,
    PreferenceWeights,
    VendorScores,
    VendorEvaluation,
    FeedbackRequest,
    FeedbackRecord,
    BusinessPreferences,
    EvaluationRequest,
    EvaluationResponse,
)
from .tools import (
    get_business_preferences,
    save_business_preferences,
    save_feedback,
    score_vendors_with_voyage,
    should_retrain,
    queue_retraining_job,
)

logger = logging.getLogger(__name__)

# Configuration
LEARNING_RATE = float(os.getenv("EVAL_LEARNING_RATE", "0.05"))
MIN_WEIGHT = float(os.getenv("EVAL_MIN_WEIGHT", "0.05"))
MAX_WEIGHT = float(os.getenv("EVAL_MAX_WEIGHT", "0.60"))
RETRAIN_THRESHOLD = int(os.getenv("EVAL_RETRAIN_THRESHOLD", "50"))


class EvaluationAgent:
    """
    Personalized vendor evaluation agent.

    Uses Voyage AI fine-tuned embeddings to learn business owner
    preferences and score vendors accordingly.
    """

    def __init__(self):
        self._preferences_cache: dict[str, BusinessPreferences] = {}

    async def get_preferences(self, business_id: str) -> BusinessPreferences:
        """Get or create preferences for a business."""
        if business_id not in self._preferences_cache:
            prefs = await get_business_preferences(business_id)
            if prefs is None:
                # Create default preferences
                prefs = BusinessPreferences(
                    business_id=business_id,
                    weights=PreferenceWeights(),
                )
                await save_business_preferences(prefs)
            self._preferences_cache[business_id] = prefs
        return self._preferences_cache[business_id]

    async def process_feedback(
        self,
        business_id: str,
        feedback: FeedbackRequest
    ) -> PreferenceWeights:
        """
        Process user feedback and update preference weights.

        When user clicks UP on a parameter:
          → Increase weight for that parameter
          → Redistribute weight from other parameters

        When user clicks DOWN on a parameter:
          → Decrease weight for that parameter
          → Redistribute weight to other parameters
        """
        prefs = await self.get_preferences(business_id)
        weights_before = prefs.weights.model_copy()

        # Calculate adjustment
        adjustment = LEARNING_RATE if feedback.direction == FeedbackDirection.UP else -LEARNING_RATE

        # Get current weights as dict
        weights_dict = prefs.weights.model_dump()
        param_key = feedback.parameter.value

        # Apply adjustment to target parameter
        new_value = weights_dict[param_key] + adjustment
        new_value = max(MIN_WEIGHT, min(MAX_WEIGHT, new_value))
        weight_change = new_value - weights_dict[param_key]

        # Redistribute to other parameters
        other_params = [p for p in weights_dict.keys() if p != param_key]
        redistribution = -weight_change / len(other_params)

        # Update weights
        weights_dict[param_key] = new_value
        for p in other_params:
            weights_dict[p] = max(MIN_WEIGHT, min(MAX_WEIGHT, weights_dict[p] + redistribution))

        # Create new weights and normalize
        new_weights = PreferenceWeights(**weights_dict).normalize()

        # Update preferences
        prefs.weights = new_weights
        prefs.total_feedback_count += 1

        # Save feedback record
        feedback_record = FeedbackRecord(
            business_id=business_id,
            vendor_id=feedback.vendor_id,
            parameter=feedback.parameter,
            direction=feedback.direction,
            weights_before=weights_before,
            weights_after=new_weights,
            timestamp=datetime.utcnow().isoformat(),
        )
        await save_feedback(feedback_record)

        # Update cache and persist
        self._preferences_cache[business_id] = prefs
        await save_business_preferences(prefs)

        # Check if retraining needed
        if await should_retrain(business_id, RETRAIN_THRESHOLD):
            logger.info(f"Queueing retraining job for {business_id}")
            await queue_retraining_job(business_id)

        logger.info(
            f"Updated weights for {business_id}: "
            f"{feedback.parameter.value} {feedback.direction.value} → {new_weights}"
        )

        return new_weights

    async def evaluate_vendors(
        self,
        request: EvaluationRequest
    ) -> EvaluationResponse:
        """
        Evaluate and select vendors based on personalized preferences.

        Process:
        1. Get business preferences and weights
        2. Score all vendors using Voyage AI embeddings
        3. Apply weighted parameter scoring
        4. Select optimal combination within budget
        5. Return ranked results with radar chart data
        """
        prefs = await self.get_preferences(request.business_id)

        # Score vendors using Voyage AI + weights
        scored_vendors = await score_vendors_with_voyage(
            business_id=request.business_id,
            model_id=prefs.voyage_model_id,
            weights=prefs.weights,
            ingredients=request.ingredients,
        )

        # Select vendors within budget (greedy by score)
        selected = []
        total_cost = 0.0

        for vendor in scored_vendors:
            vendor_cost = vendor.get("total_price", 0)
            if total_cost + vendor_cost <= request.budget:
                selected.append(VendorEvaluation(
                    vendor_id=vendor["vendor_id"],
                    vendor_name=vendor["vendor_name"],
                    scores=VendorScores(**vendor["scores"]),
                    embedding_score=vendor["embedding_score"],
                    parameter_score=vendor["parameter_score"],
                    final_score=vendor["final_score"],
                    rank=len(selected) + 1,
                ))
                total_cost += vendor_cost

        return EvaluationResponse(
            selected_vendors=selected,
            total_cost=total_cost,
            budget=request.budget,
            savings=request.budget - total_cost,
            weights_used=prefs.weights,
        )

    def get_radar_chart_data(self, evaluation: VendorEvaluation) -> list[dict]:
        """
        Format vendor scores for radar chart visualization.

        Returns data in format expected by Recharts RadarChart.
        """
        return [
            {"parameter": "Quality", "value": evaluation.scores.quality, "fullMark": 100},
            {"parameter": "Affordability", "value": evaluation.scores.affordability, "fullMark": 100},
            {"parameter": "Shipping", "value": evaluation.scores.shipping, "fullMark": 100},
            {"parameter": "Reliability", "value": evaluation.scores.reliability, "fullMark": 100},
        ]


# Global agent instance
_evaluation_agent: Optional[EvaluationAgent] = None


def get_evaluation_agent() -> EvaluationAgent:
    """Get or create the global evaluation agent instance."""
    global _evaluation_agent
    if _evaluation_agent is None:
        _evaluation_agent = EvaluationAgent()
    return _evaluation_agent
```

---

### `tools/__init__.py`

```python
"""Tools for the Evaluation Agent."""

from .voyage_tool import (
    score_vendors_with_voyage,
    create_fine_tuned_model,
    get_voyage_embeddings,
)
from .mongo_tool import (
    get_business_preferences,
    save_business_preferences,
    save_feedback,
    get_feedback_history,
    should_retrain,
    queue_retraining_job,
    get_all_suppliers,
    get_all_negotiations,
)

__all__ = [
    # Voyage AI tools
    "score_vendors_with_voyage",
    "create_fine_tuned_model",
    "get_voyage_embeddings",
    # MongoDB tools
    "get_business_preferences",
    "save_business_preferences",
    "save_feedback",
    "get_feedback_history",
    "should_retrain",
    "queue_retraining_job",
    "get_all_suppliers",
    "get_all_negotiations",
]
```

---

### `tools/voyage_tool.py`

```python
"""Voyage AI tool for the Evaluation Agent."""

import os
import logging
import asyncio
from typing import Optional
from functools import lru_cache

import voyageai

from ..schemas import PreferenceWeights

logger = logging.getLogger(__name__)

# Configuration
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
BASE_MODEL = "voyage-lite-02-instruct"  # Lightweight, <1hr training


@lru_cache(maxsize=1)
def _get_voyage_client() -> voyageai.Client | None:
    """Get or create Voyage AI client (cached)."""
    if not VOYAGE_API_KEY:
        logger.warning("VOYAGE_API_KEY not configured")
        return None
    return voyageai.Client(api_key=VOYAGE_API_KEY)


def _format_vendor_description(vendor: dict) -> str:
    """Format vendor data for embedding."""
    certifications = ", ".join(vendor.get("certifications", [])) or "None"
    return f"""
Vendor: {vendor.get('vendor_name', 'Unknown')}
Quality Score: {vendor.get('quality_score', 0)}/100
Price: ${vendor.get('price_per_unit', 0)}/{vendor.get('unit', 'unit')}
Distance: {vendor.get('distance_miles', 0)} miles
Reliability: {vendor.get('reliability_score', 0)}/100
Certifications: {certifications}
""".strip()


def _format_ideal_query(weights: PreferenceWeights) -> str:
    """Format ideal vendor query based on weights."""
    return f"""
Ideal vendor profile:
- Quality importance: {weights.quality * 100:.0f}%
- Affordability importance: {weights.affordability * 100:.0f}%
- Shipping importance: {weights.shipping * 100:.0f}%
- Reliability importance: {weights.reliability * 100:.0f}%
""".strip()


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    import math
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


async def get_voyage_embeddings(
    texts: list[str],
    model_id: Optional[str] = None,
    input_type: str = "document"
) -> list[list[float]]:
    """
    Get embeddings from Voyage AI.

    Args:
        texts: List of texts to embed
        model_id: Fine-tuned model ID or None for base model
        input_type: "document" or "query"

    Returns:
        List of embedding vectors
    """
    client = _get_voyage_client()
    if not client:
        logger.warning("Voyage client not available, returning stub embeddings")
        return [[0.0] * 1024 for _ in texts]  # Stub embeddings

    model = model_id or BASE_MODEL

    try:
        result = client.embed(
            texts=texts,
            model=model,
            input_type=input_type,
        )
        return result.embeddings
    except Exception as e:
        logger.exception(f"Failed to get Voyage embeddings: {e}")
        return [[0.0] * 1024 for _ in texts]


async def score_vendors_with_voyage(
    business_id: str,
    model_id: Optional[str],
    weights: PreferenceWeights,
    ingredients: list[str],
) -> list[dict]:
    """
    Score vendors using Voyage AI embeddings and preference weights.

    Args:
        business_id: Business identifier
        model_id: Fine-tuned Voyage model ID
        weights: Current preference weights
        ingredients: List of ingredients needed

    Returns:
        List of vendors with scores, sorted by final_score descending
    """
    from .mongo_tool import get_all_suppliers, get_all_negotiations

    # Get suppliers and negotiations from MongoDB
    suppliers = await get_all_suppliers(ingredients)
    negotiations = await get_all_negotiations()

    if not suppliers:
        logger.warning("No suppliers found")
        return []

    # Create negotiation lookup
    negotiation_map = {n["vendor_id"]: n for n in negotiations}

    # Get vendor embeddings
    vendor_texts = [_format_vendor_description(s) for s in suppliers]
    vendor_embeddings = await get_voyage_embeddings(vendor_texts, model_id, "document")

    # Get query embedding for ideal vendor
    query_text = _format_ideal_query(weights)
    query_embeddings = await get_voyage_embeddings([query_text], model_id, "query")
    query_embedding = query_embeddings[0]

    # Score each vendor
    scored_vendors = []

    for i, supplier in enumerate(suppliers):
        vendor_id = supplier.get("_id", supplier.get("vendor_id", f"vendor_{i}"))

        # Get negotiation data if available
        negotiation = negotiation_map.get(vendor_id, {})
        negotiated_price = negotiation.get("negotiated_price", supplier.get("price_per_unit", 0))

        # Calculate embedding similarity
        embedding_score = _cosine_similarity(query_embedding, vendor_embeddings[i])

        # Calculate parameter scores (0-100)
        quality_score = supplier.get("quality_score", 50)

        # Affordability: inverse of price percentile (lower price = higher score)
        price_percentile = supplier.get("price_percentile", 50)
        affordability_score = 100 - price_percentile

        # Shipping: inverse of distance percentile
        distance_percentile = supplier.get("distance_percentile", 50)
        shipping_score = 100 - distance_percentile

        # Reliability from historical data
        reliability_score = supplier.get("reliability_score", 50)

        # Weighted parameter score
        parameter_score = (
            weights.quality * (quality_score / 100) +
            weights.affordability * (affordability_score / 100) +
            weights.shipping * (shipping_score / 100) +
            weights.reliability * (reliability_score / 100)
        )

        # Final score: 60% embedding similarity, 40% parameter score
        final_score = 0.6 * embedding_score + 0.4 * parameter_score

        scored_vendors.append({
            "vendor_id": str(vendor_id),
            "vendor_name": supplier.get("vendor_name", "Unknown"),
            "ingredient": supplier.get("ingredient", ""),
            "scores": {
                "quality": quality_score,
                "affordability": affordability_score,
                "shipping": shipping_score,
                "reliability": reliability_score,
            },
            "embedding_score": embedding_score,
            "parameter_score": parameter_score,
            "final_score": final_score,
            "price_per_unit": negotiated_price,
            "unit": supplier.get("unit", "unit"),
            "total_price": negotiated_price * supplier.get("quantity", 1),
        })

    # Sort by final score descending
    scored_vendors.sort(key=lambda v: v["final_score"], reverse=True)

    return scored_vendors


async def create_fine_tuned_model(
    business_id: str,
    training_data: list[dict],
) -> str:
    """
    Create a fine-tuned Voyage model for a business.

    Training time: ~15-30 minutes with voyage-lite-02-instruct

    Args:
        business_id: Business identifier for model naming
        training_data: List of preference pairs for training

    Returns:
        Fine-tuned model ID
    """
    client = _get_voyage_client()
    if not client:
        logger.warning("Voyage client not available, returning stub model ID")
        return f"stub-model-{business_id}"

    try:
        # Prepare training examples in Voyage format
        examples = []
        for item in training_data:
            examples.append({
                "query": item["query"],
                "positive": item["positive"],
                "negative": item["negative"],
            })

        # Submit fine-tuning job
        fine_tune_job = client.fine_tuning.create(
            model=BASE_MODEL,
            training_data=examples,
            hyperparameters={
                "epochs": 3,
                "learning_rate": 2e-5,
                "batch_size": 16,
            },
            suffix=f"haggl-{business_id}",
        )

        logger.info(f"Started fine-tuning job {fine_tune_job.id} for {business_id}")

        # Poll for completion (with timeout)
        max_wait = 3600  # 1 hour
        wait_time = 0
        poll_interval = 60

        while wait_time < max_wait:
            job_status = client.fine_tuning.retrieve(fine_tune_job.id)

            if job_status.status == "completed":
                logger.info(f"Fine-tuning completed for {business_id}: {job_status.fine_tuned_model}")
                return job_status.fine_tuned_model
            elif job_status.status == "failed":
                logger.error(f"Fine-tuning failed for {business_id}")
                raise Exception("Fine-tuning job failed")

            await asyncio.sleep(poll_interval)
            wait_time += poll_interval

        raise TimeoutError("Fine-tuning job timed out")

    except Exception as e:
        logger.exception(f"Failed to create fine-tuned model: {e}")
        return f"stub-model-{business_id}"
```

---

### `tools/mongo_tool.py`

```python
"""MongoDB tool for the Evaluation Agent."""

import os
import logging
from typing import Optional
from datetime import datetime, timedelta
from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database

from ..schemas import (
    BusinessPreferences,
    FeedbackRecord,
    PreferenceWeights,
)

logger = logging.getLogger(__name__)

# Configuration
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = "haggl"


@lru_cache(maxsize=1)
def _get_database() -> Database | None:
    """Get MongoDB database connection (cached)."""
    if not MONGODB_URI:
        logger.warning("MONGODB_URI not configured")
        return None

    try:
        client = MongoClient(MONGODB_URI)
        return client[DATABASE_NAME]
    except Exception as e:
        logger.exception(f"Failed to connect to MongoDB: {e}")
        return None


async def get_business_preferences(business_id: str) -> Optional[BusinessPreferences]:
    """Get preferences for a business from MongoDB."""
    db = _get_database()
    if not db:
        return None

    try:
        doc = db.preferences.find_one({"business_id": business_id})
        if doc:
            return BusinessPreferences(
                business_id=doc["business_id"],
                weights=PreferenceWeights(**doc["weights"]),
                voyage_model_id=doc.get("voyage_model_id"),
                total_feedback_count=doc.get("total_feedback_count", 0),
                training_status=doc.get("training_status", "pending"),
            )
        return None
    except Exception as e:
        logger.exception(f"Failed to get preferences: {e}")
        return None


async def save_business_preferences(prefs: BusinessPreferences) -> bool:
    """Save or update business preferences in MongoDB."""
    db = _get_database()
    if not db:
        return False

    try:
        db.preferences.update_one(
            {"business_id": prefs.business_id},
            {
                "$set": {
                    "business_id": prefs.business_id,
                    "weights": prefs.weights.model_dump(),
                    "voyage_model_id": prefs.voyage_model_id,
                    "total_feedback_count": prefs.total_feedback_count,
                    "training_status": prefs.training_status,
                    "updated_at": datetime.utcnow(),
                },
                "$setOnInsert": {"created_at": datetime.utcnow()},
            },
            upsert=True,
        )
        return True
    except Exception as e:
        logger.exception(f"Failed to save preferences: {e}")
        return False


async def save_feedback(feedback: FeedbackRecord) -> bool:
    """Save feedback record to MongoDB."""
    db = _get_database()
    if not db:
        return False

    try:
        db.feedback.insert_one({
            "business_id": feedback.business_id,
            "vendor_id": feedback.vendor_id,
            "parameter": feedback.parameter.value,
            "direction": feedback.direction.value,
            "weights_before": feedback.weights_before.model_dump(),
            "weights_after": feedback.weights_after.model_dump(),
            "timestamp": feedback.timestamp,
            "expireAt": datetime.utcnow() + timedelta(days=90),
        })
        return True
    except Exception as e:
        logger.exception(f"Failed to save feedback: {e}")
        return False


async def get_feedback_history(business_id: str, limit: int = 100) -> list[FeedbackRecord]:
    """Get recent feedback history for a business."""
    db = _get_database()
    if not db:
        return []

    try:
        cursor = db.feedback.find({"business_id": business_id}).sort("timestamp", -1).limit(limit)
        records = []
        for doc in cursor:
            records.append(FeedbackRecord(
                business_id=doc["business_id"],
                vendor_id=doc["vendor_id"],
                parameter=doc["parameter"],
                direction=doc["direction"],
                weights_before=PreferenceWeights(**doc["weights_before"]),
                weights_after=PreferenceWeights(**doc["weights_after"]),
                timestamp=doc["timestamp"],
            ))
        return records
    except Exception as e:
        logger.exception(f"Failed to get feedback history: {e}")
        return []


async def should_retrain(business_id: str, threshold: int = 50) -> bool:
    """Check if business has enough feedback to trigger retraining."""
    db = _get_database()
    if not db:
        return False

    try:
        week_ago = datetime.utcnow() - timedelta(days=7)
        count = db.feedback.count_documents({
            "business_id": business_id,
            "timestamp": {"$gte": week_ago.isoformat()},
        })
        return count >= threshold
    except Exception as e:
        logger.exception(f"Failed to check retrain status: {e}")
        return False


async def queue_retraining_job(business_id: str) -> bool:
    """Queue a retraining job for a business."""
    db = _get_database()
    if not db:
        return False

    try:
        db.preferences.update_one(
            {"business_id": business_id},
            {"$set": {"training_status": "pending"}}
        )
        db.training_jobs.insert_one({
            "business_id": business_id,
            "status": "pending",
            "base_model": "voyage-lite-02-instruct",
            "queued_at": datetime.utcnow(),
        })
        logger.info(f"Queued retraining job for {business_id}")
        return True
    except Exception as e:
        logger.exception(f"Failed to queue retraining job: {e}")
        return False


async def get_all_suppliers(ingredients: list[str]) -> list[dict]:
    """Get all suppliers for given ingredients."""
    db = _get_database()
    if not db:
        return []

    try:
        cursor = db.suppliers.find({"ingredient": {"$in": ingredients}})
        return list(cursor)
    except Exception as e:
        logger.exception(f"Failed to get suppliers: {e}")
        return []


async def get_all_negotiations() -> list[dict]:
    """Get all negotiation results."""
    db = _get_database()
    if not db:
        return []

    try:
        cursor = db.negotiations.find({})
        return list(cursor)
    except Exception as e:
        logger.exception(f"Failed to get negotiations: {e}")
        return []
```

---

## Interactive Radar Chart (React)

```tsx
// components/VendorRadarChart.tsx
import React from 'react';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, ResponsiveContainer, Tooltip
} from 'recharts';

interface Props {
  vendorId: string;
  vendorName: string;
  scores: { quality: number; affordability: number; shipping: number; reliability: number };
  onFeedback: (parameter: string, direction: 'up' | 'down') => void;
}

export const VendorRadarChart: React.FC<Props> = ({ vendorId, vendorName, scores, onFeedback }) => {
  const data = [
    { parameter: 'Quality', value: scores.quality, fullMark: 100 },
    { parameter: 'Affordability', value: scores.affordability, fullMark: 100 },
    { parameter: 'Shipping', value: scores.shipping, fullMark: 100 },
    { parameter: 'Reliability', value: scores.reliability, fullMark: 100 },
  ];

  const parameterMap: Record<string, string> = {
    'Quality': 'quality', 'Affordability': 'affordability',
    'Shipping': 'shipping', 'Reliability': 'reliability'
  };

  return (
    <div className="vendor-radar-container">
      <h3>{vendorName}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <RadarChart data={data}>
          <PolarGrid stroke="#e0e0e0" />
          <PolarAngleAxis dataKey="parameter" />
          <PolarRadiusAxis angle={90} domain={[0, 100]} />
          <Radar dataKey="value" stroke="#22c55e" fill="#22c55e" fillOpacity={0.3} />
          <Tooltip />
        </RadarChart>
      </ResponsiveContainer>
      <div className="feedback-controls">
        {data.map((item) => (
          <div key={item.parameter} className="parameter-control">
            <span>{item.parameter}: {item.value}%</span>
            <div>
              <button onClick={() => onFeedback(parameterMap[item.parameter], 'up')}>▲</button>
              <button onClick={() => onFeedback(parameterMap[item.parameter], 'down')}>▼</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

## Environment Variables

```bash
# Voyage AI
VOYAGE_API_KEY=voyage-...

# Evaluation Agent Config
EVAL_LEARNING_RATE=0.05
EVAL_MIN_WEIGHT=0.05
EVAL_MAX_WEIGHT=0.60
EVAL_RETRAIN_THRESHOLD=50
```

---

## MongoDB Collections

### preferences
```javascript
{ business_id: "sweet_dreams", weights: { quality: 0.32, affordability: 0.38, shipping: 0.12, reliability: 0.18 }, voyage_model_id: "...", training_status: "completed" }
```

### feedback
```javascript
{ business_id: "sweet_dreams", vendor_id: "bay_area_foods", parameter: "quality", direction: "up", weights_before: {...}, weights_after: {...}, timestamp: ISODate(), expireAt: ISODate() }
```

---

**Document Status:** Ready for Implementation
**Fine-Tuning Provider:** Voyage AI
**Target Training Time:** <1 hour (typically 15-30 minutes)
