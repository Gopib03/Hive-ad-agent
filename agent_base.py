"""
HIVE AD AGENT - Base Agent System
Foundation for all AI agents
"""

from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
import asyncio
import uuid


class AgentRole(Enum):
    """Agent roles in the hive"""
    QUEEN = "queen"
    SHOPPER_BEE = "shopper_bee"
    AD_BEE = "ad_bee"


class MessageType(Enum):
    """Message types"""
    TASK = "task"
    RESULT = "result"
    QUERY = "query"


class AgentState(Enum):
    """Agent states"""
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"


@dataclass
class HiveMessage:
    """Message between agents"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    sender: str = ""
    receiver: str = ""
    content: Any = None
    msg_type: MessageType = MessageType.QUERY
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class HiveAgent(ABC):
    """Base agent class"""
    
    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        description: str
    ):
        self.agent_id = agent_id
        self.role = role
        self.description = description
        self.state = AgentState.IDLE
        self.running = False
        
        # Stats
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.messages_sent = 0
        self.messages_received = 0
        
        # Communication
        self.on_message_send: Optional[Callable] = None
    
    async def start(self):
        """Start agent"""
        self.running = True
        print(f"🐝 {self.agent_id} started")
    
    async def stop(self):
        """Stop agent"""
        self.running = False
    
    async def send_message(self, message: HiveMessage):
        """Send message"""
        message.sender = self.agent_id
        if self.on_message_send:
            await self.on_message_send(message)
        self.messages_sent += 1
    
    async def receive_message(self, message: HiveMessage):
        """Receive message"""
        self.messages_received += 1
        self.state = AgentState.THINKING
        
        response = await self.process_message(message)
        
        if response:
            await self.send_message(response)
        
        self.state = AgentState.IDLE
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent stats"""
        return {
            "agent_id": self.agent_id,
            "role": self.role.value,
            "state": self.state.value,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "messages": {
                "sent": self.messages_sent,
                "received": self.messages_received
            }
        }
    
    @abstractmethod
    async def process_message(self, message: HiveMessage) -> Optional[HiveMessage]:
        """Process message - implement in subclass"""
        pass