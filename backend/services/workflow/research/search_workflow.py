# services/workflow/research/search_workflow.py

from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
import logging
import os
import httpx
import asyncio
from datetime import datetime
from enum import Enum

from models.domain.research.search import ResearchSearch
from models.domain.research.search_operations import ResearchOperations
from models.domain.research.search_message_operations import SearchMessageOperations

logger = logging.getLogger(__name__)


class QueryCategory(str, Enum):
    CLEAR = "clear"
    UNCLEAR = "unclear"
    IRRELEVANT = "irrelevant"
    BORDERLINE = "borderline"  # For queries that might need review


class QueryType(str, Enum):
    COURT_CASE = "court_case"
    LEGISLATIVE = "legislative"
    COMMERCIAL = "commercial"
    GENERAL = "general"


class QueryStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_CLARIFICATION = "needs_clarification"
    IRRELEVANT = "irrelevant_query"


class ResearchSearchWorkflow:
    """
    Workflow orchestrator for research search functionality.
    
    This class coordinates the interaction between domain models and external services
    (like Perplexity's Sonar API) while maintaining domain-driven design principles.
    It delegates database operations to the appropriate domain operation classes.
    
    Features:
    - Query analysis and classification
    - Query enhancement with legal context
    - Comprehensive logging
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "sonar-pro"
    ):
        """
        Initialize the workflow orchestrator with API configuration.
        
        Args:
            api_key: Optional Perplexity API key (falls back to env var if not provided)
            model: Model name to use for API calls
        """
        self._api_key = api_key or os.environ.get("PERPLEXITY_API_KEY", "")
        if not self._api_key:
            logger.warning("Perplexity API key not configured. API calls will fail.")
        self._api_url = "https://api.perplexity.ai/chat/completions"
        self.model = model

    
    async def execute_search(
        self, 
        user_id: UUID, 
        query: str,
        enterprise_id: Optional[UUID] = None, 
        search_params: Optional[Dict] = None,
        db_operations: ResearchOperations = None
    ) -> Tuple[Optional[UUID], Dict[str, Any]]:
        """
        Execute a new search query, orchestrating domain models and API calls.
        
        Args:
            user_id: UUID of the user initiating the search
            query: The search query
            enterprise_id: Optional UUID of the user's enterprise
            search_params: Optional parameters for the search
            db_operations: ResearchOperations instance for database operations
            
        Returns:
            Tuple of (search_id, search_response) or (None, error_response)
        """
        # Create execution context for logging
        context = {
            "user_id": str(user_id),
            "timestamp": datetime.utcnow().isoformat(),
            "query_text": query[:100] + "..." if len(query) > 100 else query
        }
        
        # Add enterprise_id to context if provided
        if enterprise_id:
            context["enterprise_id"] = str(enterprise_id)
        
        # Log the incoming query with context
        logger.info("Processing research query", extra=context)
        
        start_time = datetime.utcnow()
        
        # Create domain model for search logic validation
        search_domain = ResearchSearch(user_id=user_id, enterprise_id=enterprise_id if enterprise_id else None)
        
        # Validate the query using domain logic
        if not search_domain.validate_query(query):
            logger.warning("Invalid query rejected", extra=context)
            return None, {"error": "Invalid query"}
        
        # Check if the query meets our basic analysis criteria
        query_analysis = await self._analyze_query(query, search_params, context)
        
        # Handle unclear or irrelevant queries
        if query_analysis.get("category") == "unclear":
            logger.info("Unclear query detected", extra={**context, "analysis": query_analysis})
            return None, {
                "error": "Query needs clarification",
                "suggested_clarifications": query_analysis.get("suggested_clarifications", [])
            }
        
        if query_analysis.get("category") == "irrelevant":
            logger.info("Irrelevant (non-legal) query detected", extra={**context, "analysis": query_analysis})
            return None, {
                "error": "This query appears to be unrelated to legal research. LegalVault Research is designed specifically for legal professionals conducting law-related research."
            }
        
        # Enhance query with legal context based on analysis
        enhanced_query = self._enhance_query_with_context(query, query_analysis)
        
        # Execute search using the API
        response = await self._call_perplexity_api(self._build_initial_payload(enhanced_query, search_params))
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        # If search execution failed, return the error
        if "error" in response:
            logger.error("Error in API response", extra={
                **context, 
                "error": response["error"],
                "execution_time": execution_time
            })
            return None, response
        
        # Process the results
        processed_response = self._process_results(response)
        
        # If no database operations provided, just return the results
        if not db_operations:
            logger.info("Search executed successfully without persistence", extra={
                **context, 
                "execution_time": execution_time
            })
            return None, processed_response
        
        # Save to database if db_operations is provided
        try:
            # Use the domain operations to create the search in the database
            search_id, search_data = await db_operations.create_search(
                user_id, 
                enterprise_id if enterprise_id else None, 
                query, 
                search_params, 
                processed_response,
                metadata={
                    "execution_time": execution_time,
                    "enhanced_query": enhanced_query,
                    "query_analysis": query_analysis
                }
            )
            
            logger.info("Persistent search created successfully", extra={
                **context, 
                "search_id": str(search_id),
                "execution_time": execution_time
            })
            
            return search_id, processed_response
            
        except Exception as e:
            logger.error(f"Error executing search", extra={
                **context,
                "error": str(e),
                "error_type": type(e).__name__,
                "execution_time": execution_time
            })
            return None, {"error": f"Workflow error: {str(e)}"}
    
    async def execute_follow_up(
        self,
        search_id: UUID,
        follow_up_query: str,
        user_id: UUID = None,  # Added for context tracking
        enterprise_id: UUID = None,  # Added for context tracking
        previous_messages: Optional[List[Dict[str, str]]] = None,
        db_operations: Optional[ResearchOperations] = None
    ) -> Dict[str, Any]:
        """
        Execute a follow-up query for an existing search.
        
        Args:
            search_id: UUID of the existing search
            follow_up_query: Follow-up query from the user
            user_id: Optional UUID of the user for context tracking
            enterprise_id: Optional UUID of the enterprise for context tracking
            previous_messages: Optional list of previous messages in the conversation
            db_operations: Optional ResearchOperations instance for database operations
            
        Returns:
            Search response or error dict
        """
        # Create execution context for logging
        context = {
            "search_id": str(search_id),
            "timestamp": datetime.utcnow().isoformat(),
            "follow_up_query": follow_up_query[:100] + "..." if len(follow_up_query) > 100 else follow_up_query
        }
        
        # Add user_id and enterprise_id to context if provided
        if user_id:
            context["user_id"] = str(user_id)
        if enterprise_id:
            context["enterprise_id"] = str(enterprise_id)
        
        logger.info("Processing follow-up query", extra=context)
        
        start_time = datetime.utcnow()
        
        # Create domain model for validation
        search_domain = ResearchSearch(
            user_id=user_id if user_id else UUID(int=0),
            enterprise_id=enterprise_id
        )
        
        # Validate the query using domain logic
        if not search_domain.validate_query(follow_up_query):
            logger.warning("Invalid follow-up query rejected", extra=context)
            return {"error": "Invalid follow-up query"}
            
        # If no database operations provided, just execute the follow-up
        if not db_operations:
            if not previous_messages:
                logger.error("Previous messages required for follow-up without database", extra=context)
                return {"error": "Previous messages required for follow-up without database"}
                
            # Execute the follow-up directly
            payload = self._build_follow_up_payload(follow_up_query, previous_messages)
            response = await self._call_perplexity_api(payload)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            if "error" in response:
                logger.error("Error in API response for follow-up", extra={
                    **context, 
                    "error": response["error"],
                    "execution_time": execution_time
                })
                return response
                
            # Process the results
            processed_response = self._process_results(response)
            
            logger.info("Follow-up executed successfully without persistence", extra={
                **context, 
                "execution_time": execution_time
            })
            
            return processed_response
        
        # With database operations, continue a persistent search
        try:
            # Get the search from the database to retrieve context
            search_data = await db_operations.get_search_by_id(search_id)
            if not search_data:
                logger.error("Search not found for follow-up", extra=context)
                return {"error": "Search not found"}
            
            # Get previous messages if not provided
            if not previous_messages:
                previous_messages = self._extract_messages_for_api(search_data["messages"])
            
            # Build the payload with conversation history
            payload = self._build_follow_up_payload(follow_up_query, previous_messages)
            
            # Execute the follow-up
            response = await self._call_perplexity_api(payload)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            if "error" in response:
                logger.error("Error in API response for persistent follow-up", extra={
                    **context, 
                    "error": response["error"],
                    "execution_time": execution_time
                })
                return response
                
            # Process the results
            processed_response = self._process_results(response)
            
            # Use the domain operations to continue the search in the database
            result = await db_operations.continue_search(
                search_id, 
                follow_up_query, 
                processed_response,
                metadata={"execution_time": execution_time}
            )
            
            logger.info("Persistent follow-up executed successfully", extra={
                **context, 
                "execution_time": execution_time
            })
            
            return result
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error executing follow-up", extra={
                **context,
                "error": str(e),
                "error_type": type(e).__name__,
                "execution_time": execution_time
            })
            return {"error": f"Workflow error: {str(e)}"}
    
    async def get_search_status(
        self, 
        search_id: UUID,
        db_operations: ResearchOperations
    ) -> Dict[str, Any]:
        """
        Retrieves the current status of a search.
        
        Args:
            search_id: The UUID of the search
            db_operations: ResearchOperations instance for database operations
            
        Returns:
            A dictionary with the current status and metadata
        """
        try:
            return await db_operations.get_search_status(search_id)
        except Exception as e:
            logger.error(f"Error retrieving search status", extra={
                "search_id": str(search_id),
                "error": str(e)
            })
            return {"error": f"Failed to retrieve search status: {str(e)}"}
    
    async def _analyze_query(
        self, 
        query: str,
        search_params: Optional[Dict],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyzes the query to determine clarity, relevance, type, and complexity.
        
        This is a simplified version for the initial implementation - 
        in a more advanced version, this would use a lightweight LLM.
        
        Args:
            query: The search query text
            search_params: Optional search parameters
            context: Logging context
            
        Returns:
            Query analysis result including classification and metadata
        """
        # Simple initial implementation of query analysis
        is_legal_query = self._is_likely_legal_query(query)
        clarity_score = self._estimate_clarity(query)
        
        # Determine query type from toggles if available
        query_type = "general"
        if search_params and "type" in search_params:
            param_type = search_params["type"]
            if param_type in ["court_case", "legislative", "commercial"]:
                query_type = param_type
        else:
            # Try to infer from content
            if any(term in query.lower() for term in ["case", "ruling", "judgment", "decision", "court"]):
                query_type = "court_case"
            elif any(term in query.lower() for term in ["law", "statute", "regulation", "code", "act", "bill"]):
                query_type = "legislative"
            elif any(term in query.lower() for term in ["market", "company", "industry", "business", "corporation"]):
                query_type = "commercial"
        
        # Determine category
        category = "clear"
        if not is_legal_query:
            category = "irrelevant"
        elif clarity_score < 0.6:
            category = "unclear"
        elif clarity_score < 0.8:
            category = "borderline"
        
        # Estimate complexity for API tier selection
        complexity_score = self._estimate_complexity(query)
        
        # Generate clarifications for unclear queries
        suggested_clarifications = []
        if category == "unclear":
            suggested_clarifications = self._generate_clarifications(query)
        
        # Log analysis results
        logger.info("Query analysis completed", extra={
            **context,
            "category": category,
            "type": query_type,
            "clarity_score": clarity_score,
            "complexity_score": complexity_score,
            "is_legal_query": is_legal_query
        })
        
        # Return structured analysis
        return {
            "category": category,
            "query_type": query_type,
            "complexity_score": complexity_score,
            "clarity_score": clarity_score,
            "is_legal_query": is_legal_query,
            "confidence_score": 0.8 if is_legal_query else 0.3,
            "suggested_clarifications": suggested_clarifications,
            "requires_citation": complexity_score > 0.5,
            "estimated_token_usage": len(query.split()) * 2  # Simple estimation
        }
    
    def _is_likely_legal_query(self, query: str) -> bool:
        """Simple heuristic to determine if a query is likely legal-related"""
        legal_terms = [
            "law", "legal", "court", "judge", "attorney", "lawyer", "case", 
            "statute", "regulation", "plaintiff", "defendant", "ruling",
            "contract", "liability", "legislation", "judicial", "rights",
            "suit", "sue", "claim", "precedent", "jurisdiction", "tort"
        ]
        query_lower = query.lower()
        
        # Check if any legal terms are present
        for term in legal_terms:
            if term in query_lower:
                return True
        
        # More sophisticated check could be implemented here
        return False
    
    def _estimate_clarity(self, query: str) -> float:
        """Estimate query clarity score between 0 and 1"""
        # Simple implementation - more sophisticated version would use NLP
        words = query.split()
        
        # Too short queries are unclear
        if len(words) < 3:
            return 0.4
        
        # Very long queries might be clear but complex
        if len(words) > 50:
            return 0.7
        
        # Check for question marks - queries with questions are often clearer
        if "?" in query:
            return 0.8
        
        # Default medium clarity
        return 0.6
    
    def _estimate_complexity(self, query: str) -> float:
        """Estimate query complexity between 0 and 1"""
        # Simple implementation - more sophisticated version would use NLP
        words = query.split()
        
        # Short queries are usually simple
        if len(words) < 5:
            return 0.2
        
        # Longer queries tend to be more complex
        if len(words) > 20:
            return 0.7
        
        # Check for complex legal terminology
        complex_terms = [
            "estoppel", "precedent", "jurisprudence", "statutory", "doctrine",
            "jurisdiction", "fiduciary", "tort", "mens rea", "prima facie"
        ]
        
        complexity_boost = 0.0
        for term in complex_terms:
            if term in query.lower():
                complexity_boost += 0.1
        
        # Base complexity with boost, capped at 1.0
        return min(0.4 + complexity_boost, 1.0)
    
    def _generate_clarifications(self, query: str) -> List[Dict[str, Any]]:
        """Generate suggested clarifications for unclear queries"""
        # Simple implementation - would be more sophisticated in production
        clarifications = []
        
        # Check if jurisdiction is missing
        if not any(term in query.lower() for term in ["state", "federal", "country", "jurisdiction"]):
            clarifications.append({
                "question": "Which jurisdiction are you interested in?",
                "options": ["Federal", "State", "International"],
                "type": "select"
            })
        
        # Check if time period is missing
        if not any(term in query.lower() for term in ["year", "recent", "current", "historical"]):
            clarifications.append({
                "question": "What time period should be considered?",
                "options": ["Current law only", "Include historical development", "Specific time period"],
                "type": "select"
            })
        
        # Generic clarification for very short queries
        if len(query.split()) < 5:
            clarifications.append({
                "question": "Please provide more details about your legal question.",
                "type": "text"
            })
        
        return clarifications
    
    def _enhance_query_with_context(self, query: str, query_analysis: Dict[str, Any]) -> str:
        """
        Enhances the original query with legal context, specialized instructions, 
        and formatting requirements based on query type.
        """
        query_type = query_analysis.get("query_type", "general")
        
        # Base query
        enhanced_query = query
        
        # Add query type specific instructions
        if query_type == "court_case":
            enhanced_query = f"""Legal Case Research Request: {enhanced_query}
            Please provide relevant case law, including case names, citations, key holdings,
            and their application to the query. Format citations according to standard legal citation practices."""
            
        elif query_type == "legislative":
            enhanced_query = f"""Legal Statutory Research Request: {enhanced_query}
            Please provide relevant statutes, regulations, or codes, including their citations,
            effective dates, and interpretation in relevant jurisdictions."""
            
        elif query_type == "commercial":
            enhanced_query = f"""Legal Commercial Research Request: {enhanced_query}
            Please provide relevant market information, corporate data, or industry practices,
            focusing on legal implications and compliance considerations in relevant jurisdictions."""
            
        # Add general legal research guidelines
        enhanced_query += """
        Please provide a comprehensive legal analysis with:
        1. Direct citations to primary sources (cases, statutes, regulations)
        2. Clear distinction between majority and minority positions
        3. Identification of any circuit splits or jurisdictional differences
        4. Recent developments or pending changes in the law
        5. Practical applications for legal practitioners
        
        Results should be structured, authoritative, and suitable for legal professionals."""
        
        return enhanced_query

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
            "model": self.model,
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
            "model": self.model,
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
                        timeout=30.0  # Increased timeout for potentially long API calls
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
            "citations": citations,
            "token_usage": response.get("usage", {}).get("total_tokens", 0)
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

# Future Enhancements:
# 1. Caching Layer
# - Implement Redis caching for frequently asked legal questions
# - Add cache key generation and TTL management

# 2. Asynchronous Processing
# - Add support for long-running queries with webhook notifications
# - Implement background tasks for complex research

# 3. User Feedback System
# - Add tracking of query quality and user satisfaction
# - Use feedback to improve query analysis and enhancement