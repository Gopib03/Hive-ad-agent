"""
A/B Testing System for Ad Campaigns
Test different variations and optimize performance
"""

import random
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import statistics


class TestStatus(Enum):
    """A/B test status"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class Variant:
    """Single test variant"""
    variant_id: str
    name: str
    config: Dict[str, Any]
    
    # Performance metrics
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    cost: float = 0.0
    
    @property
    def ctr(self) -> float:
        """Click-through rate"""
        return (self.clicks / self.impressions) if self.impressions > 0 else 0.0
    
    @property
    def conversion_rate(self) -> float:
        """Conversion rate"""
        return (self.conversions / self.clicks) if self.clicks > 0 else 0.0
    
    @property
    def cpc(self) -> float:
        """Cost per click"""
        return (self.cost / self.clicks) if self.clicks > 0 else 0.0
    
    @property
    def cpa(self) -> float:
        """Cost per acquisition"""
        return (self.cost / self.conversions) if self.conversions > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "variant_id": self.variant_id,
            "name": self.name,
            "config": self.config,
            "metrics": {
                "impressions": self.impressions,
                "clicks": self.clicks,
                "conversions": self.conversions,
                "cost": self.cost,
                "ctr": round(self.ctr, 4),
                "conversion_rate": round(self.conversion_rate, 4),
                "cpc": round(self.cpc, 2),
                "cpa": round(self.cpa, 2)
            }
        }


class ABTest:
    """
    A/B Test Manager
    Handles variant allocation and performance tracking
    """
    
    def __init__(
        self,
        test_id: str,
        name: str,
        variants: List[Variant],
        traffic_split: Optional[List[float]] = None
    ):
        self.test_id = test_id
        self.name = name
        self.variants = {v.variant_id: v for v in variants}
        
        # Traffic allocation
        if traffic_split is None:
            # Equal split
            n = len(variants)
            self.traffic_split = [1/n] * n
        else:
            self.traffic_split = traffic_split
        
        self.variant_ids = list(self.variants.keys())
        
        # Test metadata
        self.status = TestStatus.DRAFT
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        
        print(f"🧪 A/B Test created: {name} with {len(variants)} variants")
    
    def start(self):
        """Start the test"""
        self.status = TestStatus.RUNNING
        self.started_at = datetime.utcnow()
        print(f"🚀 A/B Test started: {self.name}")
    
    def pause(self):
        """Pause the test"""
        self.status = TestStatus.PAUSED
        print(f"⏸️  A/B Test paused: {self.name}")
    
    def complete(self):
        """Complete the test"""
        self.status = TestStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        print(f"✅ A/B Test completed: {self.name}")
    
    def assign_variant(self, user_id: Optional[str] = None) -> Variant:
        """
        Assign a variant to a user
        Uses consistent hashing if user_id provided, random otherwise
        """
        if user_id:
            # Consistent assignment based on user_id
            hash_value = hash(user_id) % 100
            cumulative = 0
            
            for i, split in enumerate(self.traffic_split):
                cumulative += split * 100
                if hash_value < cumulative:
                    return self.variants[self.variant_ids[i]]
        
        # Random assignment
        return random.choices(
            list(self.variants.values()),
            weights=self.traffic_split
        )[0]
    
    def record_impression(self, variant_id: str):
        """Record an impression"""
        if variant_id in self.variants:
            self.variants[variant_id].impressions += 1
    
    def record_click(self, variant_id: str):
        """Record a click"""
        if variant_id in self.variants:
            self.variants[variant_id].clicks += 1
    
    def record_conversion(self, variant_id: str, cost: float = 0.0):
        """Record a conversion"""
        if variant_id in self.variants:
            self.variants[variant_id].conversions += 1
            self.variants[variant_id].cost += cost
    
    def get_results(self) -> Dict[str, Any]:
        """Get test results"""
        variants_data = [v.to_dict() for v in self.variants.values()]
        
        # Calculate winner
        winner = max(
            self.variants.values(),
            key=lambda v: v.conversion_rate if v.conversions > 0 else 0
        )
        
        # Calculate statistical significance (simplified)
        significance = self._calculate_significance()
        
        return {
            "test_id": self.test_id,
            "name": self.name,
            "status": self.status.value,
            "variants": variants_data,
            "winner": {
                "variant_id": winner.variant_id,
                "name": winner.name,
                "conversion_rate": round(winner.conversion_rate, 4)
            },
            "statistical_significance": significance,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
    
    def _calculate_significance(self) -> Dict[str, Any]:
        """
        Calculate statistical significance
        Simplified Z-test for proportions
        """
        variants = list(self.variants.values())
        
        if len(variants) < 2:
            return {"significant": False, "confidence": 0.0}
        
        # Get conversion rates
        rates = [v.conversion_rate for v in variants if v.clicks > 10]
        
        if len(rates) < 2:
            return {"significant": False, "confidence": 0.0, "reason": "Insufficient data"}
        
        # Simple check: is there a clear winner?
        max_rate = max(rates)
        min_rate = min(rates)
        
        if max_rate == 0:
            return {"significant": False, "confidence": 0.0, "reason": "No conversions"}
        
        # Relative difference
        relative_diff = (max_rate - min_rate) / max_rate
        
        # Simple confidence calculation
        confidence = min(relative_diff * 100, 99.9)
        
        return {
            "significant": relative_diff > 0.1,  # 10% difference
            "confidence": round(confidence, 2),
            "relative_difference": round(relative_diff * 100, 2)
        }


class ABTestManager:
    """
    Manages multiple A/B tests
    """
    
    def __init__(self):
        self.tests: Dict[str, ABTest] = {}
        print("🧪 A/B Test Manager initialized")
    
    def create_test(
        self,
        name: str,
        variants: List[Dict[str, Any]],
        traffic_split: Optional[List[float]] = None
    ) -> ABTest:
        """
        Create new A/B test
        
        Example:
        create_test(
            name="Headline Test",
            variants=[
                {"name": "Control", "config": {"headline": "Buy Now"}},
                {"name": "Variant A", "config": {"headline": "Shop Today"}},
                {"name": "Variant B", "config": {"headline": "Get Yours"}}
            ]
        )
        """
        test_id = f"test_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Create variant objects
        variant_objects = []
        for i, var in enumerate(variants):
            variant_objects.append(Variant(
                variant_id=f"{test_id}_var_{i}",
                name=var["name"],
                config=var["config"]
            ))
        
        # Create test
        test = ABTest(
            test_id=test_id,
            name=name,
            variants=variant_objects,
            traffic_split=traffic_split
        )
        
        self.tests[test_id] = test
        
        return test
    
    def get_test(self, test_id: str) -> Optional[ABTest]:
        """Get test by ID"""
        return self.tests.get(test_id)
    
    def get_running_tests(self) -> List[ABTest]:
        """Get all running tests"""
        return [
            test for test in self.tests.values()
            if test.status == TestStatus.RUNNING
        ]
    
    def create_ad_copy_test(
        self,
        campaign_id: str,
        headlines: List[str],
        bodies: List[str]
    ) -> ABTest:
        """
        Convenience method to create ad copy test
        """
        variants = []
        for i, (headline, body) in enumerate(zip(headlines, bodies)):
            variants.append({
                "name": f"Variant {chr(65+i)}",  # A, B, C...
                "config": {
                    "headline": headline,
                    "body": body,
                    "campaign_id": campaign_id
                }
            })
        
        return self.create_test(
            name=f"Ad Copy Test - {campaign_id}",
            variants=variants
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics"""
        return {
            "total_tests": len(self.tests),
            "running": len([t for t in self.tests.values() if t.status == TestStatus.RUNNING]),
            "completed": len([t for t in self.tests.values() if t.status == TestStatus.COMPLETED]),
            "tests": [test.test_id for test in self.tests.values()]
        }


# Global test manager
_ab_test_manager = None


def get_ab_test_manager() -> ABTestManager:
    """Get or create A/B test manager"""
    global _ab_test_manager
    if _ab_test_manager is None:
        _ab_test_manager = ABTestManager()
    return _ab_test_manager