"""
HIVE AD AGENT - Intelligent Shopper Bee
AI-Powered Shopping Behavior Analyst
"""

import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agent_base import HiveAgent, AgentRole, HiveMessage, MessageType
from ai_engine import get_ai_engine
from data_connectors import get_data_connector


class ShopperBee(HiveAgent):
    """
    AI-Powered Shopping Analyst
    Uses GPT-4/Claude to analyze user behavior
    """
    
    def __init__(self, agent_id: str = "shopper_bee_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.SHOPPER_BEE,
            description="AI shopping behavior analyst"
        )
        
        # Get AI engine and data connector
        self.ai = get_ai_engine()
        self.data = get_data_connector()
        
        # AI system prompt
        self.system_prompt = """You are an expert shopping behavior analyst.
Analyze user data and provide insights on:
- Shopping personality and segment
- Purchase motivations
- Product interests
- Best engagement strategies

Be concise and data-driven."""
        
        print(f"🤖 {agent_id} initialized with AI")
    
    async def process_message(self, message: HiveMessage) -> Optional[HiveMessage]:
        """Process analysis requests"""
        
        if message.msg_type == MessageType.TASK:
            task = message.content
            
            if task.get("type") == "analyze_user":
                result = await self._analyze_user(task)
                
                return HiveMessage(
                    receiver=message.sender,
                    content=result,
                    msg_type=MessageType.RESULT
                )
        
        return None
    
    async def _analyze_user(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete AI-powered user analysis
        """
        user_id = task.get("user_id")
        
        print(f"\n🐝 {self.agent_id} analyzing user {user_id}")
        print(f"   Step 1/4: Fetching behavior data...")
        
        # Step 1: Get real-time user behavior data
        behavior_data = await self.data.get_user_behavior(user_id)
        
        print(f"   ✓ Got {behavior_data['sessions']} sessions, {behavior_data['page_views']} page views")
        print(f"   Step 2/4: AI analyzing behavior...")
        
        # Step 2: AI analyzes behavior and segments user
        segment_prompt = f"""Analyze this user's shopping behavior and classify them:

User Data:
- Sessions: {behavior_data['sessions']}
- Page Views: {behavior_data['page_views']}
- Avg Session Duration: {behavior_data['avg_session_duration']}s
- Bounce Rate: {behavior_data['bounce_rate']}
- Conversions: {behavior_data['conversions']}
- Revenue: ${behavior_data['revenue']}

Choose ONE segment:
1. impulse_buyer - Quick decisions, high frequency
2. researcher - Long sessions, reads reviews
3. bargain_hunter - Price sensitive, deal seeker
4. premium_buyer - High value, quality focused
5. casual_shopper - Occasional, need-based

Respond with JSON:
{{
  "segment": "segment_name",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation",
  "characteristics": ["trait1", "trait2"]
}}"""
        
        segment_result = await self.ai.generate_json(
            segment_prompt,
            {"segment": "string", "confidence": "number", "reasoning": "string", "characteristics": ["string"]},
            self.system_prompt
        )
        
        if "error" in segment_result:
            self.tasks_failed += 1
            return {"success": False, "error": segment_result["error"]}
        
        print(f"   ✓ AI classified as: {segment_result.get('segment', 'unknown')}")
        print(f"   Step 3/4: AI predicting interests...")
        
        # Step 3: AI predicts interests
        interests_prompt = f"""Based on this user's behavior, predict their top 5 product interests:

User Segment: {segment_result.get('segment')}
Top Pages Visited: {', '.join(behavior_data['top_pages'])}
Conversion Rate: {behavior_data['conversions']/behavior_data['sessions']:.2%}

Predict 5 specific product categories they'd be interested in.

Respond with JSON:
{{
  "interests": ["interest1", "interest2", "interest3", "interest4", "interest5"],
  "reasoning": "brief explanation"
}}"""
        
        interests_result = await self.ai.generate_json(
            interests_prompt,
            {"interests": ["string"], "reasoning": "string"},
            self.system_prompt
        )
        
        interests = interests_result.get("interests", ["Electronics", "Books", "Home"])
        
        print(f"   ✓ AI predicted interests: {', '.join(interests[:3])}...")
        print(f"   Step 4/4: Finding matching products...")
        
        # Step 4: Find matching products
        products = []
        for interest in interests[:3]:
            prods = await self.data.search_products(interest, max_results=3)
            products.extend(prods)
        
        print(f"   ✓ Found {len(products)} matching products")
        
        # Compile complete analysis
        analysis = {
            "user_id": user_id,
            "behavior_data": behavior_data,
            "ai_segment": segment_result,
            "ai_interests": interests,
            "recommended_products": products[:10],
            "analyzed_at": datetime.now().isoformat(),
            "analyzed_by": self.agent_id
        }
        
        self.tasks_completed += 1
        
        print(f"   ✅ Analysis complete!\n")
        
        return {
            "success": True,
            "analysis": analysis
        }