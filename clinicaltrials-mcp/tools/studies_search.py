"""MCP tool for searching clinical trials."""
from fastmcp import Context
from typing import Optional, List
from client_api import api_client
import logging

logger = logging.getLogger(__name__)


async def search_clinical_trials(
    ctx: Context,
    condition: Optional[str] = None,
    intervention: Optional[str] = None,
    location: Optional[str] = None,
    status: Optional[List[str]] = None,
    other_terms: Optional[str] = None,
    page_size: int = 10,
    page_token: Optional[str] = None
) -> dict:
    """
    Search for clinical trials based on various criteria.
    
    Args:
        condition: Disease or condition (e.g., "diabetes", "lung cancer")
        intervention: Treatment or intervention (e.g., "pembrolizumab", "surgery")
        location: Geographic location (e.g., "California", "United States")
        status: Trial status (e.g., ["RECRUITING", "ACTIVE_NOT_RECRUITING"])
        other_terms: Additional search terms
        page_size: Number of results per page (1-1000, default 10)
        page_token: Token for retrieving next page
        
    Returns:
        Dictionary with studies, total count, and next page token
    """
    await ctx.info(f"Searching clinical trials with condition='{condition}', intervention='{intervention}'")
    
    try:
        result = await api_client.search_studies(
            query_cond=condition,
            query_intr=intervention,
            query_locn=location,
            query_term=other_terms,
            filter_overall_status=status,
            page_size=page_size,
            page_token=page_token,
            countTotal=True if not page_token else False  # Only count on first page
        )
        
        study_count = len(result.get("studies", []))
        total_count = result.get("totalCount", "unknown")
        
        await ctx.info(f"Found {study_count} studies (total: {total_count})")
        
        return {
            "studies": result.get("studies", []),
            "totalCount": total_count,
            "nextPageToken": result.get("nextPageToken"),
            "hasMore": "nextPageToken" in result
        }
            
    except Exception as e:
        await ctx.error(f"Error searching clinical trials: {str(e)}")
        raise
