"""Google Gemini provider adapter."""
import google.generativeai as genai
from typing import List, Dict, AsyncIterator
from config import settings
import asyncio

class GeminiAdapter:
    name = "gemini"
    
    def __init__(self):
        genai.configure(api_key=settings.google_api_key)
    
    async def stream_complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Stream Gemini response."""
        try:
            # Convert messages to Gemini format
            chat_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    continue  # Gemini doesn't use system messages the same way
                role = "user" if msg["role"] == "user" else "model"
                chat_messages.append({"role": role, "parts": [msg["content"]]})
            
            # Use async generation
            model_instance = genai.GenerativeModel(model)
            
            # Start chat session
            chat = model_instance.start_chat(history=chat_messages[:-1] if len(chat_messages) > 1 else [])
            
            # Generate with streaming
            def generate():
                response = chat.send_message(
                    chat_messages[-1]["parts"][0],
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens,
                        temperature=temperature
                    ),
                    stream=True
                )
                return response
            
            # Run in thread pool since Gemini SDK is synchronous
            response = await asyncio.to_thread(generate)
            
            for chunk in response:
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text
        except Exception as e:
            raise Exception(f"Gemini error: {str(e)}")
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count."""
        # Rough estimate for Gemini (1 token ≈ 4 chars)
        return len(text) // 4
    
    async def health_check(self) -> bool:
        """Check if Gemini is available."""
        try:
            models = genai.list_models()
            return True
        except:
            return False

