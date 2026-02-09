"""
Enhanced AI Demo
Shows: Memory, RAG, A/B Testing
"""

import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database.db_manager import init_database
from ai.enhanced_ai_engine import get_enhanced_ai_engine
from ai.rag_system import get_knowledge_manager
from testing.ab_testing import get_ab_test_manager


async def demo_conversation_memory():
    """Demo 1: Conversation Memory"""
    print("\n" + "="*70)
    print("DEMO 1: CONVERSATION MEMORY")
    print("="*70 + "\n")
    
    ai = get_enhanced_ai_engine()
    session_id = "demo_session_001"
    
    # Turn 1
    print("User: What's a good strategy for impulse buyers?")
    response1 = await ai.chat(
        "What's a good strategy for impulse buyers?",
        session_id=session_id,
        system_prompt="You are an advertising expert."
    )
    print(f"AI: {response1.content[:200]}...\n")
    
    # Turn 2 - References previous conversation
    print("User: Can you give me 3 specific examples?")
    response2 = await ai.chat(
        "Can you give me 3 specific examples?",
        session_id=session_id,
        system_prompt="You are an advertising expert."
    )
    print(f"AI: {response2.content[:200]}...\n")
    
    # Show conversation summary
    summary = ai.get_conversation_summary(session_id)
    print(f"Conversation Summary: {summary['total_turns']} turns")
    print(f"Cost: ${response1.cost_usd + response2.cost_usd:.4f}\n")


async def demo_rag_system():
    """Demo 2: RAG System"""
    print("\n" + "="*70)
    print("DEMO 2: RAG (Retrieval Augmented Generation)")
    print("="*70 + "\n")
    
    knowledge = get_knowledge_manager()
    ai = get_enhanced_ai_engine()
    
    # Add custom knowledge
    print("Adding custom knowledge...")
    knowledge.rag.add_knowledge(
        "Black Friday campaigns perform 3x better with countdown timers and stock scarcity messaging.",
        metadata={"type": "seasonal_strategy", "event": "black_friday"}
    )
    
    # Search knowledge base
    print("\nSearching: 'Black Friday strategy'")
    results = knowledge.rag.search("Black Friday strategy", n_results=3)
    
    for i, result in enumerate(results["results"], 1):
        print(f"\n[Result {i}]")
        print(f"Text: {result['text'][:100]}...")
        print(f"Metadata: {result['metadata']}")
    
    # Generate with RAG
    print("\n\nGenerating AI response with RAG context...")
    response = await knowledge.rag.augmented_generate(
        ai_engine=ai,
        query="How should I run a Black Friday campaign?",
        system_prompt="You are an advertising strategist.",
        n_context=2
    )
    
    print(f"\nAI Response (with RAG):")
    print(response.content[:300] + "...\n")


async def demo_ab_testing():
    """Demo 3: A/B Testing"""
    print("\n" + "="*70)
    print("DEMO 3: A/B TESTING SYSTEM")
    print("="*70 + "\n")
    
    ab_manager = get_ab_test_manager()
    
    # Create ad copy test
    print("Creating A/B test for ad headlines...")
    test = ab_manager.create_ad_copy_test(
        campaign_id="camp_001",
        headlines=[
            "Buy Now and Save 50%",
            "Limited Time: Half Off Everything",
            "Get 50% Off Today Only"
        ],
        bodies=[
            "Don't miss this amazing deal",
            "Shop now before it's gone",
            "Exclusive offer for you"
        ]
    )
    
    test.start()
    
    # Simulate traffic
    print("\nSimulating test traffic...")
    import random
    
    for _ in range(1000):
        # Assign variant
        variant = test.assign_variant(f"user_{random.randint(1, 500)}")
        
        # Record impression
        test.record_impression(variant.variant_id)
        
        # Simulate click (3% CTR baseline)
        if random.random() < 0.03:
            test.record_click(variant.variant_id)
            
            # Simulate conversion (10% of clicks)
            if random.random() < 0.10:
                test.record_conversion(variant.variant_id, cost=5.0)
    
    test.complete()
    
    # Show results
    results = test.get_results()
    
    print("\nTest Results:")
    print(f"Status: {results['status']}")
    print(f"\nVariants:")
    
    for variant in results['variants']:
        print(f"\n  {variant['name']}:")
        print(f"    Impressions: {variant['metrics']['impressions']}")
        print(f"    Clicks: {variant['metrics']['clicks']}")
        print(f"    CTR: {variant['metrics']['ctr']:.2%}")
        print(f"    Conversions: {variant['metrics']['conversions']}")
        print(f"    Conversion Rate: {variant['metrics']['conversion_rate']:.2%}")
    
    print(f"\n🏆 Winner: {results['winner']['name']}")
    print(f"   Conversion Rate: {results['winner']['conversion_rate']:.2%}")
    print(f"   Statistical Significance: {results['statistical_significance']}\n")


async def main():
    """Run all enhanced demos"""
    
    print("\n" + "="*70)
    print("🧠 HIVE AD AGENT - ENHANCED AI FEATURES DEMO")
    print("="*70)
    
    # Initialize database
    print("\nInitializing database...")
    await init_database()
    
    # Run demos
    await demo_conversation_memory()
    await demo_rag_system()
    await demo_ab_testing()
    
    print("\n" + "="*70)
    print("✅ ALL ENHANCED FEATURES DEMONSTRATED")
    print("="*70)
    print("\nFeatures:")
    print("  ✓ Conversation Memory - Multi-turn context")
    print("  ✓ RAG System - Knowledge base integration")
    print("  ✓ A/B Testing - Campaign optimization")
    print("  ✓ Database Persistence - MongoDB storage")
    print()


if __name__ == "__main__":
    asyncio.run(main())