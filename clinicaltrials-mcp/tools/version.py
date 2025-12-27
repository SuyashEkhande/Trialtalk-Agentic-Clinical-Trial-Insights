"""MCP tool for version information."""
from fastmcp import Context
from client_api import api_client
import logging

logger = logging.getLogger(__name__)


async def get_api_version(ctx: Context) -> dict:
    """
    Get ClinicalTrials.gov API version and data timestamp.
    
    Returns:
        Dictionary with:
        - apiVersion: Semantic version of the API
        - dataTimestamp: UTC timestamp of last data update
    """
    await ctx.info("Retrieving API version information")
    
    try:
        result = await api_client.get_version()
        await ctx.info(f"API Version: {result.get('apiVersion')}, Data: {result.get('dataTimestamp')}")
        return result
            
    except Exception as e:
        await ctx.error(f"Error retrieving version info: {str(e)}")
        raise
