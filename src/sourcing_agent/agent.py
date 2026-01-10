"""
Sourcing Agent - Finds vendors using Exa.ai web search and extracts structured data.

The Sourcing Agent is responsible for:
1. Searching for vendors using Exa.ai semantic search
2. Extracting structured vendor data (name, phone, pricing, MOQ, etc.)
3. Estimating shipping distances
4. Storing results to local JSON storage

State Machine:
    IDLE -> SEARCHING -> EXTRACTING -> COMPLETED
                      -> FAILED (from any state)
"""

import asyncio
import logging
import time
from typing import Optional

from .schemas import (
    SourcingState,
    SourcingRequest,
    SourcingResponse,
    VendorResult,
    IngredientRequest,
    UserLocation,
    ExtractedVendor,
)
from .tools.exa_tool import search_with_multiple_queries
from .tools.extractor import extract_vendor_info
from .tools.storage import add_vendor_results

logger = logging.getLogger(__name__)


class SourcingAgent:
    """
    The Sourcing Agent finds vendors using Exa.ai web search
    and extracts structured data for the evaluation agent.

    States:
        IDLE -> SEARCHING -> EXTRACTING -> COMPLETED
                          -> FAILED (from any state)
    """

    def __init__(self):
        """Initialize the sourcing agent."""
        self.state = SourcingState.IDLE
        self.error: Optional[str] = None
        self._search_cache: dict[str, list] = {}  # For idempotency

    def _transition(self, new_state: SourcingState) -> None:
        """
        Transition to a new state with logging.

        Args:
            new_state: The state to transition to
        """
        old_state = self.state
        self.state = new_state
        logger.info(f"SourcingAgent state transition: {old_state} -> {new_state}")

    async def source_vendors(self, request: SourcingRequest) -> SourcingResponse:
        """
        Main entry point: find vendors for all requested ingredients.

        Process:
        1. Transition to SEARCHING
        2. For each ingredient, run Exa.ai search with multiple queries
        3. Transition to EXTRACTING
        4. For each search result, extract structured data using Claude
        5. Calculate distance from user location
        6. Save results to local storage
        7. Transition to COMPLETED
        8. Return aggregated results

        Args:
            request: The sourcing request containing ingredients and location

        Returns:
            SourcingResponse with all found vendors
        """
        start_time = time.time()
        results: list[VendorResult] = []
        errors: list[str] = []

        try:
            # Reset state
            self.error = None
            self._transition(SourcingState.SEARCHING)

            # Search for each ingredient
            for ingredient in request.ingredients:
                try:
                    ingredient_result = await self._process_ingredient(
                        ingredient=ingredient,
                        location=request.location,
                        max_results=request.max_results_per_ingredient,
                    )
                    results.append(ingredient_result)
                except Exception as e:
                    error_msg = f"Error processing {ingredient.name}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            # Save results to local storage
            if results:
                add_vendor_results(
                    request_id=request.request_id,
                    results=[r.model_dump() for r in results],
                    location=request.location.model_dump(),
                )

            self._transition(SourcingState.COMPLETED)

            total_vendors = sum(r.total_found for r in results)
            elapsed = time.time() - start_time

            return SourcingResponse(
                request_id=request.request_id,
                status=self.state,
                results=results,
                total_vendors_found=total_vendors,
                elapsed_seconds=elapsed,
                errors=errors,
            )

        except Exception as e:
            self.error = str(e)
            self._transition(SourcingState.FAILED)
            logger.error(f"Sourcing failed: {e}")

            return SourcingResponse(
                request_id=request.request_id,
                status=self.state,
                results=results,
                total_vendors_found=0,
                elapsed_seconds=time.time() - start_time,
                errors=[str(e)],
            )

    async def _process_ingredient(
        self,
        ingredient: IngredientRequest,
        location: UserLocation,
        max_results: int,
    ) -> VendorResult:
        """
        Process a single ingredient: search and extract vendor data.

        Args:
            ingredient: The ingredient to search for
            location: User's location
            max_results: Maximum number of results

        Returns:
            VendorResult with extracted vendors
        """
        extraction_start = time.time()

        # Check cache first
        cache_key = f"{ingredient.name}:{location.city}:{location.state}"
        if cache_key in self._search_cache:
            logger.info(f"Using cached results for {ingredient.name}")
            search_results = self._search_cache[cache_key]
        else:
            # Search using multiple query strategies
            search_results = await search_with_multiple_queries(
                ingredient=ingredient,
                location=location,
                results_per_query=max_results // 3 + 1,  # Distribute across queries
            )
            self._search_cache[cache_key] = search_results

        if not search_results:
            logger.warning(f"No search results for {ingredient.name}")
            return VendorResult(
                ingredient=ingredient.name,
                vendors=[],
                search_queries=[],
                total_found=0,
                extraction_time_seconds=time.time() - extraction_start,
            )

        # Transition to extracting
        self._transition(SourcingState.EXTRACTING)

        # Extract vendor data from each search result (with concurrency limit)
        vendors: list[ExtractedVendor] = []
        semaphore = asyncio.Semaphore(3)  # Limit concurrent extractions

        async def extract_with_semaphore(result):
            async with semaphore:
                return await extract_vendor_info(
                    search_result=result,
                    ingredient_name=ingredient.name,
                    user_location=location,
                )

        extraction_tasks = [
            extract_with_semaphore(result)
            for result in search_results[:max_results]
        ]

        extracted = await asyncio.gather(*extraction_tasks, return_exceptions=True)

        for vendor in extracted:
            if isinstance(vendor, ExtractedVendor):
                vendors.append(vendor)
            elif isinstance(vendor, Exception):
                logger.warning(f"Extraction failed: {vendor}")

        extraction_time = time.time() - extraction_start
        logger.info(f"Extracted {len(vendors)} vendors for {ingredient.name} in {extraction_time:.2f}s")

        return VendorResult(
            ingredient=ingredient.name,
            vendors=vendors,
            search_queries=[],  # Queries already logged
            total_found=len(vendors),
            extraction_time_seconds=extraction_time,
        )

    def get_state(self) -> SourcingState:
        """Get the current agent state."""
        return self.state

    def clear_cache(self) -> None:
        """Clear the search cache (for testing)."""
        self._search_cache.clear()
        self._transition(SourcingState.IDLE)
        logger.info("Cleared search cache")


# =============================================================================
# Singleton Pattern
# =============================================================================

_agent: Optional[SourcingAgent] = None


def get_sourcing_agent() -> SourcingAgent:
    """
    Get or create the global agent instance.

    Returns:
        The singleton SourcingAgent instance
    """
    global _agent
    if _agent is None:
        _agent = SourcingAgent()
    return _agent
