"""
HIVE AD AGENT - Complete Demo
Real AI with OpenAI GPT-4 & Anthropic Claude
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'agents'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'orchestration'))

from shopper_bee import ShopperBee
from ad_bee import AdBee
from queen_bee import QueenBee
from ai_engine import get_ai_engine


class Colors:
    """Terminal colors"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.END}")


def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


async def main():
    """Run complete HIVE AD AGENT demo"""
    
    # Banner
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "       🐝 HIVE AD AGENT - COMPLETE AI DEMO 🐝".center(68) + "║")
    print("║" + " "*68 + "║")
    print("║" + "     OpenAI GPT-4 & Anthropic Claude Powered".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    print(f"{Colors.END}\n")
    
    # Step 1: Initialize AI Engine
    print_header("STEP 1: INITIALIZING AI ENGINE")
    
    ai_engine = get_ai_engine()
    ai_stats = ai_engine.get_stats()
    
    print_success(f"AI Provider: {ai_stats['provider']}")
    print_success(f"AI Model: {ai_stats['model']}")
    print_info(f"Resource Limits:")
    limits = ai_stats['usage']['limits']
    print(f"  - Max tokens/request: {limits['tokens_per_request']}")
    print(f"  - Max requests/minute: {limits['requests_per_minute']}")
    print(f"  - Max cost/hour: ${limits['cost_per_hour']}")
    
    await asyncio.sleep(1)
    
    # Step 2: Initialize Hive
    print_header("STEP 2: INITIALIZING THE HIVE")
    
    # Create Queen Bee
    print_info("Creating Queen Bee (Orchestrator)...")
    queen = QueenBee()
    await queen.start()
    
    # Create Worker Bees
    print_info("Creating Shopper Bee (AI Shopping Analyst)...")
    shopper = ShopperBee()
    await shopper.start()
    queen.register_bee(shopper)
    
    print_info("Creating Ad Bee (AI Ad Strategist)...")
    ad_creator = AdBee()
    await ad_creator.start()
    queen.register_bee(ad_creator)
    
    print_success(f"Hive ready with {len(queen.worker_bees)} worker bees!")
    
    await asyncio.sleep(1)
    
    # Step 3: Execute AI Workflow
    print_header("STEP 3: EXECUTING AI-POWERED WORKFLOW")
    
    print_info("Scenario: Analyze user 'tech_lover_42' and create personalized ad campaign")
    print_info("Products: Smart Watch, Wireless Earbuds, 4K Camera")
    print()
    
    workflow_data = {
        "user_id": "tech_lover_42",
        "products": [
            {
                "id": "prod_001",
                "title": "Smart Watch Pro X",
                "price": 299.99,
                "rating": 4.7,
                "category": "Electronics"
            },
            {
                "id": "prod_002",
                "title": "Wireless Earbuds Ultra",
                "price": 149.99,
                "rating": 4.5,
                "category": "Electronics"
            },
            {
                "id": "prod_003",
                "title": "4K Action Camera",
                "price": 399.99,
                "rating": 4.8,
                "category": "Electronics"
            }
        ]
    }
    
    result = await queen.execute_workflow(
        workflow_type="full_ad_campaign",
        data=workflow_data
    )
    
    if result["success"]:
        print_success("AI Workflow completed successfully!")
        print(f"\n{Colors.BOLD}Results:{Colors.END}")
        print(f"  Workflow ID: {result['workflow_id']}")
        print(f"  Execution Time: {result['execution_time']:.2f}s")
        print(f"  Bees Involved: {', '.join(result['bees_involved'])}")
    else:
        print(f"{Colors.RED}❌ Workflow failed: {result.get('error')}{Colors.END}")
    
    await asyncio.sleep(1)
    
    # Step 4: Show Results
    print_header("STEP 4: HIVE STATUS & AI USAGE")
    
    # Hive status
    hive_status = queen.get_hive_status()
    
    print(f"{Colors.BOLD}🐝 Hive Status:{Colors.END}")
    print(f"  Total Bees: {hive_status['total_bees']}")
    print(f"  Workflows Completed: {hive_status['workflows_completed']}")
    print()
    
    # Worker bee stats
    print(f"{Colors.BOLD}Worker Bees:{Colors.END}")
    for worker in hive_status['worker_bees']:
        stats = worker['stats']
        print(f"\n  {worker['id']} ({worker['role']}):")
        print(f"    Tasks Completed: {stats['tasks_completed']}")
        print(f"    Messages: {stats['messages']['sent']} sent, {stats['messages']['received']} received")
        print(f"    State: {stats['state']}")
    
    # AI usage stats
    ai_stats = ai_engine.get_stats()
    usage = ai_stats['usage']
    
    print(f"\n{Colors.BOLD}🤖 AI Usage Statistics:{Colors.END}")
    print(f"  Total Requests: {usage['total']['requests']}")
    print(f"  Total Tokens: {usage['total']['tokens']:,}")
    print(f"  Total Cost: ${usage['total']['cost']:.4f}")
    print()
    print(f"  Current Hour:")
    print(f"    Tokens Used: {usage['current_hour']['tokens']:,} / {limits['tokens_per_hour']:,}")
    print(f"    Cost: ${usage['current_hour']['cost']:.4f} / ${limits['cost_per_hour']}")
    print()
    print(f"  Current Minute:")
    print(f"    Requests: {usage['current_minute']['requests']} / {limits['requests_per_minute']}")
    
    await asyncio.sleep(1)
    
    # Step 5: Demo Complete
    print_header("DEMO COMPLETE")
    
    print_success("HIVE AD AGENT demonstration completed!")
    print()
    print(f"{Colors.BOLD}🎓 What You Built:{Colors.END}")
    print("  ✓ AI-powered multi-agent system")
    print("  ✓ Real OpenAI GPT-4 / Claude integration")
    print("  ✓ Resource-limited AI engine")
    print("  ✓ Cost tracking and monitoring")
    print("  ✓ Shopping behavior analysis with AI")
    print("  ✓ AI-generated ad campaigns")
    print("  ✓ Agent orchestration and coordination")
    print()
    print(f"{Colors.BOLD}💡 Key Features:{Colors.END}")
    print("  • Only 2 AI providers (OpenAI + Anthropic)")
    print("  • Automatic resource management")
    print("  • Real-time cost tracking")
    print("  • Production-ready architecture")
    print()
    print(f"{Colors.BOLD}📊 Production Tips:{Colors.END}")
    print("  1. Set .env limits based on your budget")
    print("  2. Monitor AI usage in real-time")
    print("  3. Use gpt-4o-mini for cost efficiency")
    print("  4. Implement caching for repeated queries")
    print("  5. Add retry logic for failed requests")
    print()
    
    # Cleanup
    await shopper.stop()
    await ad_creator.stop()
    await queen.stop()
    
    print(f"{Colors.YELLOW}💤 All bees resting. System shutdown complete.{Colors.END}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Demo interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()