"""
HIVE AD AGENT - Data Connectors
Simulated real-time data sources
In production, replace with actual API calls
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import random


class DataConnector:
    """Simulated data connector for demo purposes"""
    
    @staticmethod
    async def get_user_behavior(user_id: str) -> Dict[str, Any]:
        """Get user behavior data (simulated Google Analytics)"""
        # Generate deterministic but realistic data based on user_id
        seed = hash(user_id) % 1000
        random.seed(seed)
        
        sessions = 10 + random.randint(5, 30)
        page_views = sessions * random.randint(3, 8)
        
        return {
            "user_id": user_id,
            "sessions": sessions,
            "page_views": page_views,
            "avg_session_duration": 120 + random.randint(60, 300),
            "bounce_rate": round(0.2 + random.random() * 0.4, 2),
            "conversions": random.randint(1, 8),
            "revenue": round(100 + random.random() * 500, 2),
            "top_pages": [
                "/products/electronics",
                "/products/books",
                "/cart",
                "/checkout"
            ],
            "devices": {
                "desktop": 0.6,
                "mobile": 0.3,
                "tablet": 0.1
            },
            "time_period": {
                "start": (datetime.now() - timedelta(days=30)).isoformat(),
                "end": datetime.now().isoformat()
            }
        }
    
    @staticmethod
    async def search_products(keywords: str, max_results: int = 10) -> List[Dict]:
        """Search products (simulated Amazon API)"""
        products = []
        for i in range(max_results):
            products.append({
                "id": f"prod_{i+1:03d}",
                "title": f"{keywords} - Product {i+1}",
                "price": round(29.99 + (i * 15.5), 2),
                "rating": round(3.5 + (random.random() * 1.5), 1),
                "reviews": 50 + (i * 30),
                "category": "Electronics",
                "in_stock": True,
                "image_url": f"https://example.com/product_{i+1}.jpg"
            })
        return products
    
    @staticmethod
    async def get_trending_topics() -> List[Dict]:
        """Get trending topics (simulated social media)"""
        return [
            {"topic": "#TechDeals", "volume": 15000, "sentiment": "positive"},
            {"topic": "#SmartHome", "volume": 12000, "sentiment": "neutral"},
            {"topic": "#Gadgets2024", "volume": 10000, "sentiment": "positive"},
            {"topic": "#ShoppingOnline", "volume": 8000, "sentiment": "neutral"}
        ]


# Global connector
_connector = None


def get_data_connector() -> DataConnector:
    """Get data connector"""
    global _connector
    if _connector is None:
        _connector = DataConnector()
    return _connector