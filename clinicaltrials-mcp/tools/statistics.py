"""MCP tools for statistics endpoints."""
from fastmcp import Context
from typing import Optional, List
from client_api import api_client
import logging

logger = logging.getLogger(__name__)


async def get_study_size_stats(ctx: Context) -> dict:
    """
    Get statistics about study JSON sizes.
    
    Returns:
        Statistics including:
        - Average size in bytes
        - Percentile distribution
        - Size ranges with study counts
        - Largest studies
    """
    await ctx.info("Retrieving study size statistics")
    
    try:
        result = await api_client.get_size_stats()
        await ctx.info("Retrieved study size statistics")
        return result
            
    except Exception as e:
        await ctx.error(f"Error retrieving size stats: {str(e)}")
        raise


async def get_field_value_stats(
    ctx: Context,
    field_types: Optional[List[str]] = None,
    fields: Optional[List[str]] = None
) -> dict:
    """
    Get value statistics for study fields.
    
    Args:
        field_types: Filter by field types (e.g., ["ENUM", "BOOLEAN", "STRING"])
        fields: Specific field names to get stats for
        
    Returns:
        Statistics including:
        - Field value distributions
        - Top values with counts
        - Missing value counts
        - Unique value counts
    """
    await ctx.info(f"Retrieving field value statistics for types={field_types}, fields={fields}")
    
    try:
        result = await api_client.get_field_value_stats(
            types=field_types,
            fields=fields
        )
        await ctx.info(f"Retrieved statistics for {len(result)} fields")
        return result
            
    except Exception as e:
        await ctx.error(f"Error retrieving field value stats: {str(e)}")
        raise


async def get_list_field_sizes(
    ctx: Context,
    fields: Optional[List[str]] = None
) -> dict:
    """
    Get size statistics for array/list fields.
    
    Args:
        fields: Specific field names to get size stats for
        
    Returns:
        Statistics including:
        - Min/max array sizes
        - Most common sizes
        - Unique size count
    """
    await ctx.info(f"Retrieving list field size statistics for fields={fields}")
    
    try:
        # This endpoint uses the same stats endpoint with different parameters
        result = await api_client.get("/stats/field/sizes", params={"fields": "|".join(fields)} if fields else None)
        await ctx.info("Retrieved list field size statistics")
        return result
            
    except Exception as e:
        await ctx.error(f"Error retrieving list field sizes: {str(e)}")
        raise
