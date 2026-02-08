"""
HIVE AD AGENT - Queen Bee Orchestrator
AI-Powered Master Coordinator
"""

import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agent_base import HiveAgent, AgentRole, HiveMessage, MessageType


class QueenBee(HiveAgent):
    """
    Master Orchestrator
    Coordinates all worker bees
    """
    
    def __init__(self, agent_id: str = "queen_bee_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.QUEEN,
            description="Master orchestrator"
        )
        
        # Worker bees registry
        self.worker_bees: Dict[str, Dict[str, Any]] = {}
        
        # System metrics
        self.workflows_completed = 0
        self.workflows_failed = 0
        
        print(f"👑 {agent_id} initialized")
    
    def register_bee(self, bee: HiveAgent):
        """Register a worker bee"""
        self.worker_bees[bee.agent_id] = {
            "bee": bee,
            "role": bee.role
        }
        
        # Set up message routing
        bee.on_message_send = self.route_message
        
        print(f"👑 Registered: {bee.agent_id} ({bee.role.value})")
    
    async def route_message(self, message: HiveMessage):
        """Route messages between bees"""
        receiver_id = message.receiver
        
        if receiver_id in self.worker_bees:
            bee = self.worker_bees[receiver_id]["bee"]
            await bee.receive_message(message)
    
    async def process_message(self, message: HiveMessage) -> Optional[HiveMessage]:
        """Process orchestration requests"""
        # Queen doesn't process messages directly
        return None
    
    async def execute_workflow(
        self,
        workflow_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute complete workflow
        Coordinates worker bees to complete complex task
        """
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        print(f"\n👑 WORKFLOW START: {workflow_id}")
        print(f"   Type: {workflow_type}")
        
        start_time = datetime.now()
        
        try:
            if workflow_type == "full_ad_campaign":
                result = await self._full_campaign_workflow(data)
            else:
                result = {"success": False, "error": "Unknown workflow"}
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            if result.get("success"):
                self.workflows_completed += 1
                print(f"   ✅ Workflow completed in {execution_time:.2f}s\n")
            else:
                self.workflows_failed += 1
                print(f"   ❌ Workflow failed\n")
            
            result["workflow_id"] = workflow_id
            result["execution_time"] = execution_time
            
            return result
            
        except Exception as e:
            self.workflows_failed += 1
            print(f"   ❌ Workflow error: {e}\n")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def _full_campaign_workflow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete workflow: User Analysis → Ad Campaign
        """
        user_id = data.get("user_id")
        
        # Step 1: Get shopper bee to analyze user
        shopper_bee_id = self._find_bee_by_role(AgentRole.SHOPPER_BEE)
        if not shopper_bee_id:
            return {"success": False, "error": "Shopper bee not found"}
        
        print(f"   📊 Delegating to {shopper_bee_id}...")
        
        # Send task to shopper bee
        shopper_message = HiveMessage(
            sender=self.agent_id,
            receiver=shopper_bee_id,
            content={"type": "analyze_user", "user_id": user_id},
            msg_type=MessageType.TASK
        )
        
        await self.route_message(shopper_message)
        
        # Wait for analysis to complete
        await asyncio.sleep(0.5)  # Simulate async processing
        
        shopper_bee = self.worker_bees[shopper_bee_id]["bee"]
        
        # Check if analysis completed
        if shopper_bee.tasks_completed == 0:
            return {"success": False, "error": "Shopper analysis failed"}
        
        # Get analysis result (in production, would retrieve from message queue)
        # For demo, we'll create a simplified flow
        
        # Step 2: Get ad bee to create campaign
        ad_bee_id = self._find_bee_by_role(AgentRole.AD_BEE)
        if not ad_bee_id:
            return {"success": False, "error": "Ad bee not found"}
        
        print(f"   📢 Delegating to {ad_bee_id}...")
        
        # Send task to ad bee (with shopper analysis)
        ad_message = HiveMessage(
            sender=self.agent_id,
            receiver=ad_bee_id,
            content={
                "type": "create_campaign",
                "shopper_analysis": {
                    "ai_segment": {"segment": "tech_enthusiast"},
                    "ai_interests": ["Electronics", "Gadgets", "Tech"],
                    "recommended_products": data.get("products", [])
                }
            },
            msg_type=MessageType.TASK
        )
        
        await self.route_message(ad_message)
        
        # Wait for campaign creation
        await asyncio.sleep(0.5)
        
        ad_bee = self.worker_bees[ad_bee_id]["bee"]
        
        # Check if campaign completed
        if ad_bee.tasks_completed == 0:
            return {"success": False, "error": "Campaign creation failed"}
        
        return {
            "success": True,
            "message": "Complete workflow executed",
            "bees_involved": [shopper_bee_id, ad_bee_id]
        }
    
    def _find_bee_by_role(self, role: AgentRole) -> Optional[str]:
        """Find bee by role"""
        for bee_id, bee_info in self.worker_bees.items():
            if bee_info["role"] == role:
                return bee_id
        return None
    
    def get_hive_status(self) -> Dict[str, Any]:
        """Get complete hive status"""
        return {
            "queen_id": self.agent_id,
            "total_bees": len(self.worker_bees),
            "workflows_completed": self.workflows_completed,
            "workflows_failed": self.workflows_failed,
            "worker_bees": [
                {
                    "id": bee_id,
                    "role": info["role"].value,
                    "stats": info["bee"].get_stats()
                }
                for bee_id, info in self.worker_bees.items()
            ]
        }