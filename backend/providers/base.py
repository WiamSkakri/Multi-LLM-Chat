"""Base provider interface."""
from typing import Protocol, AsyncIterator, List, Dict

class LLMProvider(Protocol):
    name: str
    
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Stream response chunks. Yield plain text strings."""
        ...
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count for this provider."""
        ...
    
    async def health_check(self) -> bool:
        """Check if provider is available."""
        ...

