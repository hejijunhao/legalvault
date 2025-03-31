# services/workflow/research/search_workflow.py

from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
import logging
import os
import httpx
import asyncio
from datetime import datetime
import json
from abc import ABC, abstractmethod
from openai import AsyncOpenAI

from core.config import settings
from models.domain.research.search_operations import ResearchOperations
from models.dtos.research.search_dto import SearchResultDTO
from models.enums.research_enums import QueryCategory, QueryType, QueryStatus

logger = logging.getLogger(__name__)

class SearchWorkflowError(Exception):
    """Base exception for search workflow errors."""
    def __init__(self, message: str, error_code: str = "general_error", status_code: int = 400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class LLMService(ABC):
    @abstractmethod
    async def analyze_query(self, prompt: str) -> str:
        pass

class GPT4oMiniService(LLMService):
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in settings")
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def analyze_query(self, prompt: str) -> str:
        formatted_prompt = f"""Analyze the following legal query and return a JSON object with:
        - type: string (COURT_CASE, LEGISLATIVE, COMMERCIAL, GENERAL)
        - clarity: float (0-1)
        - complexity: float (0-1)
        - relevance: string (yes/no)
        - clarifications: list of strings (empty if clear)
        Query: {prompt}
        Respond ONLY with the JSON object."""
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content

class ResearchSearchWorkflow:
    """Orchestrates research search functionality with LLM and Perplexity API integration."""

    def __init__(self, llm_service: LLMService, research_operations: ResearchOperations, api_key: Optional[str] = None, model: str = "sonar"):
        self.llm_service = llm_service
        self.research_operations = research_operations
        self._api_key = api_key or os.environ.get("PERPLEXITY_API_KEY", "")
        self._api_url = "https://api.perplexity.ai/chat/completions"
        self.model = model
        if not self._api_key:
            logger.warning("Perplexity API key not configured.")

    async def _analyze_query(self, query: str, search_params: Optional[Dict], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes query using LLM for clarity, relevance, and type."""
        prompt = f"""You are an expert legal research assistant. Analyze this query:
        1. Relevance: Is it legal-related? (Yes/No)
        2. Clarity: Rate 0-1
        3. Type: court_case, legislative, commercial, general
        4. Complexity: Rate 0-1
        5. Clarifications: If clarity < 0.6, suggest 1-3 questions
        Query: "{query}"
        Return JSON: relevance, clarity, type, complexity, clarifications"""
        if search_params and "type" in search_params:
            prompt += f"\nUser specified type: '{search_params['type']}'"
        
        response = await self.llm_service.analyze_query(prompt)
        try:
            analysis = json.loads(response)
            category = (
                QueryCategory.IRRELEVANT if analysis["relevance"].lower() != "yes" else
                QueryCategory.UNCLEAR if analysis["clarity"] < 0.6 else
                QueryCategory.BORDERLINE if analysis["clarity"] < 0.8 else
                QueryCategory.CLEAR
            )
            logger.info("Query analyzed", extra={**context, "category": category, "type": analysis["type"]})
            return {
                "category": category,
                "query_type": QueryType(analysis["type"]),
                "complexity_score": analysis["complexity"],
                "clarity_score": analysis["clarity"],
                "is_legal_query": analysis["relevance"].lower() == "yes",
                "suggested_clarifications": analysis["clarifications"] if category == QueryCategory.UNCLEAR else []
            }
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response", extra=context)
            raise SearchWorkflowError("Failed to analyze query", "json_error", 500)

    async def _call_perplexity_api(self, payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Calls Perplexity API with retry logic."""
        if not self._api_key:
            raise SearchWorkflowError("API key not configured", "api_key_missing", 500)
        
        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            for attempt in range(3):
                try:
                    response = await client.post(self._api_url, json=payload, headers=headers, timeout=30.0)
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPStatusError as e:
                    logger.warning(f"HTTP error {e.response.status_code}", extra=context)
                    if attempt == 2:
                        raise SearchWorkflowError(f"API failed: {e.response.text}", "api_error", e.response.status_code)
                except httpx.RequestError as e:
                    logger.warning(f"Request error: {e}", extra=context)
                    if attempt == 2:
                        raise SearchWorkflowError(f"API request failed: {e}", "request_error", 500)
                await asyncio.sleep(1 * (2 ** attempt))
            return {}

    async def execute_search(self, user_id: UUID, query: str, enterprise_id: Optional[UUID] = None, search_params: Optional[Dict] = None) -> SearchResultDTO:
        """Executes a new search query."""
        context = {"user_id": str(user_id), "query_text": query[:100] + "..." if len(query) > 100 else query}
        if enterprise_id:
            context["enterprise_id"] = str(enterprise_id)
        logger.info("Processing search", extra=context)
        
        start_time = datetime.utcnow()
        query_analysis = await self._analyze_query(query, search_params, context)
        
        if query_analysis["category"] == QueryCategory.UNCLEAR:
            raise SearchWorkflowError("Query needs clarification", "needs_clarification", 400, query_analysis["suggested_clarifications"])
        if query_analysis["category"] == QueryCategory.IRRELEVANT:
            raise SearchWorkflowError("Query unrelated to legal research", "irrelevant_query", 400)
        
        enhanced_query = (
            f"Legal {query_analysis['query_type'].value.replace('_', ' ').title()} Research: {query}\n"
            "Provide comprehensive legal analysis with citations, distinctions, splits, updates, and applications."
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "Answer legally, concisely, with authoritative sources for lawyers."},
                {"role": "user", "content": enhanced_query}
            ],
            "temperature": search_params.get("temperature", 0.7) if search_params else 0.7,
            "max_tokens": search_params.get("max_tokens", 500) if search_params else 500
        }
        response = await self._call_perplexity_api(payload, context)
        if "error" in response:
            raise SearchWorkflowError(response["error"], "api_error", 500)
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        text = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        citations = [{"text": f"Source {i+1}", "url": c} if isinstance(c, str) else c for i, c in enumerate(response.get("citations", []))]
        
        result_dto = SearchResultDTO(
            thread_id=response.get("id", ""),
            text=text,
            citations=citations,
            token_usage=response.get("usage", {}).get("total_tokens", 0),
            metadata={"execution_time": execution_time, "query_analysis": query_analysis}
        )
        
        search_id = uuid4()
        search_dto = await self.research_operations.create_search_record(
            search_id=search_id, user_id=user_id, query=query, enterprise_id=enterprise_id,
            search_params=search_params, response=result_dto.dict()
        )
        if isinstance(search_dto, dict) and "error" in search_dto:
            raise SearchWorkflowError(f"Persistence failed: {search_dto['error']}", "persistence_error", 500)
        result_dto.metadata["search_id"] = str(search_id)
        
        logger.info("Search completed", extra={**context, "execution_time": execution_time, "search_id": str(search_id)})
        return result_dto

    async def execute_follow_up(self, search_id: UUID, user_id: UUID, follow_up_query: str, enterprise_id: Optional[UUID] = None) -> SearchResultDTO:
        """Executes a follow-up query."""
        context = {"user_id": str(user_id), "search_id": str(search_id), "query_text": follow_up_query[:100] + "..." if len(follow_up_query) > 100 else follow_up_query}
        if enterprise_id:
            context["enterprise_id"] = str(enterprise_id)
        logger.info("Processing follow-up", extra=context)
        
        start_time = datetime.utcnow()
        search_dto = await self.research_operations.get_search_by_id(search_id)
        if not search_dto:
            raise SearchWorkflowError("Search not found", "search_not_found", 404)
        if search_dto.user_id != user_id:
            raise SearchWorkflowError("Unauthorized access", "unauthorized", 403)
        
        previous_messages = [
            {"role": m.role, "content": m.content.get("text", "")}
            for m in sorted(search_dto.messages or [], key=lambda m: m.sequence)
            if m.role in ["user", "assistant"] and m.content.get("text")
        ] or [{"role": "system", "content": "Answer legally, concisely, with authoritative sources for lawyers."}]
        previous_messages.append({"role": "user", "content": follow_up_query})
        
        payload = {"model": self.model, "messages": previous_messages, "temperature": 0.7, "max_tokens": 500}
        response = await self._call_perplexity_api(payload, context)
        if "error" in response:
            raise SearchWorkflowError(response["error"], "api_error", 500)
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        text = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        citations = [{"text": f"Source {i+1}", "url": c} if isinstance(c, str) else c for i, c in enumerate(response.get("citations", []))]
        
        result_dto = SearchResultDTO(
            thread_id=response.get("id", ""),
            text=text,
            citations=citations,
            token_usage=response.get("usage", {}).get("total_tokens", 0),
            metadata={"execution_time": execution_time, "is_follow_up": True}
        )
        
        success = await self.research_operations.add_search_messages(search_id, follow_up_query, result_dto.dict())
        if not success:
            raise SearchWorkflowError("Failed to save follow-up", "persistence_error", 500)
        
        logger.info("Follow-up completed", extra={**context, "execution_time": execution_time})
        return result_dto