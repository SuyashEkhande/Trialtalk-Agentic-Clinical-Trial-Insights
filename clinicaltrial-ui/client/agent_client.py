"""HTTP client for communicating with the agent API."""
import httpx
import json
from typing import Dict, Any, AsyncIterator
from config import settings


class AgentClient:
    """Client for the Clinical Trial Agent API."""
    
    def __init__(self):
        """Initialize the client."""
        self.base_url = settings.agent_api_url
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def query(self, query_text: str, session_id: str) -> Dict[str, Any]:
        """
        Send a query to the agent.
        
        Args:
            query_text: User's query
            session_id: Session identifier
            
        Returns:
            Agent response
        """
        url = f"{self.base_url}/query"
        payload = {
            "query": query_text,
            "session_id": session_id
        }
        
        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    async def stream_query(
        self,
        query_text: str,
        session_id: str
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream a query response via SSE.
        
        Args:
            query_text: User's query
            session_id: Session identifier
            
        Yields:
            Event dictionaries
        """
        url = f"{self.base_url}/stream/{session_id}"
        params = {"query": query_text}
        
        async with self.client.stream("GET", url, params=params) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        continue
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session information."""
        url = f"{self.base_url}/sessions/{session_id}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()
    
    async def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        url = f"{self.base_url}/sessions/{session_id}"
        response = await self.client.delete(url)
        response.raise_for_status()
    
    async def close(self):
        """Close the client."""
        await self.client.aclose()


# Global client instance
agent_client = AgentClient()
