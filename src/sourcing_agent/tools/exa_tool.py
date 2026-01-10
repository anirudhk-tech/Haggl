"""Exa.ai web search integration for the Sourcing Agent."""

import os
import logging
import httpx
from typing import Optional
from dotenv import load_dotenv

from ..schemas import IngredientRequest, UserLocation, ExaSearchResult

load_dotenv()
logger = logging.getLogger(__name__)

# Exa.ai configuration
EXA_API_KEY = os.getenv("EXA_API_KEY")
EXA_BASE_URL = "https://api.exa.ai"


def build_vendor_search_queries(
    ingredient: IngredientRequest,
    location: UserLocation,
) -> list[str]:
    """
    Build multiple query variations for better coverage.

    Args:
        ingredient: The ingredient being sourced
        location: User's location for regional search

    Returns:
        List of search queries to try
    """
    queries = []

    # Base ingredient name (with quality if specified)
    ingredient_str = f"{ingredient.quality} {ingredient.name}" if ingredient.quality else ingredient.name
    location_str = f"{location.city} {location.state}"

    # Query 1: Generic wholesale supplier search
    queries.append(f"wholesale {ingredient_str} supplier near {location_str}")

    # Query 2: B2B focused with pricing terms
    queries.append(f"B2B {ingredient.name} vendor bulk pricing MOQ {location.state}")

    # Query 3: Food service distributor focus
    queries.append(f"{ingredient_str} food service distributor {location.city}")

    return queries


async def search_vendors(
    query: str,
    num_results: int = 10,
    use_autoprompt: bool = True,
    include_text: bool = True,
    include_highlights: bool = True,
) -> list[ExaSearchResult]:
    """
    Search for vendors using Exa.ai semantic/neural search.

    Args:
        query: Search query (e.g., "wholesale flour supplier San Francisco")
        num_results: Number of results to return
        use_autoprompt: Let Exa optimize the query
        include_text: Include full page text content
        include_highlights: Include relevant highlights

    Returns:
        List of ExaSearchResult objects
    """
    if not EXA_API_KEY:
        logger.error("EXA_API_KEY not set")
        return []

    headers = {
        "Content-Type": "application/json",
        "x-api-key": EXA_API_KEY,
    }

    # Build the search request
    payload = {
        "query": query,
        "numResults": num_results,
        "useAutoprompt": use_autoprompt,
        "type": "auto",  # Let Exa decide between neural and keyword
    }

    # Add content options if requested
    contents_options = {}
    if include_text:
        contents_options["text"] = {"maxCharacters": 5000}
    if include_highlights:
        contents_options["highlights"] = {"numSentences": 3}

    if contents_options:
        payload["contents"] = contents_options

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{EXA_BASE_URL}/search",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("results", []):
                result = ExaSearchResult(
                    url=item.get("url", ""),
                    title=item.get("title", ""),
                    text=item.get("text"),
                    highlights=item.get("highlights", []),
                    published_date=item.get("publishedDate"),
                    score=item.get("score"),
                )
                results.append(result)

            logger.info(f"Exa search returned {len(results)} results for query: {query[:50]}...")
            return results

    except httpx.HTTPStatusError as e:
        logger.error(f"Exa API error: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Error searching Exa: {e}")
        return []


async def get_page_contents(
    urls: list[str],
    max_characters: int = 5000,
) -> list[dict]:
    """
    Get full content from URLs using Exa's /contents endpoint.

    Args:
        urls: List of URLs to fetch content from
        max_characters: Maximum characters per page

    Returns:
        List of dicts with url and text content
    """
    if not EXA_API_KEY:
        logger.error("EXA_API_KEY not set")
        return []

    if not urls:
        return []

    headers = {
        "Content-Type": "application/json",
        "x-api-key": EXA_API_KEY,
    }

    payload = {
        "ids": urls,
        "text": {"maxCharacters": max_characters},
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{EXA_BASE_URL}/contents",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            contents = []
            for item in data.get("results", []):
                contents.append({
                    "url": item.get("url", ""),
                    "title": item.get("title", ""),
                    "text": item.get("text", ""),
                })

            logger.info(f"Fetched content for {len(contents)} URLs")
            return contents

    except httpx.HTTPStatusError as e:
        logger.error(f"Exa contents API error: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Error fetching contents: {e}")
        return []


async def search_with_multiple_queries(
    ingredient: IngredientRequest,
    location: UserLocation,
    results_per_query: int = 5,
) -> list[ExaSearchResult]:
    """
    Search using multiple query variations and deduplicate results.

    Args:
        ingredient: The ingredient being sourced
        location: User's location
        results_per_query: Number of results per query

    Returns:
        Deduplicated list of search results
    """
    queries = build_vendor_search_queries(ingredient, location)
    all_results: list[ExaSearchResult] = []
    seen_urls: set[str] = set()

    for query in queries:
        results = await search_vendors(query, num_results=results_per_query)
        for result in results:
            if result.url not in seen_urls:
                all_results.append(result)
                seen_urls.add(result.url)

    logger.info(f"Multi-query search found {len(all_results)} unique results for {ingredient.name}")
    return all_results
