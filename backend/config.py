"""Configuration management."""
import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    
    # Model Defaults
    default_gpt_model: str = "gpt-4o-mini"
    default_claude_model: str = "claude-haiku-4-5-20251001"
    default_gemini_model: str = "gemini-2.0-flash-exp"
    default_local_model: str = "llama3"
    
    # Limits
    daily_cost_limit: float = 5.00
    max_context_messages: int = 20
    ip_rate_limit: int = 60
    max_input_chars: int = 10000
    
    # Security
    allowed_origins: str = "http://localhost:3000"
    app_password: str = ""
    
    # Optional
    ollama_base_url: str = "http://localhost:11434"
    use_system_prompt: bool = False
    
    # Timeouts (seconds)
    openai_timeout: int = 60
    anthropic_timeout: int = 60
    gemini_timeout: int = 60
    ollama_timeout: int = 90
    
    # Context limits (tokens)
    gpt_max_context: int = 128000
    claude_max_context: int = 200000
    gemini_max_context: int = 1000000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

settings = Settings()

