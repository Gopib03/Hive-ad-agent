"""
RAG System - Retrieval Augmented Generation
Combines AI with knowledge base search
"""

import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from datetime import datetime


class RAGSystem:
    """
    Retrieval Augmented Generation System
    
    Features:
    - Vector database for knowledge storage
    - Semantic search
    - Context injection into AI prompts
    - Knowledge base management
    """
    
    def __init__(self, collection_name: str = "hive_knowledge"):
        # Initialize ChromaDB
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./data/chroma"
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "HIVE AD AGENT knowledge base"}
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print(f"🔍 RAG System initialized: {collection_name}")
    
    def add_knowledge(
        self,
        text: str,
        metadata: Dict[str, Any],
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add knowledge to vector database
        """
        if doc_id is None:
            doc_id = f"doc_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        
        # Add to collection
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        return doc_id
    
    def add_knowledge_batch(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        doc_ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add multiple knowledge items"""
        if doc_ids is None:
            doc_ids = [
                f"doc_{i}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
                for i in range(len(texts))
            ]
        
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=doc_ids
        )
        
        return doc_ids
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Search knowledge base
        Returns relevant documents
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                    "id": results["ids"][0][i] if results["ids"] else None
                })
        
        return {
            "query": query,
            "results": formatted_results,
            "count": len(formatted_results)
        }
    
    def get_context_for_prompt(
        self,
        query: str,
        n_results: int = 3
    ) -> str:
        """
        Get relevant context formatted for AI prompt
        """
        search_results = self.search(query, n_results)
        
        if not search_results["results"]:
            return ""
        
        context_parts = []
        for i, result in enumerate(search_results["results"], 1):
            context_parts.append(f"[Source {i}]: {result['text']}")
        
        return "\n\n".join(context_parts)
    
    async def augmented_generate(
        self,
        ai_engine,
        query: str,
        system_prompt: str = None,
        n_context: int = 3
    ):
        """
        Generate AI response with RAG
        Retrieves relevant context and includes in prompt
        """
        
        # Get relevant context
        context = self.get_context_for_prompt(query, n_context)
        
        # Build augmented prompt
        if context:
            augmented_prompt = f"""Use the following context to answer the query:

Context:
{context}

Query: {query}

Answer based on the context above:"""
        else:
            augmented_prompt = query
        
        # Generate with AI
        response = await ai_engine.generate(
            prompt=augmented_prompt,
            system_prompt=system_prompt
        )
        
        return response
    
    def delete_knowledge(self, doc_id: str) -> bool:
        """Delete knowledge by ID"""
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            print(f"Error deleting knowledge: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        count = self.collection.count()
        
        return {
            "collection_name": self.collection.name,
            "total_documents": count,
            "embedding_model": "all-MiniLM-L6-v2"
        }


class KnowledgeManager:
    """
    Manages knowledge base for the hive
    Handles product data, user insights, campaign learnings
    """
    
    def __init__(self):
        self.rag = RAGSystem()
        
        # Initialize with base knowledge
        self._initialize_base_knowledge()
        
        print("📚 Knowledge Manager initialized")
    
    def _initialize_base_knowledge(self):
        """Initialize with base advertising knowledge"""
        base_knowledge = [
            {
                "text": "Impulse buyers respond best to urgency messaging like 'Limited Time' and 'Act Now'. They prefer short, direct copy with clear calls-to-action.",
                "metadata": {"type": "segment_strategy", "segment": "impulse_buyer"}
            },
            {
                "text": "Researchers need detailed information, comparisons, and social proof. Include product specifications, reviews, and ratings in ads.",
                "metadata": {"type": "segment_strategy", "segment": "researcher"}
            },
            {
                "text": "Bargain hunters are motivated by discounts and savings. Emphasize price reductions, deals, and value propositions prominently.",
                "metadata": {"type": "segment_strategy", "segment": "bargain_hunter"}
            },
            {
                "text": "Premium buyers value quality over price. Focus on exclusivity, craftsmanship, and premium features in messaging.",
                "metadata": {"type": "segment_strategy", "segment": "premium_buyer"}
            },
            {
                "text": "Optimal CTR for e-commerce ads ranges from 2-5%. Conversion rates typically fall between 1-3% depending on product category.",
                "metadata": {"type": "performance_benchmark", "category": "general"}
            }
        ]
        
        texts = [item["text"] for item in base_knowledge]
        metadatas = [item["metadata"] for item in base_knowledge]
        
        self.rag.add_knowledge_batch(texts, metadatas)
    
    async def get_segment_strategy(self, segment: str, ai_engine) -> str:
        """Get AI-powered strategy for user segment using RAG"""
        query = f"What is the best advertising strategy for {segment}?"
        
        response = await self.rag.augmented_generate(
            ai_engine=ai_engine,
            query=query,
            system_prompt="You are an advertising expert. Provide specific, actionable strategies.",
            n_context=2
        )
        
        return response.content if response.success else ""
    
    def add_campaign_learning(
        self,
        campaign_id: str,
        learning: str,
        performance_data: Dict[str, Any]
    ):
        """Add learning from campaign performance"""
        self.rag.add_knowledge(
            text=learning,
            metadata={
                "type": "campaign_learning",
                "campaign_id": campaign_id,
                "ctr": performance_data.get("ctr"),
                "conversion_rate": performance_data.get("conversion_rate"),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def add_product_insight(self, product_id: str, insight: str):
        """Add product-specific insight"""
        self.rag.add_knowledge(
            text=insight,
            metadata={
                "type": "product_insight",
                "product_id": product_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# Global knowledge manager
_knowledge_manager = None


def get_knowledge_manager() -> KnowledgeManager:
    """Get or create knowledge manager"""
    global _knowledge_manager
    if _knowledge_manager is None:
        _knowledge_manager = KnowledgeManager()
    return _knowledge_manager