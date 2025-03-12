# models/domain/research/search.py

from typing import Dict, List, Optional, Any
from uuid import UUID
import httpx  # For API calls
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

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
        self._api_url = "https://api.perplexity.ai/chat/completions"

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

        # Create messages array with system prompt and user query
        messages = [
            {
                "role": "system",
                "content": "Provide a concise, accurate, and legally relevant response to the query, prioritizing authoritative sources such as case law, statutes, and reputable legal commentary, tailored to the needs of a practicing lawyer."
            },
            {
                "role": "user",
                "content": query
            }
        ]
        
        # Set up API payload
        payload = {
            "model": "sonar-pro",  # Using Sonar Pro for legal research
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        # Add any additional parameters from params
        if params:
            # Only add supported parameters
            for key in ["temperature", "max_tokens", "top_p", "top_k"]:
                if key in params:
                    payload[key] = params[key]
        
        logger.debug(f"Starting search with query: {query[:100]}...")
        response = await self._call_perplexity_api(payload)
        
        if "error" in response:
            return response
        
        # Validate response structure
        if not self._validate_api_response(response):
            return {"error": "Invalid API response structure"}
        
        return self.process_results(response)

    async def continue_search(
        self, 
        follow_up_query: str, 
        previous_messages: List[Dict[str, str]] = None,
        thread_id: str = None  # Kept for backward compatibility
    ) -> Dict[str, Any]:
        """
        Continue an existing search thread with a follow-up query.
        
        Args:
            follow_up_query: Additional query from the user
            previous_messages: List of previous messages in the conversation
            thread_id: ID of the existing search thread (kept for compatibility)
            
        Returns:
            Processed response for the follow-up
        """
        if not self.validate_query(follow_up_query):
            return {"error": "Invalid follow-up query"}
        
        # Use provided previous messages or start with a fresh conversation
        messages = previous_messages or []
        
        # If no previous messages, add a system message
        if not messages:
            messages.append({
                "role": "system",
                "content": "Provide a concise, accurate, and legally relevant response to the follow-up query, prioritizing authoritative sources such as case law, statutes, and reputable legal commentary, tailored to the needs of a practicing lawyer."
            })
        
        # Add the user's follow-up query
        messages.append({
            "role": "user",
            "content": follow_up_query
        })
        
        payload = {
            "model": "sonar-pro",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        logger.debug(f"Continuing search with follow-up query: {follow_up_query[:100]}...")
        response = await self._call_perplexity_api(payload)
        
        if "error" in response:
            return response
        
        # Validate response structure
        if not self._validate_api_response(response):
            return {"error": "Invalid API response structure"}
        
        return self.process_results(response)

    async def _call_perplexity_api(
        self,
        payload: Dict[str, Any],
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        Internal helper to call Perplexity's Chat Completions API with retry logic.
        
        Args:
            payload: Request payload for the API
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries (exponential backoff applied)
            
        Returns:
            Raw API response or error dict
        """
        if not self._api_key:
            logger.error("API key not configured")
            return {"error": "API key not configured"}
        
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }
        
        retries = 0
        last_error = None
        
        while retries <= max_retries:
            try:
                async with httpx.AsyncClient() as client:
                    logger.debug(f"Calling Perplexity API with payload structure: {list(payload.keys())}")
                    response = await client.post(
                        self._api_url,
                        json=payload,
                        headers=headers,
                        timeout=10.0
                    )
                    response.raise_for_status()
                    response_json = response.json()
                    logger.debug(f"Received response with structure: {list(response_json.keys())}")
                    return response_json
                    
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                error_content = e.response.text
                if status_code == 401:
                    logger.error(f"API authentication failed: {error_content}")
                    return {"error": "API authentication failed. Please check your API key."}
                elif status_code == 429:
                    logger.error(f"Rate limit exceeded: {error_content}")
                    return {"error": "Rate limit exceeded. Please try again later."}
                elif status_code in (403,):
                    logger.error(f"Authorization error ({status_code}): {error_content}")
                    return {"error": f"Authorization error ({status_code}). Please check your credentials."}
                else:
                    logger.warning(f"HTTP error {status_code}: {error_content}. Retrying...")
                    last_error = f"HTTP error {status_code}"
                
            except httpx.RequestError as e:
                logger.warning(f"Request error: {str(e)}. Retrying...")
                last_error = f"Request error: {str(e)}"
            
            # Apply exponential backoff
            if retries < max_retries:
                await asyncio.sleep(retry_delay * (2 ** retries))
            
            retries += 1
        
        # If we've exhausted retries, return the last error
        logger.error(f"API call failed after {max_retries} attempts. Last error: {last_error}")
        return {"error": f"API call failed after {max_retries} attempts. Last error: {last_error}"}

    def process_results(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw API response for legal relevance.
        
        Args:
            response: Raw Perplexity API response
            
        Returns:
            Structured response with text and citations
        """
        # Extract text from the first choice's message content
        text = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Extract citations if available
        citations = self.extract_citations(response)
        
        # Use the response ID as thread_id for consistency
        thread_id = response.get("id", "")
        
        return {
            "thread_id": thread_id,
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
        # Extract citations from the response
        raw_citations = response.get("citations", [])
        
        # Format citations as objects with text and url
        formatted_citations = []
        for i, citation in enumerate(raw_citations):
            if isinstance(citation, str):
                formatted_citations.append({
                    "text": f"Source {i+1}",
                    "url": citation
                })
            elif isinstance(citation, dict):
                # If citations are already formatted as objects, use them directly
                formatted_citations.append(citation)
        
        return formatted_citations

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
            
        # Verify choices array exists
        if "choices" not in response or not isinstance(response["choices"], list) or not response["choices"]:
            return False
            
        # Verify first choice has a message with content
        first_choice = response["choices"][0]
        if not isinstance(first_choice, dict) or "message" not in first_choice:
            return False
            
        message = first_choice["message"]
        if not isinstance(message, dict) or "content" not in message or not isinstance(message["content"], str):
            return False
            
        # Verify id exists
        if "id" not in response or not response["id"]:
            return False
            
        # Verify citations is a list if present
        if "citations" in response and not isinstance(response["citations"], list):
            return False
            
        return True