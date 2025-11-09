"""Anthropic provider adapter."""
import anthropic
from typing import List, Dict, AsyncIterator
from config import settings

class AnthropicAdapter:
    name = "anthropic"

    def __init__(self):
        if settings.anthropic_api_key:
            self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        else:
            self.client = None
    
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Stream Anthropic response."""
        if not self.client:
            raise Exception("Anthropic API key not configured")

        try:
            # Anthropic uses system/user/assistant format
            system_messages = []
            conversation = []

            for msg in messages:
                if msg["role"] == "system":
                    system_messages.append({
                        "type": "text",
                        "text": msg["content"]
                    })
                else:
                    conversation.append(msg)

            # Build kwargs for the API call
            kwargs = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": conversation
            }

            # Only include system if we have system messages
            if system_messages:
                kwargs["system"] = system_messages

            async with self.client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise Exception(f"Anthropic error: {str(e)}")
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count."""
        # Rough estimate for Anthropic (1 token ≈ 4 chars)
        # Anthropic's actual tokenizer isn't easily accessible
        return len(text) // 4
    
    async def health_check(self) -> bool:
        """Check if Anthropic is available."""
        if not self.client:
            return False
        try:
            # Simple health check
            return True
        except:
            return False

