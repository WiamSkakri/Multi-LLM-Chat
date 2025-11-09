"""Ollama (local) provider adapter."""
import aiohttp
from typing import List, Dict, AsyncIterator
from config import settings
import json

class OllamaAdapter:
    name = "ollama"
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
    
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Stream Ollama response."""
        try:
            # Convert messages to Ollama format
            prompt = self._format_messages(messages)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens
                        }
                    }
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Ollama error: {response.status}")
                    
                    async for line in response.content:
                        if line:
                            try:
                                line_str = line.decode('utf-8').strip()
                                if line_str:
                                    data = json.loads(line_str)
                                    if "response" in data:
                                        yield data["response"]
                                    if data.get("done", False):
                                        break
                            except json.JSONDecodeError:
                                continue
        except aiohttp.ClientError as e:
            raise Exception(f"Ollama connection error: {str(e)}")
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """Format messages for Ollama prompt."""
        formatted = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            formatted.append(f"{role.capitalize()}: {content}")
        return "\n\n".join(formatted)
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count."""
        # Rough estimate (1 token ≈ 4 chars)
        return len(text) // 4
    
    async def health_check(self) -> bool:
        """Check if Ollama is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags", timeout=aiohttp.ClientTimeout(total=2)) as response:
                    return response.status == 200
        except:
            return False

