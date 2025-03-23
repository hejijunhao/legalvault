# services/workflow/research/search_workflow.py

from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
import logging
import os
import httpx
import asyncio
from datetime import datetime
import json
from abc import ABC, abstractmethod
from openai import AsyncOpenAI

# Import settings
from core.config import settings

# Get logger for this module
logger = logging.getLogger(__name__)

# Import domain models and operations
from models.domain.research.search import ResearchSearch
from models.domain.research.search_operations import ResearchOperations
from models.domain.research.search_message_operations import SearchMessageOperations

# Import DTOs
from models.dtos.research.search_dto import SearchDTO, SearchResultDTO

# Import centralized enums
from models.enums.research_enums import QueryCategory, QueryType, QueryStatus

# Custom exceptions for more structured error handling
class SearchWorkflowError(Exception):
    """Base exception for search workflow errors."""
    def __init__(self, message: str, error_code: str = "general_error", status_code: int = 400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class QueryValidationError(SearchWorkflowError):
    """Exception raised for query validation failures."""
    def __init__(self, message: str = "Invalid query", error_code: str = "invalid_query"):
        super().__init__(message, error_code, 400)

class QueryClarificationError(SearchWorkflowError):
    """Exception raised when a query needs clarification."""
    def __init__(self, message: str = "Query needs clarification", error_code: str = "needs_clarification", 
                 suggested_clarifications: List[str] = None):
        self.suggested_clarifications = suggested_clarifications or []
        super().__init__(message, error_code, 400)

class IrrelevantQueryError(SearchWorkflowError):
    """Exception raised for non-legal queries."""
    def __init__(self, message: str = "Query is not related to legal research", error_code: str = "irrelevant_query"):
        super().__init__(message, error_code, 400)

class APIError(SearchWorkflowError):
    """Exception raised for external API errors."""
    def __init__(self, message: str, error_code: str = "api_error", status_code: int = 500):
        super().__init__(message, error_code, status_code)

class PersistenceError(SearchWorkflowError):
    """Exception raised for database persistence errors."""
    def __init__(self, message: str, error_code: str = "persistence_error"):
        super().__init__(message, error_code, 500)

# New LLM Service Classes
class LLMService(ABC):
    """Abstract base class for LLM services."""
    @abstractmethod
    async def analyze_query(self, prompt: str) -> str:
        pass

class GPT4oMiniService(LLMService):
    """Concrete implementation of LLMService using GPT-4o-mini."""
    def __init__(self):
        """Initialize the OpenAI client with API key from settings."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in settings")
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def analyze_query(self, prompt: str) -> str:
        """Analyze a query using GPT-4o-mini, ensuring JSON response."""
        # Add explicit JSON formatting instructions
        formatted_prompt = f"""Analyze the following legal query and return a JSON object with these fields:
        - type: string (one of: "COURT_CASE", "LEGISLATIVE", "COMMERCIAL", "GENERAL")
        - clarity: float (0-1)
        - complexity: float (0-1)
        - relevance: string ("yes" or "no")
        - clarifications: list of strings (empty if query is clear)

        Query: {prompt}

        Respond ONLY with the JSON object, no other text.
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}  # Force JSON response
        )
        return response.choices[0].message.content

# Updated ResearchSearchWorkflow Class
class ResearchSearchWorkflow:
    """
    Workflow orchestrator for research search functionality.
    
    This class coordinates the interaction between domain models and external services
    (like Perplexity's Sonar API) while maintaining domain-driven design principles.
    It delegates database operations to the appropriate domain operation classes.
    
    Features:
    - LLM-based query analysis and classification
    - Query enhancement with legal context
    - Comprehensive logging
    - Complete orchestration including persistence
    """
    
    def __init__(
        self,
        llm_service: LLMService,
        research_operations: ResearchOperations,
        api_key: Optional[str] = None,
        model: str = "sonar"
    ):
        """
        Initialize the workflow orchestrator with API configuration, LLM service, and operations.
        
        Args:
            llm_service: Instance of LLMService for query analysis
            research_operations: Operations class for database persistence
            api_key: Optional Perplexity API key (falls back to env var if not provided)
            model: Model name to use for API calls
        """
        self.llm_service = llm_service
        self.research_operations = research_operations
        self._api_key = api_key or os.environ.get("PERPLEXITY_API_KEY", "")
        if not self._api_key:
            logger.warning("Perplexity API key not configured. API calls will fail.")
        self._api_url = "https://api.perplexity.ai/chat/completions"
        self.model = model

    async def _analyze_query(
        self, 
        query: str,
        search_params: Optional[Dict],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyzes the query using an LLM to determine clarity, relevance, type, and complexity.
        
        Args:
            query: The search query text
            search_params: Optional search parameters
            context: Logging context
            
        Returns:
            Query analysis result including classification and metadata
        """
        prompt = f"""
        You are an expert legal research assistant. Analyze this query and provide:

        1. **Relevance**: Is it or could it be related to legal research? (Yes/No)
        2. **Clarity**: Rate its clarity from 0 (vague) to 1 (crystal clear).
        3. **Type**: Pick one: `court_case`, `legislative`, `commercial`, `general`.
        4. **Complexity**: Rate complexity from 0 (simple) to 1 (intricate).
        5. **Clarifications**: If clarity < 0.6, suggest 1-3 questions to refine it.

        Query: "{query}"

        Return your answer in JSON format with keys: relevance, clarity, type, complexity, clarifications (list or empty).
        """
        if search_params and "type" in search_params:
            prompt += f"\n\nNote: The user specified the query type as '{search_params['type']}'."

        response = await self.llm_service.analyze_query(prompt)
        try:
            analysis = json.loads(response)
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON", extra=context)
            return {"error": "Failed to analyze query"}

        if analysis["relevance"].lower() != "yes":
            category = QueryCategory.IRRELEVANT
        elif analysis["clarity"] < 0.6:
            category = QueryCategory.UNCLEAR
        elif analysis["clarity"] < 0.8:
            category = QueryCategory.BORDERLINE
        else:
            category = QueryCategory.CLEAR

        logger.info("Query analysis completed", extra={
            **context,
            "category": category,
            "type": analysis["type"],
            "clarity_score": analysis["clarity"],
            "complexity_score": analysis["complexity"],
            "is_legal_query": analysis["relevance"].lower() == "yes"
        })

        return {
            "category": category,
            "query_type": QueryType(analysis["type"]),
            "complexity_score": analysis["complexity"],
            "clarity_score": analysis["clarity"],
            "is_legal_query": analysis["relevance"].lower() == "yes",
            "confidence_score": 0.8 if analysis["relevance"].lower() == "yes" else 0.3,
            "suggested_clarifications": analysis["clarifications"] if category == QueryCategory.UNCLEAR else [],
            "requires_citation": analysis["complexity"] > 0.5,
            "estimated_token_usage": len(query.split()) * 2  # Simple estimation
        }

    def _enhance_query_with_context(self, query: str, query_analysis: Dict[str, Any]) -> str:
        """
        Enhances the original query with legal context, specialized instructions, 
        and formatting requirements based on query type.
        """
        query_type = query_analysis.get("query_type", QueryType.GENERAL)
        
        enhanced_query = query
        
        if query_type == QueryType.COURT_CASE:
            enhanced_query = f"""Legal Case Research Request: {enhanced_query}
            Please provide relevant case law, including case names, citations, key holdings,
            and their application to the query. Format citations according to standard legal citation practices."""
            
        elif query_type == QueryType.LEGISLATIVE:
            enhanced_query = f"""Legal Statutory Research Request: {enhanced_query}
            Please provide relevant statutes, regulations, or codes, including their citations,
            effective dates, and interpretation in relevant jurisdictions."""
            
        elif query_type == QueryType.COMMERCIAL:
            enhanced_query = f"""Legal Commercial Research Request: {enhanced_query}
            Please provide relevant market information, corporate data, or industry practices,
            focusing on legal implications and compliance considerations in relevant jurisdictions."""
            
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
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        if params:
            for key in ["temperature", "max_tokens", "top_p", "top_k"]:
                if key in params:
                    payload[key] = params[key]
        
        return payload

    def _build_follow_up_payload(self, follow_up_query: str, thread_id: Optional[str] = None, previous_messages: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Build the payload for a follow-up query.
        
        Args:
            follow_up_query: Follow-up query from the user
            thread_id: Optional thread ID from previous API call
            previous_messages: Optional list of previous messages in the conversation
            
        Returns:
            API payload dictionary
        """
        messages = previous_messages or []
        
        if not messages:
            messages.append({
                "role": "system",
                "content": "Provide a concise, accurate, and legally relevant response to the follow-up query, prioritizing authoritative sources such as case law, statutes, and reputable legal commentary, tailored to the needs of a practicing lawyer."
            })
        
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
        
        has_system = any(msg["role"] == "system" for msg in messages)
        if not has_system:
            api_messages.append({
                "role": "system",
                "content": "Provide a concise, accurate, and legally relevant response to the query, prioritizing authoritative sources such as case law, statutes, and reputable legal commentary, tailored to the needs of a practicing lawyer."
            })
        
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
                        timeout=30.0
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
            
            if retries < max_retries:
                await asyncio.sleep(retry_delay * (2 ** retries))
            
            retries += 1
        
        logger.error(f"API call failed after {max_retries} attempts. Last error: {last_error}")
        return {"error": f"API call failed after {max_retries} attempts. Last error: {last_error}"}

    def _validate_api_response(self, response: Dict[str, Any]) -> bool:
        """
        Validate that the API response has the expected structure.
        
        Args:
            response: Raw API response to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(response, dict):
            return False
            
        if "choices" not in response or not isinstance(response["choices"], list) or not response["choices"]:
            return False
            
        first_choice = response["choices"][0]
        if not isinstance(first_choice, dict) or "message" not in first_choice:
            return False
            
        message = first_choice["message"]
        if not isinstance(message, dict) or "content" not in message or not isinstance(message["content"], str):
            return False
            
        if "id" not in response or not response["id"]:
            return False
            
        if "citations" in response and not isinstance(response["citations"], list):
            return False
            
        return True

    def _extract_citations(self, response: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract legal citations from API response.
        
        Args:
            response: Raw Perplexity API response
            
        Returns:
            List of citation objects (e.g., {"text": "", "url": ""})
        """
        raw_citations = response.get("citations", [])
        
        formatted_citations = []
        for i, citation in enumerate(raw_citations):
            if isinstance(citation, str):
                formatted_citations.append({
                    "text": f"Source {i+1}",
                    "url": citation
                })
            elif isinstance(citation, dict):
                formatted_citations.append(citation)
        
        return formatted_citations

    def _process_results(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw API response for legal relevance.
        
        Args:
            response: Raw Perplexity API response
            
        Returns:
            Structured response with text and citations
        """
        if not self._validate_api_response(response):
            return {"error": "Invalid API response structure"}
        
        text = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        citations = self._extract_citations(response)
        
        thread_id = response.get("id", "")
        
        return {
            "thread_id": thread_id,
            "text": text,
            "citations": citations,
            "token_usage": response.get("usage", {}).get("total_tokens", 0)
        }

    async def execute_search(
        self, 
        user_id: UUID, 
        query: str,
        enterprise_id: Optional[UUID] = None, 
        search_params: Optional[Dict] = None,
        search_domain: Optional[ResearchSearch] = None
    ) -> SearchResultDTO:
        """
        Execute a new search query, orchestrating domain models and API calls.
        
        Args:
            user_id: UUID of the user initiating the search
            query: The search query
            enterprise_id: Optional UUID of the user's enterprise
            search_params: Optional parameters for the search
            search_domain: Optional ResearchSearch domain model
            
        Returns:
            SearchResultDTO containing the search results or error information
        """
        context = {
            "user_id": str(user_id),
            "timestamp": datetime.utcnow().isoformat(),
            "query_text": query[:100] + "..." if len(query) > 100 else query
        }
        
        if enterprise_id:
            context["enterprise_id"] = str(enterprise_id)
        
        logger.info("Processing research query", extra=context)
        
        start_time = datetime.utcnow()
        
        if not search_domain:
            search_domain = ResearchSearch(
                title=query,  # Use the query as initial title
                user_id=user_id,
                enterprise_id=enterprise_id if enterprise_id else None
            )
        
        if not search_domain.validate_query(query):
            logger.warning("Invalid query rejected", extra=context)
            raise QueryValidationError("Invalid query")
        
        query_analysis = await self._analyze_query(query, search_params, context)
        
        if query_analysis.get("category") == QueryCategory.UNCLEAR:
            logger.info("Unclear query detected", extra={**context, "analysis": query_analysis})
            raise QueryClarificationError(
                "Query needs clarification",
                suggested_clarifications=query_analysis.get("suggested_clarifications", [])
            )
        
        if query_analysis.get("category") == QueryCategory.IRRELEVANT:
            logger.info("Irrelevant (non-legal) query detected", extra={**context, "analysis": query_analysis})
            raise IrrelevantQueryError("This query appears to be unrelated to legal research. LegalVault Research is designed specifically for legal professionals conducting law-related research.")
        
        enhanced_query = self._enhance_query_with_context(query, query_analysis)
        
        response = await self._call_perplexity_api(self._build_initial_payload(enhanced_query, search_params))
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        if "error" in response:
            logger.error("Error in API response", extra={
                **context, 
                "error": response["error"],
                "execution_time": execution_time
            })
            raise APIError(response["error"])
        
        processed_response = self._process_results(response)
        
        # Add metadata to the response
        processed_response["metadata"] = {
            "execution_time": execution_time,
            "enhanced_query": enhanced_query,
            "query_analysis": query_analysis
        }
        
        # Create a SearchResultDTO from the processed response
        result_dto = SearchResultDTO(
            thread_id=processed_response.get("thread_id"),
            text=processed_response.get("text", ""),
            citations=processed_response.get("citations", []),
            token_usage=processed_response.get("token_usage", 0),
            metadata=processed_response.get("metadata", {})
        )
        
        # Persist the search and its results
        search_id = uuid4()
        search_dto = await self.research_operations.create_search_record(
            search_id=search_id,
            user_id=user_id,
            query=query,
            enterprise_id=enterprise_id,
            search_params=search_params,
            response=processed_response
        )
        
        # Handle database errors
        if isinstance(search_dto, dict) and "error" in search_dto:
            logger.error("Database error while persisting search", extra={
                **context,
                "error": search_dto["error"],
                "execution_time": execution_time
            })
            raise PersistenceError(search_dto["error"])
        else:
            # Add search_id to metadata for reference
            result_dto.metadata["search_id"] = str(search_id)
        
        logger.info("Search executed successfully", extra={
            **context, 
            "execution_time": execution_time,
            "search_id": str(search_id)
        })
        
        return result_dto

    async def execute_follow_up(
        self,
        search_id: UUID,
        user_id: UUID,
        follow_up_query: str,
        enterprise_id: Optional[UUID] = None,
        thread_id: Optional[str] = None,
        previous_messages: Optional[List[Dict[str, Any]]] = None
    ) -> SearchResultDTO:
        """
        Execute a follow-up query for an existing search, maintaining context.
        
        Args:
            search_id: UUID of the existing search
            user_id: UUID of the user initiating the follow-up
            follow_up_query: The follow-up query text
            enterprise_id: Optional UUID of the user's enterprise
            thread_id: Optional thread ID from previous API call
            previous_messages: Optional list of previous messages
            
        Returns:
            SearchResultDTO containing the search results or error information
            
        Raises:
            QueryValidationError: If the query is invalid
            APIError: If there's an error with the external API
            PersistenceError: If there's an error persisting the results
        """
        context = {
            "user_id": str(user_id),
            "search_id": str(search_id),
            "timestamp": datetime.utcnow().isoformat(),
            "query_text": follow_up_query[:100] + "..." if len(follow_up_query) > 100 else follow_up_query
        }
        
        if enterprise_id:
            context["enterprise_id"] = str(enterprise_id)
        
        logger.info("Processing follow-up query", extra=context)
        
        start_time = datetime.utcnow()
        
        # First, verify the search exists and belongs to this user
        search_dto = await self.research_operations.get_search_by_id(search_id)
        
        if not search_dto:
            logger.warning("Search not found", extra=context)
            raise SearchWorkflowError("Search not found", "search_not_found", 404)
        
        if search_dto.user_id != user_id:
            logger.warning("Unauthorized access attempt", extra=context)
            raise SearchWorkflowError("Unauthorized access to this search", "unauthorized", 403)
        
        # If no thread_id or previous_messages provided, try to get them from the search
        if not thread_id or not previous_messages:
            if search_dto.messages and len(search_dto.messages) >= 2:
                # Extract thread_id and messages from the search
                assistant_messages = [m for m in search_dto.messages if m.role == "assistant"]
                if assistant_messages and "thread_id" in assistant_messages[-1].content:
                    thread_id = assistant_messages[-1].content.get("thread_id")
                
                # Convert messages to the format expected by the API
                previous_messages = []
                for msg in search_dto.messages:
                    if msg.role == "user":
                        previous_messages.append({"role": "user", "content": msg.content.get("text", "")})
                    elif msg.role == "assistant" and "text" in msg.content:
                        previous_messages.append({"role": "assistant", "content": msg.content.get("text", "")})
        
        # Validate the follow-up query
        search_domain = ResearchSearch(user_id=user_id, enterprise_id=enterprise_id)
        if not search_domain.validate_query(follow_up_query):
            logger.warning("Invalid follow-up query rejected", extra=context)
            raise QueryValidationError("Invalid follow-up query")
        
        # Call the API with the follow-up query and context
        payload = self._build_follow_up_payload(follow_up_query, thread_id, previous_messages or [])
        response = await self._call_perplexity_api(payload)
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        if "error" in response:
            logger.error("Error in API response", extra={
                **context, 
                "error": response["error"],
                "execution_time": execution_time
            })
            raise APIError(response["error"])
        
        processed_response = self._process_results(response)
        
        # Add metadata to the response
        processed_response["metadata"] = {
            "execution_time": execution_time,
            "is_follow_up": True
        }
        
        # Create a SearchResultDTO from the processed response
        result_dto = SearchResultDTO(
            thread_id=processed_response.get("thread_id"),
            text=processed_response.get("text", ""),
            citations=processed_response.get("citations", []),
            token_usage=processed_response.get("token_usage", 0),
            metadata=processed_response.get("metadata", {})
        )
        
        # Persist the follow-up query and response
        success = await self.research_operations.add_search_messages(
            search_id=search_id,
            user_query=follow_up_query,
            response=processed_response
        )
        
        if not success:
            logger.error("Failed to persist follow-up messages", extra=context)
            raise PersistenceError("Failed to save follow-up messages")
        
        logger.info("Follow-up query executed successfully", extra={
            **context, 
            "execution_time": execution_time
        })
        
        return result_dto

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