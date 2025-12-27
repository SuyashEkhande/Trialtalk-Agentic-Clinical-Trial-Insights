"""Rate limiting middleware for MCP server."""
from fastmcp.server.middleware import Middleware
from collections import defaultdict
import time
import logging
from config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(Middleware):
    """Simple in-memory rate limiting middleware."""
    
    def __init__(self):
        """Initialize rate limiter."""
        super().__init__()
        self.requests = defaultdict(list)
        self.limit = settings.rate_limit_requests_per_minute
        self.window = 60  # seconds
        
    async def on_tool_call(self, tool_name: str, arguments: dict):
        """Check rate limit before tool execution."""
        if not settings.rate_limit_enabled:
            return
            
        now = time.time()
        client_id = "global"  # In production, extract from request context
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.limit:
            logger.warning(f"Rate limit exceeded for {client_id}")
            raise Exception(f"Rate limit exceeded: {self.limit} requests per minute")
            
        # Record request
        self.requests[client_id].append(now)
