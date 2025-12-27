"""HTTP client for ClinicalTrials.gov API with retry logic and error handling."""
import httpx
import logging
from typing import Any, Dict, Optional
from config import settings

logger = logging.getLogger(__name__)


class ClinicalTrialsAPIClient:
    """Async HTTP client for ClinicalTrials.gov API."""
    
    def __init__(self):
        """Initialize the API client."""
        self.base_url = settings.clinical_trials_api_base_url
        self.timeout = httpx.Timeout(settings.http_timeout_seconds)
        self.limits = httpx.Limits(
            max_keepalive_connections=5,
            max_connections=20,
            keepalive_expiry=30.0
        )
        self._client: Optional[httpx.AsyncClient] = None
        
    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create the internal httpx client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                limits=self.limits,
                follow_redirects=True,
                http2=False,  # Disable HTTP/2 to avoid ReadError/StreamDrops
                http1=True,   # Explicitly use HTTP/1.1
                headers={
                    "User-Agent": "TrialTalk-MCP-Server/1.0",
                    "Accept": "application/json",
                    "Connection": "keep-alive"
                }
            )
        return self._client

    async def aclose(self):
        """Close the internal client if it exists."""
        if self._client:
            try:
                await self._client.aclose()
            except Exception as e:
                logger.error(f"Error closing client: {e}")
            self._client = None
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        retries: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a GET request to the ClinicalTrials.gov API with retries.
        
        Args:
            endpoint: API endpoint path (e.g., '/studies')
            params: Query parameters
            retries: Number of retry attempts for protocol errors
            **kwargs: Additional httpx request arguments
            
        Returns:
            JSON response as dictionary
        """
        last_error = None
        
        for attempt in range(retries):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt + 1}/{retries} for {endpoint}")
                
                response = await self.client.get(endpoint, params=params, **kwargs)
                response.raise_for_status()
                
                # Handle different response types
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    return response.json()
                else:
                    return {"content": response.text, "content_type": content_type}
                    
            except (httpx.ReadError, httpx.RemoteProtocolError, httpx.WriteError) as e:
                last_error = e
                logger.warning(f"Protocol error '{type(e).__name__}' on attempt {attempt + 1}: {e}")
                # Force client recreate on next attempt
                await self.aclose()
                if attempt == retries - 1:
                    raise
                continue
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code} for {endpoint}: {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Request error for {endpoint}: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error for {endpoint}: {str(e)}")
                raise
        
        if last_error:
            raise last_error
    
    async def search_studies(
        self,
        query_cond: Optional[str] = None,
        query_term: Optional[str] = None,
        query_locn: Optional[str] = None,
        query_intr: Optional[str] = None,
        filter_overall_status: Optional[list] = None,
        filter_geo: Optional[str] = None,
        page_size: int = 10,
        page_token: Optional[str] = None,
        fields: Optional[list] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Search clinical trials with various filters."""
        params = {}
        
        if query_cond:
            params["query.cond"] = query_cond
        if query_term:
            params["query.term"] = query_term
        if query_locn:
            params["query.locn"] = query_locn
        if query_intr:
            params["query.intr"] = query_intr
            
        if filter_overall_status:
            params["filter.overallStatus"] = "|".join(filter_overall_status)
        if filter_geo:
            params["filter.geo"] = filter_geo
            
        params["pageSize"] = page_size
        if page_token:
            params["pageToken"] = page_token
            
        if fields:
            params["fields"] = "|".join(fields)
            
        params.update(kwargs)
        
        return await self.get("/studies", params=params)
    
    async def get_study(
        self,
        nct_id: str,
        fields: Optional[list] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """Get detailed information for a single study."""
        params = {"format": format}
        if fields:
            params["fields"] = "|".join(fields)
            
        return await self.get(f"/studies/{nct_id}", params=params)
    
    async def get_metadata(self) -> Dict[str, Any]:
        """Get study data model field metadata."""
        return await self.get("/studies/metadata")
    
    async def get_search_areas(self) -> Dict[str, Any]:
        """Get search area definitions."""
        return await self.get("/studies/search-areas")
    
    async def get_enums(self) -> Dict[str, Any]:
        """Get enumeration types and values."""
        return await self.get("/studies/enums")
    
    async def get_size_stats(self) -> Dict[str, Any]:
        """Get study size statistics."""
        return await self.get("/stats/size")
    
    async def get_field_value_stats(
        self,
        types: Optional[list] = None,
        fields: Optional[list] = None
    ) -> Dict[str, Any]:
        """Get field value statistics."""
        params = {}
        if types:
            params["types"] = "|".join(types)
        if fields:
            params["fields"] = "|".join(fields)
            
        return await self.get("/stats/field/values", params=params)
    
    async def get_version(self) -> Dict[str, Any]:
        """Get API and data version information."""
        return await self.get("/version")


# Singleton instance for reuse
api_client = ClinicalTrialsAPIClient()
