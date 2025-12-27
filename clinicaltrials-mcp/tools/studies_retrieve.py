"""MCP tool for retrieving detailed study information."""
from fastmcp import Context
from typing import Optional, List
from client_api import api_client
import logging

logger = logging.getLogger(__name__)


async def get_study_details(
    ctx: Context,
    nct_id: str,
    fields: Optional[List[str]] = None
) -> dict:
    """
    Retrieve detailed information for a specific clinical trial.
    
    Args:
        nct_id: NCT identifier (e.g., "NCT04852770")
        fields: Specific field paths to return (e.g., ["protocolSection.eligibilityModule.eligibilityCriteria", "protocolSection.identificationModule.briefTitle"]). 
                Common paths: 
                - Eligibility/Inclusion: protocolSection.eligibilityModule.eligibilityCriteria
                - Outcomes: protocolSection.outcomesModule.primaryOutcomes
                - Description: protocolSection.descriptionModule.briefSummary
        
    Returns:
        Complete study information or selected fields as a dictionary.
    """
    await ctx.info(f"Retrieving details for study {nct_id}")
    
    try:
        # Client now manages its own session, no need for'async with' here
        result = await api_client.get_study(
            nct_id=nct_id,
            fields=fields
        )
        
        await ctx.info(f"Successfully retrieved study {nct_id}")
        
        return result
        
    except Exception as e:
        await ctx.error(f"Error retrieving study {nct_id}: {str(e)}")
        raise
