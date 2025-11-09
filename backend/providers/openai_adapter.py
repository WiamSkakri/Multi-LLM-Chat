"""OpenAI provider adapter."""
import openai
from typing import List, Dict, AsyncIterator
import time
from config import settings

class OpenAIAdapter:
    name = "openai"
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
    
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Stream OpenAI response."""
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"OpenAI error: {str(e)}")
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count using tiktoken."""
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model("gpt-4")
            return len(encoding.encode(text))
        except:
            # Fallback: rough estimate (1 token ≈ 4 chars)
            return len(text) // 4
    
    async def health_check(self) -> bool:
        """Check if OpenAI is available."""
        try:
            await self.client.models.list()
            return True
        except:
            return False

