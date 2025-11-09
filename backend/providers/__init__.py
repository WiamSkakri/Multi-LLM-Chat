"""Provider adapters."""
from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter
from .gemini_adapter import GeminiAdapter
from .ollama_adapter import OllamaAdapter

PROVIDERS = {
    "openai": OpenAIAdapter,
    "anthropic": AnthropicAdapter,
    "gemini": GeminiAdapter,
    "ollama": OllamaAdapter,
}

def get_provider(provider_name: str):
    """Get provider instance."""
    provider_class = PROVIDERS.get(provider_name)
    if provider_class:
        return provider_class()
    return None
