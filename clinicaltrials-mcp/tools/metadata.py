"""MCP tools for metadata endpoints."""
from fastmcp import Context
from client_api import api_client
import logging

logger = logging.getLogger(__name__)


async def get_field_metadata(ctx: Context) -> dict:
    """
    Get complete study data model field metadata.
    
    Returns detailed information about all available fields including:
    - Field names and types
    - Descriptions
    - Whether fields are indexed or historic-only
    - Nested structure
    
    Returns:
        List of field metadata objects
    """
    await ctx.info("Retrieving field metadata")
    
    try:
        result = await api_client.get_metadata()
        await ctx.info(f"Retrieved metadata for {len(result)} fields")
        return result
            
    except Exception as e:
        await ctx.error(f"Error retrieving field metadata: {str(e)}")
        raise


async def get_search_areas(ctx: Context) -> dict:
    """
    Get search area definitions and their parameters.
    
    Returns information about available search areas:
    - Area names and parameters
    - Search parts and their weights
    - UI labels
    
    Returns:
        Search document list with area definitions
    """
    await ctx.info("Retrieving search areas")
    
    try:
        result = await api_client.get_search_areas()
        await ctx.info("Retrieved search area definitions")
        return result
            
    except Exception as e:
        await ctx.error(f"Error retrieving search areas: {str(e)}")
        raise


async def get_enum_values(ctx: Context) -> dict:
    """
    Get enumeration types and their valid values.
    
    Returns information about enum fields:
    - Enum type names
    - All valid values for each enum
    - Legacy value mappings
    - Field pieces that use each enum
    
    Returns:
        List of enum information objects
    """
    await ctx.info("Retrieving enum values")
    
    try:
        result = await api_client.get_enums()
        await ctx.info(f"Retrieved {len(result)} enum types")
        return result
            
    except Exception as e:
        await ctx.error(f"Error retrieving enum values: {str(e)}")
        raise
