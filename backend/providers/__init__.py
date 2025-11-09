"""Provider adapters."""
import logging

from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter
from .gemini_adapter import GeminiAdapter
from .ollama_adapter import OllamaAdapter

logger = logging.getLogger(__name__)

PROVIDERS = {
    "openai": OpenAIAdapter,
    "anthropic": AnthropicAdapter,
    "gemini": GeminiAdapter,
    "ollama": OllamaAdapter,
}

def get_provider(provider_name: str):
    """Get provider instance."""
    provider_class = PROVIDERS.get(provider_name)
    if not provider_class:
        return None
    
    try:
        return provider_class()
    except Exception as exc:  # pragma: no cover - best effort logging
        logger.warning("Provider %s unavailable: %s", provider_name, exc)
        return None
