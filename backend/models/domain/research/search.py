# models/domain/research/search.py

from typing import Dict, List, Optional, Any
from uuid import UUID
import httpx  # For API calls
import os
import asyncio

class ResearchSearch:
    """
    Domain model for executing legal-focused searches via Perplexity's Sonar API.
    Handles search initiation, result processing, and conversational follow-ups,
    focusing purely on search execution logic without persistence concerns.
    """
    
    def __init__(self, user_id: UUID, enterprise_id: UUID):
        """
        Initialize with user and enterprise context.
        
        Args:
            user_id: UUID of the user initiating the search
            enterprise_id: UUID of the user's enterprise
        """
        self.user_id = user_id
        self.enterprise_id = enterprise_id
        self._api_key = os.environ.get("PERPLEXITY_API_KEY", "")
        self._api_url = os.environ.get("PERPLEXITY_API_URL", "https://api.perplexity.ai/sonar")

    def validate_query(self, query: str) -> bool:
        """
        Check if the query is valid for processing.
        
        Args:
            query: User's search query
            
        Returns:
            True if valid, False otherwise
        """
        return bool(query and query.strip())

    async def start_search(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Initiate a new search with a legal lens.
        
        Args:
            query: User's search query
            params: Optional search parameters (e.g., jurisdiction) - placeholder for future use
            
        Returns:
            Processed response from Perplexity API
        """
        if not self.validate_query(query):
            return {"error": "Invalid query"}

        legal_prompt = "Interpret through a legal lens, prioritize case law and precedents."
        full_query = f"{legal_prompt} {query}"
        response = await self._call_perplexity_api(full_query)
        
        if "error" in response:
            return response
        
        # Validate response structure
        if not self._validate_api_response(response):
            return {"error": "Invalid API response structure"}
        
        return self.process_results(response)

    async def continue_search(self, follow_up_query: str, thread_id: str) -> Dict[str, Any]:
        """
        Continue an existing search thread with a follow-up query.
        
        Args:
            follow_up_query: Additional query from the user
            thread_id: ID of the existing search thread
            
        Returns:
            Processed response for the follow-up
        """
        if not self.validate_query(follow_up_query):
            return {"error": "Invalid follow-up query"}
        
        response = await self._call_perplexity_api(follow_up_query, thread_id)
        if "error" in response:
            return response
        
        # Validate response structure
        if not self._validate_api_response(response):
            return {"error": "Invalid API response structure"}
        
        return self.process_results(response)

    async def _call_perplexity_api(
        self,
        query: str,
        thread_id: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        Internal helper to call Perplexity's Sonar API with retry logic.
        
        Args:
            query: Search query
            thread_id: Optional thread ID for follow-ups
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries (exponential backoff applied)
            
        Returns:
            Raw API response or error dict
        """
        if not self._api_key:
            return {"error": "API key not configured"}
        
        headers = {"Authorization": f"Bearer {self._api_key}"}
        payload = {"query": query}
        if thread_id:
            payload["thread_id"] = thread_id
        
        retries = 0
        last_error = None
        
        while retries <= max_retries:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self._api_url,
                        json=payload,
                        headers=headers,
                        timeout=10.0
                    )
                    response.raise_for_status()
                    return response.json()
                    
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                # Don't retry auth errors or rate limits
                if status_code in (401, 403, 429):
                    if status_code == 401:
                        return {"error": "API authentication failed. Please check your API key."}
                    elif status_code == 429:
                        return {"error": "Rate limit exceeded. Please try again later."}
                    else:
                        return {"error": f"Authorization error ({status_code}). Please check your credentials."}
                
                # For other HTTP errors, retry with backoff
                last_error = f"HTTP error {status_code}"
                
            except httpx.RequestError as e:
                # Network-related errors are retryable
                last_error = f"Request error: {str(e)}"
            
            # Apply exponential backoff
            if retries < max_retries:
                await asyncio.sleep(retry_delay * (2 ** retries))
            
            retries += 1
        
        # If we've exhausted retries, return the last error
        return {"error": f"API call failed after {max_retries} attempts. Last error: {last_error}"}

    def process_results(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw API response for legal relevance.
        
        Args:
            response: Raw Perplexity API response
            
        Returns:
            Structured response with text and citations
        """
        text = response.get("answer", "")
        citations = self.extract_citations(response)
        return {
            "thread_id": response.get("thread_id", ""),
            "text": text,
            "citations": citations
        }

    def extract_citations(self, response: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract legal citations from API response.
        
        Args:
            response: Raw Perplexity API response
            
        Returns:
            List of citation objects (e.g., {"text": "", "url": ""})
        """
        return response.get("citations", [])

    def _validate_api_response(self, response: Dict[str, Any]) -> bool:
        """
        Validate that the API response has the expected structure.
        
        Args:
            response: Raw API response to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check for required fields
        if not isinstance(response, dict):
            return False
            
        # Verify answer field exists and is a string
        if "answer" not in response or not isinstance(response["answer"], str):
            return False
            
        # Verify thread_id exists
        if "thread_id" not in response or not response["thread_id"]:
            return False
            
        # Verify citations is a list if present
        if "citations" in response and not isinstance(response["citations"], list):
            return False
            
        return True