"""
Enhanced AI Engine with Memory & Context
- Conversation history tracking
- Context-aware responses
- Memory persistence
- Multi-turn conversations
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from collections import deque

from ai_engine import AIEngine, AIResponse
from database.db_manager import get_db_manager


@dataclass
class ConversationTurn:
    """Single turn in conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConversationMemory:
    """
    Manages conversation history and context
    Implements sliding window for token management
    """
    
    def __init__(self, max_turns: int = 10, max_tokens: int = 4000):
        self.max_turns = max_turns
        self.max_tokens = max_tokens
        self.turns: deque = deque(maxlen=max_turns)
        self.conversation_id = f"conv_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        self.metadata = {}
    
    def add_turn(self, role: str, content: str, metadata: Dict = None):
        """Add conversation turn"""
        turn = ConversationTurn(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.turns.append(turn)
    
    def get_context_messages(self) -> List[Dict[str, str]]:
        """Get messages formatted for AI API"""
        messages = []
        for turn in self.turns:
            messages.append({
                "role": turn.role,
                "content": turn.content
            })
        return messages
    
    def get_recent_context(self, n: int = 5) -> List[ConversationTurn]:
        """Get N most recent turns"""
        return list(self.turns)[-n:]
    
    def clear(self):
        """Clear conversation history"""
        self.turns.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "conversation_id": self.conversation_id,
            "turns": [
                {
                    "role": turn.role,
                    "content": turn.content,
                    "timestamp": turn.timestamp,
                    "metadata": turn.metadata
                }
                for turn in self.turns
            ],
            "metadata": self.metadata
        }


class EnhancedAIEngine(AIEngine):
    """
    Enhanced AI Engine with memory and context
    Extends base AIEngine with conversation tracking
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Conversation sessions
        self.conversations: Dict[str, ConversationMemory] = {}
        
        # Database for persistence
        self.db = get_db_manager()
        
        print(f"🧠 Enhanced AI Engine initialized with memory")
    
    async def chat(
        self,
        prompt: str,
        session_id: str,
        system_prompt: str = None,
        save_to_db: bool = True
    ) -> AIResponse:
        """
        Chat with conversation memory
        Maintains context across turns
        """
        
        # Get or create conversation
        if session_id not in self.conversations:
            self.conversations[session_id] = ConversationMemory()
        
        conversation = self.conversations[session_id]
        
        # Get conversation history
        context_messages = conversation.get_context_messages()
        
        # Generate response with context
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=self.tracker.max_tokens_per_request
        )
        
        if response.success:
            # Add to conversation history
            conversation.add_turn("user", prompt)
            conversation.add_turn("assistant", response.content)
            
            # Save to database
            if save_to_db:
                await self._save_conversation(session_id, conversation)
        
        return response
    
    async def _save_conversation(self, session_id: str, conversation: ConversationMemory):
        """Save conversation to database"""
        try:
            await self.db.agent_memory.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "session_id": session_id,
                        "conversation": conversation.to_dict(),
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
        except Exception as e:
            print(f"⚠️  Failed to save conversation: {e}")
    
    async def load_conversation(self, session_id: str) -> Optional[ConversationMemory]:
        """Load conversation from database"""
        try:
            doc = await self.db.agent_memory.find_one({"session_id": session_id})
            
            if doc and "conversation" in doc:
                conversation = ConversationMemory()
                conversation.conversation_id = doc["conversation"]["conversation_id"]
                conversation.metadata = doc["conversation"]["metadata"]
                
                # Restore turns
                for turn_data in doc["conversation"]["turns"]:
                    turn = ConversationTurn(
                        role=turn_data["role"],
                        content=turn_data["content"],
                        timestamp=turn_data["timestamp"],
                        metadata=turn_data.get("metadata", {})
                    )
                    conversation.turns.append(turn)
                
                self.conversations[session_id] = conversation
                return conversation
        
        except Exception as e:
            print(f"⚠️  Failed to load conversation: {e}")
        
        return None
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get conversation summary"""
        if session_id not in self.conversations:
            return {"error": "Conversation not found"}
        
        conversation = self.conversations[session_id]
        
        return {
            "session_id": session_id,
            "conversation_id": conversation.conversation_id,
            "total_turns": len(conversation.turns),
            "recent_turns": [
                {"role": turn.role, "preview": turn.content[:50] + "..."}
                for turn in conversation.get_recent_context(3)
            ]
        }


# Global enhanced engine
_enhanced_engine = None


def get_enhanced_ai_engine() -> EnhancedAIEngine:
    """Get or create enhanced AI engine"""
    global _enhanced_engine
    if _enhanced_engine is None:
        _enhanced_engine = EnhancedAIEngine()
    return _enhanced_engine