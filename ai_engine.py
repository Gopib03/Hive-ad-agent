"""
HIVE AD AGENT - AI Engine
2 Providers Only: OpenAI GPT-4 & Anthropic Claude
With Resource Management and Cost Tracking
"""

import os
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json

load_dotenv()

# Import AI SDKs
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI not available. Install: pip install openai")

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️  Anthropic not available. Install: pip install anthropic")


class AIProvider(Enum):
    """Available AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class AIResponse:
    """Standardized AI response"""
    content: str
    model: str
    tokens_used: int
    cost_usd: float
    provider: str
    success: bool = True
    error: Optional[str] = None


class ResourceTracker:
    """Track API usage and enforce limits"""
    
    def __init__(self):
        # Get limits from environment or use defaults
        self.max_tokens_per_request = int(os.getenv("MAX_TOKENS_PER_REQUEST", 2000))
        self.max_requests_per_minute = int(os.getenv("MAX_REQUESTS_PER_MINUTE", 10))
        self.max_cost_per_hour = float(os.getenv("MAX_COST_PER_HOUR", 5.0))
        self.max_tokens_per_hour = int(os.getenv("MAX_TOKENS_PER_HOUR", 100000))
        
        # Tracking variables
        self.minute_requests = []
        self.hour_tokens = 0
        self.hour_cost = 0.0
        self.hour_start = datetime.now()
        
        # Total stats
        self.total_requests = 0
        self.total_tokens = 0
        self.total_cost = 0.0
    
    def _reset_if_needed(self):
        """Reset counters if time periods elapsed"""
        now = datetime.now()
        
        # Reset minute counter
        self.minute_requests = [t for t in self.minute_requests if (now - t).seconds < 60]
        
        # Reset hour counters
        if (now - self.hour_start).seconds >= 3600:
            self.hour_tokens = 0
            self.hour_cost = 0.0
            self.hour_start = now
    
    async def check_limits(self, estimated_tokens: int) -> tuple[bool, str]:
        """Check if request is within limits"""
        self._reset_if_needed()
        
        # Check requests per minute
        if len(self.minute_requests) >= self.max_requests_per_minute:
            wait_time = 60 - (datetime.now() - self.minute_requests[0]).seconds
            return False, f"Rate limit reached. Wait {wait_time}s"
        
        # Check tokens per hour
        if self.hour_tokens + estimated_tokens > self.max_tokens_per_hour:
            return False, f"Token limit reached ({self.max_tokens_per_hour}/hour)"
        
        # Check cost per hour
        estimated_cost = (estimated_tokens / 1000) * 0.03  # Rough estimate
        if self.hour_cost + estimated_cost > self.max_cost_per_hour:
            return False, f"Cost limit reached (${self.max_cost_per_hour}/hour)"
        
        return True, "OK"
    
    def record_usage(self, tokens: int, cost: float):
        """Record API usage"""
        now = datetime.now()
        
        self.minute_requests.append(now)
        self.hour_tokens += tokens
        self.hour_cost += cost
        
        self.total_requests += 1
        self.total_tokens += tokens
        self.total_cost += cost
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "total": {
                "requests": self.total_requests,
                "tokens": self.total_tokens,
                "cost": round(self.total_cost, 4)
            },
            "current_hour": {
                "tokens": self.hour_tokens,
                "cost": round(self.hour_cost, 4)
            },
            "current_minute": {
                "requests": len(self.minute_requests)
            },
            "limits": {
                "tokens_per_request": self.max_tokens_per_request,
                "requests_per_minute": self.max_requests_per_minute,
                "tokens_per_hour": self.max_tokens_per_hour,
                "cost_per_hour": self.max_cost_per_hour
            }
        }


class AIEngine:
    """
    Unified AI Engine
    Supports: OpenAI GPT-4 & Anthropic Claude
    Features: Resource limits, cost tracking, automatic failover
    """
    
    def __init__(
        self,
        provider: AIProvider = None,
        model: str = None
    ):
        # Determine provider
        if provider is None:
            provider_name = os.getenv("AI_PROVIDER", "openai").lower()
            provider = AIProvider.OPENAI if provider_name == "openai" else AIProvider.ANTHROPIC
        
        self.provider = provider
        
        # Set model
        if model:
            self.model = model
        else:
            if self.provider == AIProvider.OPENAI:
                self.model = "gpt-4o-mini"  # Cheaper and faster
            else:
                self.model = "claude-3-5-sonnet-20241022"
        
        # Initialize clients
        self.openai_client = None
        self.anthropic_client = None
        
        if self.provider == AIProvider.OPENAI and OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = AsyncOpenAI(api_key=api_key)
            else:
                print("❌ OPENAI_API_KEY not found in .env")
        
        if self.provider == AIProvider.ANTHROPIC and ANTHROPIC_AVAILABLE:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.anthropic_client = AsyncAnthropic(api_key=api_key)
            else:
                print("❌ ANTHROPIC_API_KEY not found in .env")
        
        # Resource tracker
        self.tracker = ResourceTracker()
        
        print(f"🤖 AI Engine: {self.provider.value} | Model: {self.model}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        max_tokens: int = None
    ) -> AIResponse:
        """
        Generate AI response
        Main method for all AI interactions
        """
        if max_tokens is None:
            max_tokens = self.tracker.max_tokens_per_request
        
        # Check resource limits
        can_proceed, message = await self.tracker.check_limits(max_tokens)
        if not can_proceed:
            return AIResponse(
                content="",
                model=self.model,
                tokens_used=0,
                cost_usd=0.0,
                provider=self.provider.value,
                success=False,
                error=f"Resource limit: {message}"
            )
        
        # Generate based on provider
        try:
            if self.provider == AIProvider.OPENAI:
                return await self._openai_generate(prompt, system_prompt, max_tokens)
            else:
                return await self._anthropic_generate(prompt, system_prompt, max_tokens)
        except Exception as e:
            return AIResponse(
                content="",
                model=self.model,
                tokens_used=0,
                cost_usd=0.0,
                provider=self.provider.value,
                success=False,
                error=str(e)
            )
    
    async def _openai_generate(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int
    ) -> AIResponse:
        """OpenAI implementation"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        tokens_used = response.usage.total_tokens
        
        # Calculate cost (GPT-4o-mini pricing)
        input_cost = (response.usage.prompt_tokens / 1000) * 0.00015
        output_cost = (response.usage.completion_tokens / 1000) * 0.0006
        total_cost = input_cost + output_cost
        
        # Record usage
        self.tracker.record_usage(tokens_used, total_cost)
        
        return AIResponse(
            content=response.choices[0].message.content,
            model=self.model,
            tokens_used=tokens_used,
            cost_usd=total_cost,
            provider="openai",
            success=True
        )
    
    async def _anthropic_generate(
        self,
        prompt: str,
        system_prompt: str,
        max_tokens: int
    ) -> AIResponse:
        """Anthropic implementation"""
        if not self.anthropic_client:
            raise Exception("Anthropic client not initialized")
        
        response = await self.anthropic_client.messages.create(
            model=self.model,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        tokens_used = response.usage.input_tokens + response.usage.output_tokens
        
        # Calculate cost (Claude Sonnet pricing)
        input_cost = (response.usage.input_tokens / 1000) * 0.003
        output_cost = (response.usage.output_tokens / 1000) * 0.015
        total_cost = input_cost + output_cost
        
        # Record usage
        self.tracker.record_usage(tokens_used, total_cost)
        
        return AIResponse(
            content=response.content[0].text,
            model=self.model,
            tokens_used=tokens_used,
            cost_usd=total_cost,
            provider="anthropic",
            success=True
        )
    
    async def generate_json(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_prompt: str = None
    ) -> Dict[str, Any]:
        """Generate structured JSON response"""
        
        json_prompt = f"""{prompt}

Respond with valid JSON matching this schema:
{json.dumps(schema, indent=2)}

JSON Response:"""
        
        response = await self.generate(json_prompt, system_prompt)
        
        if not response.success:
            return {"error": response.error}
        
        try:
            # Clean and parse JSON
            content = response.content.strip()
            
            # Remove markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content.strip())
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON: {str(e)}", "raw": response.content}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "usage": self.tracker.get_stats()
        }


# Global engine instance
_engine = None


def get_ai_engine() -> AIEngine:
    """Get or create global AI engine"""
    global _engine
    if _engine is None:
        _engine = AIEngine()
    return _engine


# Convenience function
async def ai_generate(prompt: str, system: str = None) -> str:
    """Quick AI generation"""
    engine = get_ai_engine()
    response = await engine.generate(prompt, system)
    return response.content if response.success else f"Error: {response.error}"