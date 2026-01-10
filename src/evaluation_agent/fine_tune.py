#!/usr/bin/env python3
"""
Fine-tune Voyage AI model for bakery vendor evaluation.

This script:
1. Generates training data from bakery vendor preferences
2. Creates preference embeddings using contrastive learning
3. Saves learned preference vectors for vendor scoring

Usage:
    cd Haggl && python3 -m src.evaluation_agent.fine_tune

The Voyage AI API key is pre-configured. Training completes in <5 minutes.
"""

import os
import sys
import logging
import json
import math
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Voyage AI API Key (provided)
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY", "pa-f-ViMrYCaqJcJqgWmeo8icmSTyZCYid8P3e7rHQFGI3")
BASE_MODEL = "voyage-lite-02-instruct"


def generate_training_data(num_examples: int = 50) -> list[dict]:
    """Generate training examples for fine-tuning."""
    from .tools.exa_tool import generate_training_data as gen_data
    return gen_data(num_examples)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def learn_preference_vectors(training_data: list[dict]) -> dict:
    """
    Learn preference vectors from training data using contrastive embeddings.

    This creates "soft fine-tuning" by computing preference direction vectors
    for each evaluation parameter (quality, affordability, shipping, reliability).

    Args:
        training_data: List of {query, positive, negative} examples

    Returns:
        Dictionary with preference vectors and learned weights
    """
    import voyageai

    client = voyageai.Client(api_key=VOYAGE_API_KEY)

    logger.info(f"Learning preference vectors from {len(training_data)} examples...")

    # Collect texts for batch embedding
    all_texts = []
    text_types = []  # Track type: 'query', 'positive', 'negative'

    for example in training_data:
        all_texts.append(example['query'])
        text_types.append('query')
        all_texts.append(example['positive'])
        text_types.append('positive')
        all_texts.append(example['negative'])
        text_types.append('negative')

    # Get embeddings in batches (Voyage allows up to 128 texts per request)
    logger.info("Computing embeddings...")
    all_embeddings = []
    batch_size = 100

    for i in range(0, len(all_texts), batch_size):
        batch = all_texts[i:i + batch_size]
        result = client.embed(
            texts=batch,
            model=BASE_MODEL,
            input_type="document",
        )
        all_embeddings.extend(result.embeddings)
        logger.info(f"  Processed {min(i + batch_size, len(all_texts))}/{len(all_texts)} texts")

    # Compute preference direction vectors
    # For each triplet, the preference vector = positive_emb - negative_emb
    preference_vectors = {
        'quality': [],
        'affordability': [],
        'shipping': [],
        'reliability': [],
    }

    for i, example in enumerate(training_data):
        query_emb = all_embeddings[i * 3]
        pos_emb = all_embeddings[i * 3 + 1]
        neg_emb = all_embeddings[i * 3 + 2]

        # Compute preference direction
        pref_vec = [p - n for p, n in zip(pos_emb, neg_emb)]

        # Categorize by query type
        query = example['query'].lower()
        if 'quality' in query or 'best' in query or 'premium' in query:
            preference_vectors['quality'].append(pref_vec)
        elif 'cheap' in query or 'budget' in query or 'afford' in query or 'price' in query:
            preference_vectors['affordability'].append(pref_vec)
        elif 'local' in query or 'close' in query or 'near' in query or 'distance' in query:
            preference_vectors['shipping'].append(pref_vec)
        elif 'reliable' in query or 'consistent' in query or 'deliver' in query:
            preference_vectors['reliability'].append(pref_vec)
        else:
            # Balanced - add to all with lower weight
            for key in preference_vectors:
                preference_vectors[key].append([x * 0.25 for x in pref_vec])

    # Average preference vectors for each parameter
    averaged_vectors = {}
    for param, vectors in preference_vectors.items():
        if vectors:
            dim = len(vectors[0])
            avg = [sum(v[d] for v in vectors) / len(vectors) for d in range(dim)]
            # Normalize
            norm = math.sqrt(sum(x * x for x in avg))
            if norm > 0:
                avg = [x / norm for x in avg]
            averaged_vectors[param] = avg
            logger.info(f"  {param}: {len(vectors)} examples, norm={norm:.4f}")
        else:
            averaged_vectors[param] = [0.0] * 1024

    return {
        'preference_vectors': averaged_vectors,
        'base_model': BASE_MODEL,
        'training_examples': len(training_data),
    }


def test_preference_model(learned_model: dict):
    """Test the learned preference model with sample vendors."""
    import voyageai
    from .tools.exa_tool import get_sample_vendors

    client = voyageai.Client(api_key=VOYAGE_API_KEY)
    vendors = get_sample_vendors()

    logger.info("\nTesting learned preference model...")
    logger.info("-" * 60)

    # Get vendor embeddings
    vendor_texts = []
    for v in vendors[:5]:  # Test with first 5 vendors
        text = f"""
Vendor: {v['vendor_name']}
Product: {v['product']}
Quality: {v['quality_score']}/100
Price: ${v['price_per_unit']}/{v['unit']}
Distance: {v['distance_miles']} miles
Reliability: {v['reliability_score']}/100
""".strip()
        vendor_texts.append(text)

    result = client.embed(texts=vendor_texts, model=BASE_MODEL, input_type="document")
    vendor_embeddings = result.embeddings

    # Test scoring with different preference emphasis
    pref_vectors = learned_model['preference_vectors']

    for emphasis in ['quality', 'affordability', 'shipping', 'reliability']:
        logger.info(f"\n{emphasis.upper()}-focused scoring:")
        pref_vec = pref_vectors[emphasis]

        scores = []
        for i, v in enumerate(vendors[:5]):
            score = cosine_similarity(vendor_embeddings[i], pref_vec)
            scores.append((v['vendor_name'], score))

        scores.sort(key=lambda x: x[1], reverse=True)
        for name, score in scores:
            logger.info(f"  {score:.4f} - {name}")


def save_model(learned_model: dict, filename: str = "learned_model.json"):
    """Save learned model to file."""
    filepath = os.path.join(os.path.dirname(__file__), filename)

    # Convert numpy arrays to lists if needed
    save_data = {
        'base_model': learned_model['base_model'],
        'training_examples': learned_model['training_examples'],
        'preference_vectors': {
            k: [float(x) for x in v]
            for k, v in learned_model['preference_vectors'].items()
        },
        'created_at': datetime.now().isoformat(),
    }

    with open(filepath, 'w') as f:
        json.dump(save_data, f)
    logger.info(f"Learned model saved to {filepath}")


def save_training_data(training_data: list[dict], filename: str = "training_data.json"):
    """Save training data to file."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, 'w') as f:
        json.dump(training_data, f, indent=2)
    logger.info(f"Training data saved to {filepath}")


def main():
    """Main fine-tuning pipeline."""
    logger.info("=" * 60)
    logger.info("Haggl Evaluation Agent - Voyage AI Fine-Tuning")
    logger.info("=" * 60)
    logger.info(f"Model: {BASE_MODEL}")
    logger.info(f"API Key: {VOYAGE_API_KEY[:20]}...")

    # Step 1: Generate training data
    logger.info("\n[1/4] Generating training data...")
    training_data = generate_training_data(num_examples=1000)
    logger.info(f"Generated {len(training_data)} training examples")
    save_training_data(training_data)

    # Show sample
    if training_data:
        logger.info("\nSample training example:")
        sample = training_data[0]
        logger.info(f"  Query: {sample['query']}")
        logger.info(f"  Positive: {sample['positive'][:80]}...")

    # Step 2: Learn preference vectors (contrastive fine-tuning)
    logger.info("\n[2/4] Learning preference vectors...")
    learned_model = learn_preference_vectors(training_data)

    # Step 3: Test the model
    logger.info("\n[3/4] Testing learned model...")
    test_preference_model(learned_model)

    # Step 4: Save model
    logger.info("\n[4/4] Saving learned model...")
    save_model(learned_model)

    # Also save config
    config = {
        "model_id": BASE_MODEL,
        "fine_tuned": True,
        "method": "contrastive_preference_learning",
        "training_examples": len(training_data),
        "created_at": datetime.now().isoformat(),
    }
    config_path = os.path.join(os.path.dirname(__file__), "model_config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    logger.info("\n" + "=" * 60)
    logger.info("Fine-tuning complete!")
    logger.info(f"Base Model: {BASE_MODEL}")
    logger.info(f"Training Examples: {len(training_data)}")
    logger.info("Learned preference vectors for: quality, affordability, shipping, reliability")
    logger.info("=" * 60)

    return learned_model


if __name__ == "__main__":
    main()
