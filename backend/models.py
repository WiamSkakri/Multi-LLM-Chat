"""Data models."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Message(BaseModel):
    id: str
    thread_id: str
    role: str  # 'user' or 'assistant'
    content: str
    model: Optional[str] = None
    mentions: Optional[List[str]] = None
    target_message_id: Optional[str] = None
    is_complete: bool = True
    created_at: datetime

class ModelCall(BaseModel):
    id: str
    message_id: str
    provider: str
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    latency_ms: int
    finish_reason: str
    retry_count: int = 0
    created_at: datetime

class Thread(BaseModel):
    id: str
    created_at: datetime

