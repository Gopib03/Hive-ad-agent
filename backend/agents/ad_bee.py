"""
HIVE AD AGENT - Intelligent Ad Bee
AI-Powered Ad Campaign Creator
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


class AdBee(HiveAgent):
    """
    AI-Powered Ad Strategist
    Uses GPT-4/Claude to create campaigns
    """
    
    def __init__(self, agent_id: str = "ad_bee_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.AD_BEE,
            description="AI advertising strategist"
        )
        
        # Get AI engine and data
        self.ai = get_ai_engine()
        self.data = get_data_connector()
        
        # AI system prompt
        self.system_prompt = """You are an expert advertising strategist.
Create data-driven, personalized ad campaigns that:
- Match user psychology
- Leverage trends
- Optimize for conversions
- Use compelling copy

Be creative and strategic."""
        
        print(f"🤖 {agent_id} initialized with AI")
    
    async def process_message(self, message: HiveMessage) -> Optional[HiveMessage]:
        """Process campaign requests"""
        
        if message.msg_type == MessageType.TASK:
            task = message.content
            
            if task.get("type") == "create_campaign":
                result = await self._create_campaign(task)
                
                return HiveMessage(
                    receiver=message.sender,
                    content=result,
                    msg_type=MessageType.RESULT
                )
        
        return None
    
    async def _create_campaign(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete AI-powered campaign creation
        """
        shopper_analysis = task.get("shopper_analysis", {})
        
        print(f"\n🐝 {self.agent_id} creating ad campaign")
        print(f"   Step 1/4: Analyzing trends...")
        
        # Step 1: Get trending topics
        trends = await self.data.get_trending_topics()
        
        print(f"   ✓ Found {len(trends)} trending topics")
        print(f"   Step 2/4: AI creating campaign strategy...")
        
        # Step 2: AI creates campaign strategy
        segment = shopper_analysis.get("ai_segment", {}).get("segment", "casual_shopper")
        interests = shopper_analysis.get("ai_interests", [])
        products = shopper_analysis.get("recommended_products", [])[:3]
        
        strategy_prompt = f"""Create a complete ad campaign strategy:

Target Audience:
- Segment: {segment}
- Interests: {', '.join(interests)}
- Behavior: {shopper_analysis.get('ai_segment', {}).get('characteristics', [])}

Available Products:
{json.dumps(products, indent=2)}

Trending Topics:
{', '.join([t['topic'] for t in trends[:3]])}

Create a campaign with:
1. Campaign name and objective
2. Key messaging approach
3. Budget allocation strategy
4. Target metrics (CTR, conversion rate, ROAS)

Respond with JSON:
{{
  "campaign_name": "creative name",
  "objective": "primary goal",
  "messaging_approach": "strategy description",
  "budget": {{
    "daily": 100,
    "total": 3000
  }},
  "target_metrics": {{
    "ctr": 0.03,
    "conversion_rate": 0.01,
    "roas": 4.0
  }},
  "duration_days": 30
}}"""
        
        strategy_result = await self.ai.generate_json(
            strategy_prompt,
            {
                "campaign_name": "string",
                "objective": "string",
                "messaging_approach": "string",
                "budget": {"daily": "number", "total": "number"},
                "target_metrics": {"ctr": "number", "conversion_rate": "number", "roas": "number"},
                "duration_days": "number"
            },
            self.system_prompt
        )
        
        if "error" in strategy_result:
            self.tasks_failed += 1
            return {"success": False, "error": strategy_result["error"]}
        
        print(f"   ✓ Campaign strategy: {strategy_result.get('campaign_name', 'Untitled')}")
        print(f"   Step 3/4: AI generating ad copy...")
        
        # Step 3: AI generates ad copy for each product
        ad_creatives = []
        
        for i, product in enumerate(products[:2], 1):  # Generate for top 2 products
            copy_prompt = f"""Create compelling ad copy for this product targeting {segment}:

Product: {product['title']}
Price: ${product['price']}
Rating: {product['rating']}⭐

Trending Context: {trends[0]['topic']}

Create ad copy with:
- Attention-grabbing headline (8 words max)
- Persuasive body text (20 words max)
- Strong call-to-action (3 words max)

Match the {segment} psychology.

Respond with JSON:
{{
  "headline": "headline text",
  "body": "body text",
  "cta": "CTA text",
  "tone": "emotional tone"
}}"""
            
            copy_result = await self.ai.generate_json(
                copy_prompt,
                {"headline": "string", "body": "string", "cta": "string", "tone": "string"},
                self.system_prompt
            )
            
            if "error" not in copy_result:
                ad_creatives.append({
                    "product_id": product['id'],
                    "product_title": product['title'],
                    "ad_copy": copy_result,
                    "format": "video_overlay",
                    "duration_seconds": 15
                })
                print(f"   ✓ Generated ad {i}/2")
        
        print(f"   Step 4/4: Finalizing campaign...")
        
        # Step 4: Compile complete campaign
        campaign = {
            "campaign_id": f"camp_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "strategy": strategy_result,
            "ad_creatives": ad_creatives,
            "target_audience": {
                "segment": segment,
                "interests": interests,
                "products_matched": len(products)
            },
            "trending_aligned": [t['topic'] for t in trends[:3]],
            "created_at": datetime.now().isoformat(),
            "created_by": self.agent_id
        }
        
        self.tasks_completed += 1
        
        print(f"   ✅ Campaign created!\n")
        
        return {
            "success": True,
            "campaign": campaign
        }