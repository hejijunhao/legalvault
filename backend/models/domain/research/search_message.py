# models/domain/research/search_message.py

from typing import Dict, Any, Optional, Literal
from uuid import UUID
from models.enums.research_enums import QueryStatus

class ResearchMessage:
    """Domain model for search message operations within a public search conversation."""

    def __init__(self, content: Dict[str, Any], role: str, message_id: Optional[UUID] = None, 
                 sequence: Optional[int] = None, status: QueryStatus = QueryStatus.PENDING):
        """
        Initialize a ResearchMessage.
        
        Args:
            content: Dictionary containing message text and metadata (e.g., citations).
            role: Role of the sender ('user' or 'assistant').
            message_id: Optional UUID of the message, if already persisted.
            sequence: Optional sequence number for ordering within a conversation.
            status: Status of the message (pending, completed, failed, etc.).
        """
        self.content = content
        self.role = role
        self.message_id = message_id
        self.sequence = sequence
        self.status = status
        self._validate()

    def _validate(self) -> None:
        """Validate message properties."""
        if not isinstance(self.content, dict) or "text" not in self.content:
            raise ValueError("Content must be a dictionary with a 'text' key")
        if self.role not in ["user", "assistant"]:
            raise ValueError("Role must be 'user' or 'assistant'")

    def format_for_external_sharing(self) -> str:
        """Format message content for external sharing."""
        if self.role == "user":
            return f"Question: {self.content.get('text', '')}"
        else:
            text = self.content.get('text', '')
            citations = self.content.get('citations', [])
            formatted_citations = "\n".join(
                [f"- {c.get('text', '')}: {c.get('url', '')}" for c in citations]
            )
            return f"Answer: {text}\n\nSources:\n{formatted_citations}" if citations else f"Answer: {text}"

    def generate_reply_context(self) -> Dict[str, Any]:
        """Generate context for replying to this message."""
        return {
            "original_text": self.content.get('text', ''),
            "reply_to_message_id": self.message_id,
            "role": "assistant" if self.role == "user" else "user",
            "sequence": self.sequence,
            "status": self.status.value if hasattr(self.status, 'value') else self.status
        }

    def forward_message(self, destination: str, destination_type: str) -> Dict[str, Any]:
        """
        Prepare data for forwarding this message to another destination.
        
        Args:
            destination: Where the message is being forwarded (e.g., email, user ID).
            destination_type: Type of destination (e.g., 'email', 'internal').
        
        Returns:
            Dict with forwarding details.
        """
        if not destination or not destination_type:
            raise ValueError("Destination and destination_type are required")
        return {
            "message_id": self.message_id,
            "content": self.content,
            "role": self.role,
            "destination": destination,
            "destination_type": destination_type,
            "sequence": self.sequence,
            "status": self.status.value if hasattr(self.status, 'value') else self.status
        }
        
    def categorize_message(self) -> Literal["question", "answer", "clarification", "citation"]:
        """
        Categorize the message based on its content and role.
        
        Returns:
            Message category as a string.
        """
        if self.role == "user":
            text = self.content.get('text', '').lower()
            if any(q in text for q in ["?", "how", "what", "when", "where", "why", "who"]):
                return "question"
            elif any(c in text for c in ["clarify", "explain", "elaborate", "mean"]):
                return "clarification"
            else:
                return "question"  # Default for user messages
        else:
            if self.content.get('citations', []):
                return "citation"
            else:
                return "answer"
                
    def is_system_message(self) -> bool:
        """
        Check if this is a system message.
        
        Returns:
            True if this is a system message, False otherwise.
        """
        return self.role == "assistant" and self.content.get('is_system', False)
        
    def update_status(self, status: QueryStatus) -> None:
        """
        Update the status of this message.
        
        Args:
            status: New status value
        """
        self.status = status
        
    def is_completed(self) -> bool:
        """
        Check if this message has been completed.
        
        Returns:
            True if the message status is COMPLETED, False otherwise.
        """
        return self.status == QueryStatus.COMPLETED
        
    def is_failed(self) -> bool:
        """
        Check if this message has failed processing.
        
        Returns:
            True if the message status is FAILED, False otherwise.
        """
        return self.status == QueryStatus.FAILED