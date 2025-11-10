"""Utility functions."""
import re
import uuid
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta


def parse_mentions(text: str) -> List[str]:
    """Extract @mentions from text."""
    pattern = r'@(\w+)'
    mentions = re.findall(pattern, text)
    return list(set(mentions))  # Remove duplicates


def is_critique(text: str) -> bool:
    """Check if message contains critique keyword."""
    return "critique" in text.lower()


def parse_critique_target(text: str) -> Optional[tuple]:
    """Parse critique target from text.
    Returns (model_name, index) or None.
    Example: '@claude critique @gpt #2' -> ('gpt', 2)
    """
    # Look for explicit target with index
    match = re.search(r'critique\s+@(\w+)\s+#(\d+)', text, re.IGNORECASE)
    if match:
        return (match.group(1), int(match.group(2)))

    # Look for explicit target without index
    match = re.search(r'critique\s+@(\w+)', text, re.IGNORECASE)
    if match:
        return (match.group(1), 1)  # Default to most recent

    return None


def generate_id() -> str:
    """Generate unique ID."""
    return str(uuid.uuid4())


def calculate_cost(provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Calculate cost based on provider pricing (as of Nov 2024)."""
    # Pricing per 1M tokens
    pricing = {
        "openai": {
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4-turbo": {"input": 10.00, "output": 30.00},
            "default": {"input": 0.15, "output": 0.60}
        },
        "anthropic": {
            "claude-haiku-4-5-20251001": {"input": 1.00, "output": 5.00},
            "claude-3-7-sonnet-20250219": {"input": 3.00, "output": 15.00},
            "claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00},
            "default": {"input": 3.00, "output": 15.00}
        },
        "gemini": {
            "gemini-2.0-flash-exp": {"input": 0.075, "output": 0.30},
            "default": {"input": 0.075, "output": 0.30}
        },
        "ollama": {
            "default": {"input": 0.0, "output": 0.0}
        }
    }

    provider_pricing = pricing.get(provider, {}).get(model, pricing.get(
        provider, {}).get("default", {"input": 0, "output": 0}))

    input_cost = (prompt_tokens / 1_000_000) * provider_pricing["input"]
    output_cost = (completion_tokens / 1_000_000) * provider_pricing["output"]

    return input_cost + output_cost


def format_messages_for_provider(messages: List[Dict], provider: str, use_system_prompt: bool = False) -> List[Dict]:
    """Format messages for specific provider."""
    formatted = []

    if use_system_prompt:
        # Add system prompt explaining multi-LLM conversation context
        system_prompt = f"""You are {provider}. You are in a multi-LLM chat where different AI models (@gpt, @claude, @gemini, etc.) respond to the user and can see each other's messages in the conversation history.

When asked to critique or analyze another model's response, directly provide your assessment without explaining that you're a different model - the user already knows this.

Respond naturally in your own style."""
        formatted.append({"role": "system", "content": system_prompt})

    for msg in messages:
        role = msg["role"]
        content = msg["content"]

        if provider == "anthropic" and role == "system":
            # Anthropic handles system separately
            continue

        formatted.append({"role": role, "content": content})

    return formatted


def get_daily_cost_limit_reset_time() -> datetime:
    """Get next reset time (midnight UTC)."""
    now = datetime.utcnow()
    tomorrow = now + timedelta(days=1)
    return tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
