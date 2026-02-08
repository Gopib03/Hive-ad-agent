"""
Enhanced Shopper Bee with Memory & RAG
Uses conversation context and knowledge base
"""

import sys
import os
from typing import Dict, Any, Optional

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agent_base import HiveAgent, AgentRole, HiveMessage, MessageType
from ai.enhanced_ai_engine import get_enhanced_ai_engine
from ai.rag_system import get_knowledge_manager
from apis.real_connectors import get_analytics_connector, get_amazon_connector
from database.db_manager import get_db_manager


class EnhancedShopperBee(HiveAgent):
    """
    Enhanced Shopping Analyst with:
    - Conversation memory
    - RAG knowledge base
    - Persistent storage
    """
    
    def __init__(self, agent_id: str = "enhanced_shopper_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.SHOPPER_BEE,
            description="Enhanced AI shopping analyst with memory and RAG"
        )
        
        # Enhanced AI components
        self.ai = get_enhanced_ai_engine()
        self.knowledge = get_knowledge_manager()
        self.db = get_db_manager()
        
        # Data connectors
        self.analytics = get_analytics_connector()
        self.amazon = get_amazon_connector()
        
        # System prompt
        self.system_prompt = """You are an expert shopping behavior analyst with memory.
You can reference previous conversations and use accumulated knowledge to provide insights."""
        
        print(f"🧠 {agent_id} initialized with enhanced AI + RAG")
    
    async def process_message(self, message: HiveMessage) -> Optional[HiveMessage]:
        """Process with conversation memory"""
        
        if message.msg_type == MessageType.TASK:
            task = message.content
            session_id = task.get("session_id", "default")
            
            if task.get("type") == "analyze_user":
                result = await self._analyze_with_memory(task, session_id)
                
                return HiveMessage(
                    receiver=message.sender,
                    content=result,
                    msg_type=MessageType.RESULT
                )
        
        return None
    
    async def _analyze_with_memory(
        self,
        task: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """
        Analyze user with conversation memory and RAG
        """
        user_id = task.get("user_id")
        
        print(f"\n🧠 {self.agent_id} analyzing with enhanced AI")
        print(f"   Session: {session_id}")
        
        # Step 1: Get behavior data
        behavior_data = await self.analytics.get_user_behavior(user_id)
        
        # Step 2: Get relevant knowledge from RAG
        segment_query = f"Best strategy for user with {behavior_data['sessions']} sessions and {behavior_data['conversions']} conversions"
        rag_context = self.knowledge.rag.get_context_for_prompt(segment_query, n_results=2)
        
        print(f"   📚 Retrieved RAG context: {len(rag_context)} chars")
        
        # Step 3: Analyze with conversation memory
        analysis_prompt = f"""Analyze this shopper using context and data:

Previous Knowledge:
{rag_context}

Current User Data:
- Sessions: {behavior_data['sessions']}
- Page Views: {behavior_data['page_views']}
- Conversions: {behavior_data['conversions']}
- Revenue: ${behavior_data['revenue']}

Provide:
1. User segment classification
2. Key behavioral insights
3. Recommended approach

Format as JSON."""
        
        response = await self.ai.chat(
            prompt=analysis_prompt,
            session_id=session_id,
            system_prompt=self.system_prompt
        )
        
        # Step 4: Save analysis to database
        analysis_result = {
            "user_id": user_id,
            "session_id": session_id,
            "behavior_data": behavior_data,
            "ai_analysis": response.content if response.success else "Analysis failed",
            "rag_used": bool(rag_context),
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        await self.db.save_workflow({
            "workflow_type": "shopper_analysis",
            "agent_id": self.agent_id,
            "result": analysis_result
        })
        
        self.tasks_completed += 1
        
        print(f"   ✅ Enhanced analysis complete!\n")
        
        return {
            "success": True,
            "analysis": analysis_result,
            "enhanced_features": {
                "conversation_memory": True,
                "rag_context": True,
                "database_saved": True
            }
        }