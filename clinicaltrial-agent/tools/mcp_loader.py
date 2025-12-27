"""MCP tool loader - Logic for connecting to MCP server and loading tools."""
import logging
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from langchain_mcp_adapters.tools import load_mcp_tools
from config import settings

logger = logging.getLogger(__name__)

async def get_mcp_tools(url: str = None):
    """
    Connect to MCP server and load tools using the LangChain adapter.
    
    This function should be used within an AsyncExitStack or similar 
    to keep the connection alive if persistent tools are needed.
    """
    mcp_url = url or settings.mcp_server_url
    if not mcp_url.endswith("/mcp"):
        mcp_url = f"{mcp_url.rstrip('/')}/mcp"
        
    logger.info(f"Connecting to MCP server at {mcp_url}...")
    
    # We return the context managers so the agent can manage the lifecycle
    transport_ctx = streamable_http_client(mcp_url)
    return transport_ctx
