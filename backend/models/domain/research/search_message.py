# models/domain/research/search_message.py

from typing import Dict, Any, Optional
from uuid import UUID

class ResearchMessage:
    """Domain model for search message operations within a public search conversation."""

    def __init__(self, content: Dict[str, Any], role: str, message_id: Optional[UUID] = None):
        """
        Initialize a ResearchMessage.
        
        Args:
            content: Dictionary containing message text and metadata (e.g., citations).
            role: Role of the sender ('user' or 'assistant').
            message_id: Optional UUID of the message, if already persisted.
        """
        self.content = content
        self.role = role
        self.message_id = message_id
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
            "role": "assistant" if self.role == "user" else "user"
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
            "destination_type": destination_type
        }

        