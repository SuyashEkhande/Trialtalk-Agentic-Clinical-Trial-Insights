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
        self.client: Optional[httpx.AsyncClient] = None
        
    async def __aenter__(self):
        """Context manager entry."""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "TrialTalk-MCP-Server/1.0",
                "Accept": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.client:
            await self.client.aclose()
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make a GET request to the ClinicalTrials.gov API.
        
        Args:
            endpoint: API endpoint path (e.g., '/studies')
            params: Query parameters
            **kwargs: Additional httpx request arguments
            
        Returns:
            JSON response as dictionary
            
        Raises:
            httpx.HTTPError: On HTTP errors
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        try:
            logger.info(f"GET {endpoint} with params: {params}")
            response = await self.client.get(endpoint, params=params, **kwargs)
            response.raise_for_status()
            
            # Handle different response types
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                return response.json()
            else:
                # For CSV or other formats, return raw text
                return {"content": response.text, "content_type": content_type}
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
    
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
        """
        Search clinical trials with various filters.
        
        Args:
            query_cond: Condition/disease query
            query_term: Other terms query
            query_locn: Location query
            query_intr: Intervention/treatment query
            filter_overall_status: List of status filters
            filter_geo: Geographic filter (e.g., "distance(39.0,-77.1,50mi)")
            page_size: Number of results per page
            page_token: Token for next page
            fields: List of fields to return
            **kwargs: Additional query parameters
            
        Returns:
            Paginated study results
        """
        params = {}
        
        # Add query parameters
        if query_cond:
            params["query.cond"] = query_cond
        if query_term:
            params["query.term"] = query_term
        if query_locn:
            params["query.locn"] = query_locn
        if query_intr:
            params["query.intr"] = query_intr
            
        # Add filters
        if filter_overall_status:
            params["filter.overallStatus"] = "|".join(filter_overall_status)
        if filter_geo:
            params["filter.geo"] = filter_geo
            
        # Add pagination
        params["pageSize"] = page_size
        if page_token:
            params["pageToken"] = page_token
            
        # Add field selection
        if fields:
            params["fields"] = "|".join(fields)
            
        # Merge additional parameters
        params.update(kwargs)
        
        return await self.get("/studies", params=params)
    
    async def get_study(
        self,
        nct_id: str,
        fields: Optional[list] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Get detailed information for a single study.
        
        Args:
            nct_id: NCT ID of the study
            fields: List of fields to return
            format: Response format (json, csv, etc.)
            
        Returns:
            Study details
        """
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
        """
        Get field value statistics.
        
        Args:
            types: Field types to filter by (e.g., ['ENUM', 'BOOLEAN'])
            fields: Specific fields to get stats for
            
        Returns:
            Field value statistics
        """
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
