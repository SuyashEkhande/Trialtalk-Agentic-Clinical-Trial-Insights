"""ClinicalTrials.gov MCP Server - Main Entry Point."""
import logging
import sys
from fastmcp import FastMCP
from config import settings

# Import tools
from tools.studies_search import search_clinical_trials
from tools.studies_retrieve import get_study_details
from tools.metadata import get_field_metadata, get_search_areas, get_enum_values
from tools.statistics import get_study_size_stats, get_field_value_stats, get_list_field_sizes
from tools.version import get_api_version

# Import resources
from resources.openapi_spec import get_openapi_spec, RESOURCE_URI as OPENAPI_URI, RESOURCE_NAME as OPENAPI_NAME, RESOURCE_DESCRIPTION as OPENAPI_DESC
from resources.usage_examples import get_usage_examples, RESOURCE_URI as EXAMPLES_URI, RESOURCE_NAME as EXAMPLES_NAME, RESOURCE_DESCRIPTION as EXAMPLES_DESC

# Import prompts
from prompts.query_builder import PROMPTS, build_condition_query_prompt, build_location_query_prompt, build_advanced_filter_prompt

# Import middleware
from middleware.request_logger import RequestLoggingMiddleware
from middleware.rate_limiter import RateLimitMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(settings.mcp_server_name)

# Add middleware
logger.info("Adding middleware...")
mcp.add_middleware(RequestLoggingMiddleware())
mcp.add_middleware(RateLimitMiddleware())

# Register tools
logger.info("Registering tools...")
mcp.tool(search_clinical_trials)
mcp.tool(get_study_details)
mcp.tool(get_field_metadata)
mcp.tool(get_search_areas)
mcp.tool(get_enum_values)
mcp.tool(get_study_size_stats)
mcp.tool(get_field_value_stats)
mcp.tool(get_list_field_sizes)
mcp.tool(get_api_version)

# Register resources
logger.info("Registering resources...")

@mcp.resource(OPENAPI_URI)
def openapi_resource() -> str:
    """OpenAPI specification resource."""
    return get_openapi_spec()

@mcp.resource(EXAMPLES_URI)
def examples_resource() -> str:
    """Usage examples resource."""
    return get_usage_examples()

# Register prompts
logger.info("Registering prompts...")

@mcp.prompt()
def build_condition_query(user_input: str) -> str:
    """Prompt for building condition queries."""
    return build_condition_query_prompt(user_input)

@mcp.prompt()
def build_location_query(location: str) -> str:
    """Prompt for building location queries."""
    return build_location_query_prompt(location)

@mcp.prompt()
def build_advanced_filter(criteria: str) -> str:
    """Prompt for building advanced filters."""
    # Convert string to dict if needed
    import json
    try:
        criteria_dict = json.loads(criteria) if isinstance(criteria, str) else criteria
    except:
        criteria_dict = {"raw": criteria}
    return build_advanced_filter_prompt(criteria_dict)

# Health check endpoint
@mcp.tool()
async def health_check() -> dict:
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "server": settings.mcp_server_name,
        "version": "1.0.0"
    }


def main():
    """Main entry point for the MCP server."""
    logger.info(f"Starting {settings.mcp_server_name}...")
    logger.info(f"Server configuration:")
    logger.info(f"  Host: {settings.mcp_server_host}")
    logger.info(f"  Port: {settings.mcp_server_port}")
    logger.info(f"  API Base: {settings.clinical_trials_api_base_url}")
    logger.info(f"  Rate Limiting: {'Enabled' if settings.rate_limit_enabled else 'Disabled'}")
    
    # Run with HTTP transport
    mcp.run(
        transport="http",
        host=settings.mcp_server_host,
        port=settings.mcp_server_port
    )


if __name__ == "__main__":
    main()
