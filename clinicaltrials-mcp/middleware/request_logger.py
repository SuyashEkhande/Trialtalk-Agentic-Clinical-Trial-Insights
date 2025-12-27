"""Request logging middleware for MCP server."""
from fastmcp.server.middleware import Middleware
import logging
import time

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(Middleware):
    """Middleware to log all incoming requests and their response times."""
    
    async def on_tool_call(self, tool_name: str, arguments: dict):
        """Log when a tool is called."""
        logger.info(f"Tool called: {tool_name} with args: {arguments}")
        # Store start time for duration calculation
        self.start_time = time.time()
        
    async def on_tool_result(self, tool_name: str, result: any):
        """Log tool result and execution time."""
        duration = time.time() - getattr(self, 'start_time', time.time())
        logger.info(f"Tool {tool_name} completed in {duration:.3f}s")
        
    async def on_tool_error(self, tool_name: str, error: Exception):
        """Log tool errors."""
        logger.error(f"Tool {tool_name} failed: {str(error)}")
