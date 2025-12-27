"""Conversation memory management for the agent."""
import logging
from typing import List, Dict, Any
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from config import settings

logger = logging.getLogger(__name__)


class InMemoryChatHistory(BaseChatMessageHistory):
    """Simple in-memory chat history implementation."""
    
    def __init__(self, session_id: str):
        """
        Initialize chat history for a session.
        
        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.messages: List[BaseMessage] = []
        self.max_messages = settings.conversation_memory_window * 2  # User + AI pairs
    
    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the history."""
        self.messages.append(message)
        
        # Keep only recent messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def clear(self) -> None:
        """Clear all messages."""
        self.messages = []
    
    @property
    def messages_list(self) -> List[BaseMessage]:
        """Get all messages."""
        return self.messages


class ConversationManager:
    """Manages multiple conversation sessions."""
    
    def __init__(self):
        """Initialize the conversation manager."""
        self.sessions: Dict[str, InMemoryChatHistory] = {}
    
    def get_session(self, session_id: str) -> InMemoryChatHistory:
        """
        Get or create a chat history for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Chat history for the session
        """
        if session_id not in self.sessions:
            logger.info(f"Creating new session: {session_id}")
            self.sessions[session_id] = InMemoryChatHistory(session_id)
        
        return self.sessions[session_id]
    
    def add_user_message(self, session_id: str, message: str) -> None:
        """Add a user message to the session."""
        session = self.get_session(session_id)
        session.add_message(HumanMessage(content=message))
        logger.debug(f"Added user message to session {session_id}")
    
    def add_ai_message(self, session_id: str, message: str) -> None:
        """Add an AI message to the session."""
        session = self.get_session(session_id)
        session.add_message(AIMessage(content=message))
        logger.debug(f"Added AI message to session {session_id}")
    
    def get_messages(self, session_id: str) -> List[BaseMessage]:
        """Get all messages for a session."""
        session = self.get_session(session_id)
        return session.messages_list
    
    def clear_session(self, session_id: str) -> None:
        """Clear a session's history."""
        if session_id in self.sessions:
            self.sessions[session_id].clear()
            logger.info(f"Cleared session: {session_id}")
    
    def delete_session(self, session_id: str) -> None:
        """Delete a session entirely."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")


# Global conversation manager instance
conversation_manager = ConversationManager()
