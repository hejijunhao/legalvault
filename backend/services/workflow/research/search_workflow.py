# services/workflow/research/search_workflow.py

from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
import logging
import os
import httpx
import asyncio

from models.domain.research.search import ResearchSearch
from models.domain.research.search_operations import ResearchOperations
from models.domain.research.search_message_operations import SearchMessageOperations

logger = logging.getLogger(__name__)

class ResearchSearchWorkflow:
    """
    Workflow orchestrator for research search functionality.
    
    This class coordinates the interaction between domain models and external services
    (like Perplexity's Sonar API) while maintaining domain-driven design principles.
    It delegates database operations to the appropriate domain operation classes.
    """
    
    def __init__(self):
        """
        Initialize the workflow orchestrator with API configuration.
        """
        self._api_key = api_key or os.environ.get("PERPLEXITY_API_KEY", "")
        if not self._api_key:
            logger.warning("Perplexity API key not configured. API calls will fail.")
        self._api_url = "https://api.perplexity.ai/chat/completions"
        self.model = model

    
    async def execute_search(self, 
                           user_id: UUID, 
                           enterprise_id: UUID, 
                           query: str,
                           search_params: Optional[Dict] = None,
                           db_operations: Optional[ResearchOperations] = None) -> Tuple[Optional[UUID], Dict[str, Any]]:
        """
        Execute a new search query, orchestrating domain models and API calls.
        
        Args:
            user_id: UUID of the user initiating the search
            enterprise_id: UUID of the user's enterprise
            query: The search query
            search_params: Optional parameters for the search
            db_operations: Optional ResearchOperations instance for database operations
            
        Returns:
            Tuple of (search_id, search_response) or (None, error_response)
        """
        # Create domain model for search logic validation
        search_domain = ResearchSearch(user_id=user_id, enterprise_id=enterprise_id)
        
        # Validate the query using domain logic
        if not search_domain.validate_query(query):
            return None, {"error": "Invalid query"}
        
        # If no database operations provided, we're just executing the search without persistence
        if not db_operations:
            # Execute the search directly and return results
            response = await self._call_perplexity_api(self._build_initial_payload(query, search_params))
            if "error" in response:
                return None, response
                
            # Process the results using domain logic
            processed_response = self._process_results(response)
            return None, processed_response
        
        # With database operations, create a persistent search
        try:
            # Execute search using the API
            response = await self._call_perplexity_api(self._build_initial_payload(query, search_params))
            
            # If search execution failed, return the error
            if "error" in response:
                return None, response
            
            # Process the results
            processed_response = self._process_results(response)
            
            # Use the domain operations to create the search in the database
            return await db_operations.create_search(user_id, enterprise_id, query, search_params, processed_response)
        except Exception as e:
            logger.error(f"Error executing search: {str(e)}")
            return None, {"error": f"Workflow error: {str(e)}"}
    
    async def execute_follow_up(self,
                             search_id: UUID,
                             follow_up_query: str,
                             previous_messages: Optional[List[Dict[str, str]]] = None,
                             db_operations: Optional[ResearchOperations] = None) -> Dict[str, Any]:
        """
        Execute a follow-up query for an existing search.
        
        Args:
            search_id: UUID of the existing search
            follow_up_query: Follow-up query from the user
            previous_messages: Optional list of previous messages in the conversation
            db_operations: Optional ResearchOperations instance for database operations
            
        Returns:
            Search response or error dict
        """
        # Create domain model for validation
        search_domain = ResearchSearch(user_id=user_id, enterprise_id=enterprise_id)
        
        # Validate the query using domain logic
        if not search_domain.validate_query(follow_up_query):
            return {"error": "Invalid follow-up query"}
            
        # If no database operations provided, just execute the follow-up
        if not db_operations:
            if not previous_messages:
                return {"error": "Previous messages required for follow-up without database"}
                
            # Execute the follow-up directly
            payload = self._build_follow_up_payload(follow_up_query, previous_messages)
            response = await self._call_perplexity_api(payload)
            
            if "error" in response:
                return response
                
            # Process the results
            return self._process_results(response)
        
        # With database operations, continue a persistent search
        try:
            # Get the search from the database to retrieve context
            search_data = await db_operations.get_search_by_id(search_id)
            if not search_data:
                return {"error": "Search not found"}
            
            # Get previous messages if not provided
            if not previous_messages:
                previous_messages = self._extract_messages_for_api(search_data["messages"])
            
            # Build the payload with conversation history
            payload = self._build_follow_up_payload(follow_up_query, previous_messages)
            
            # Execute the follow-up
            response = await self._call_perplexity_api(payload)
            
            if "error" in response:
                return response
                
            # Process the results
            processed_response = self._process_results(response)
            
            # Use the domain operations to continue the search in the database
            return await db_operations.continue_search(search_id, follow_up_query, processed_response)
        except Exception as e:
            logger.error(f"Error executing follow-up: {str(e)}")
            return {"error": f"Workflow error: {str(e)}"}
    
    def _build_initial_payload(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Build the initial payload for the Perplexity API.
        
        Args:
            query: User's search query
            params: Optional search parameters
            
        Returns:
            API payload dictionary
        """
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
        
        return payload
    
    def _build_follow_up_payload(self, follow_up_query: str, previous_messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Build the payload for a follow-up query.
        
        Args:
            follow_up_query: Follow-up query from the user
            previous_messages: List of previous messages in the conversation
            
        Returns:
            API payload dictionary
        """
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
        
        return {
            "model": "sonar-pro",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
    
    def _extract_messages_for_api(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Extract messages from database format to API format.
        
        Args:
            messages: List of messages from the database
            
        Returns:
            List of messages formatted for the API
        """
        api_messages = []
        
        # Add system message if not present
        has_system = any(msg["role"] == "system" for msg in messages)
        if not has_system:
            api_messages.append({
                "role": "system",
                "content": "Provide a concise, accurate, and legally relevant response to the query, prioritizing authoritative sources such as case law, statutes, and reputable legal commentary, tailored to the needs of a practicing lawyer."
            })
        
        # Add user and assistant messages
        for msg in sorted(messages, key=lambda m: m["sequence"]):
            if msg["role"] in ["user", "assistant", "system"]:
                content = msg["content"].get("text", "") if msg["role"] == "user" else msg["content"].get("text", "")
                if content:
                    api_messages.append({
                        "role": msg["role"],
                        "content": content
                    })
        
        return api_messages
    
    async def _call_perplexity_api(
        self,
        payload: Dict[str, Any],
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        Call Perplexity's Chat Completions API with retry logic.
        
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
    
    def _process_results(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw API response for legal relevance.
        
        Args:
            response: Raw Perplexity API response
            
        Returns:
            Structured response with text and citations
        """
        # Validate response structure
        if not self._validate_api_response(response):
            return {"error": "Invalid API response structure"}
        
        # Extract text from the first choice's message content
        text = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Extract citations if available
        citations = self._extract_citations(response)
        
        # Use the response ID as thread_id for consistency
        thread_id = response.get("id", "")
        
        return {
            "thread_id": thread_id,
            "text": text,
            "citations": citations
        }
    
    def _extract_citations(self, response: Dict[str, Any]) -> List[Dict[str, str]]:
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