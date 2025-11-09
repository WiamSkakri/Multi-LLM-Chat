"""FastAPI main application."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import json
import time
import asyncio
from typing import List, Dict
import aiosqlite

from config import settings
from database import init_db, get_db
from providers import get_provider
from utils import (
    parse_mentions, is_critique, parse_critique_target,
    generate_id, calculate_cost, format_messages_for_provider
)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Model aliases
MODEL_ALIASES = {
    "gpt": ("openai", settings.default_gpt_model),
    "claude": ("anthropic", settings.default_claude_model),
    "gemini": ("gemini", settings.default_gemini_model),
    "local": ("ollama", settings.default_local_model),
}

@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    await init_db()

@app.get("/healthz")
async def healthz():
    """Basic health check."""
    return {"status": "ok"}

@app.get("/readyz")
async def readyz():
    """Detailed readiness check."""
    status = {
        "status": "healthy",
        "database": "unknown",
        "providers": {}
    }
    
    # Check database
    try:
        async with get_db() as db:
            await db.execute("SELECT 1")
        status["database"] = "connected"
    except:
        status["database"] = "disconnected"
        status["status"] = "unhealthy"
    
    # Check providers
    for alias, (provider_name, _) in MODEL_ALIASES.items():
        provider = get_provider(provider_name)
        if provider:
            try:
                is_healthy = await provider.health_check()
                status["providers"][alias] = "available" if is_healthy else "unavailable"
            except:
                status["providers"][alias] = "unavailable"
        else:
            status["providers"][alias] = "unavailable"
    
    return status

@app.get("/api/providers/status")
async def providers_status():
    """Get provider status for frontend."""
    status = {}
    for alias, (provider_name, _) in MODEL_ALIASES.items():
        provider = get_provider(provider_name)
        if provider:
            try:
                is_healthy = await provider.health_check()
                status[alias] = "available" if is_healthy else "unavailable"
            except:
                status[alias] = "unavailable"
        else:
            status[alias] = "unavailable"
    return status

def check_auth(request: Request):
    """Check authentication."""
    # Simple password check via header
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = auth_header.replace("Bearer ", "")
    if token != settings.app_password:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for chat."""
    await websocket.accept()
    
    thread_id = None
    reconnect_attempts = 0
    max_reconnect_attempts = 3
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "auth":
                # Simple auth check
                if message_data.get("password") != settings.app_password:
                    await websocket.send_json({"type": "error", "message": "Unauthorized"})
                    await websocket.close()
                    return
                thread_id = message_data.get("thread_id") or generate_id()
                await websocket.send_json({"type": "authenticated", "thread_id": thread_id})
                continue
            
            if message_data.get("type") == "message":
                content = message_data.get("content", "")
                thread_id = message_data.get("thread_id") or thread_id
                
                # Check input length
                if len(content) > settings.max_input_chars:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Message too long (max {settings.max_input_chars} chars)"
                    })
                    continue
                
                # Save user message
                user_message_id = generate_id()
                mentions = parse_mentions(content)
                
                async with get_db() as db:
                    # Ensure thread exists
                    await db.execute(
                        "INSERT OR IGNORE INTO threads (id) VALUES (?)",
                        (thread_id,)
                    )
                    
                    # Save user message
                    await db.execute("""
                        INSERT INTO messages (id, thread_id, role, content, mentions)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user_message_id, thread_id, "user", content, json.dumps(mentions)))
                    await db.commit()
                
                # Process mentions
                if is_critique(content):
                    # Handle critique
                    target_info = parse_critique_target(content)
                    if target_info:
                        target_model, index = target_info
                        await handle_critique(
                            websocket, thread_id, content, target_model, index, user_message_id
                        )
                else:
                    # Handle regular mentions
                    await handle_mentions(websocket, thread_id, content, mentions, user_message_id)
                
                reconnect_attempts = 0  # Reset on successful message
    
    except WebSocketDisconnect:
        # Handle reconnection
        reconnect_attempts += 1
        if reconnect_attempts <= max_reconnect_attempts:
            delay = 2 ** (reconnect_attempts - 1)  # Exponential backoff
            await asyncio.sleep(delay)
            # Client should reconnect
        else:
            # Max attempts reached, client should show reconnect button
            pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Server error: {str(e)}"
        })

async def handle_mentions(
    websocket: WebSocket,
    thread_id: str,
    content: str,
    mentions: List[str],
    user_message_id: str
):
    """Handle multiple @mentions in parallel."""
    if not mentions:
        await websocket.send_json({
            "type": "error",
            "message": "No @mentions found. Try: @gpt, @claude, @gemini, @local"
        })
        return
    
    # Get recent messages for context
    async with get_db() as db:
        async with db.execute("""
            SELECT role, content, model FROM messages
            WHERE thread_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (thread_id, settings.max_context_messages)) as cursor:
            rows = await cursor.fetchall()
    
    # Build message history
    message_history = []
    for row in reversed(rows):  # Oldest first
        role, msg_content, model = row
        message_history.append({
            "role": role,
            "content": msg_content
        })
    
    # Add current user message
    message_history.append({"role": "user", "content": content})
    
    # Process each mention in parallel
    tasks = []
    for mention in mentions:
        if mention not in MODEL_ALIASES:
            await websocket.send_json({
                "type": "error",
                "message": f"Unknown model: @{mention}. Try: @gpt, @claude, @gemini, @local"
            })
            continue
        
        provider_name, model_name = MODEL_ALIASES[mention]
        task = process_model_request(
            websocket, thread_id, message_history, provider_name, model_name, mention, user_message_id
        )
        tasks.append(task)
    
    # Run all in parallel
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

async def handle_critique(
    websocket: WebSocket,
    thread_id: str,
    content: str,
    target_model: str,
    index: int,
    user_message_id: str
):
    """Handle critique request."""
    if target_model not in MODEL_ALIASES:
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown target model: @{target_model}"
        })
        return
    
    # Find target message
    async with get_db() as db:
        async with db.execute("""
            SELECT id, content FROM messages
            WHERE thread_id = ? AND model = ? AND role = 'assistant'
            ORDER BY created_at DESC
            LIMIT ?
        """, (thread_id, target_model, index)) as cursor:
            rows = await cursor.fetchall()
    
    if not rows:
        await websocket.send_json({
            "type": "error",
            "message": f"No @{target_model} response found to critique"
        })
        return
    
    target_message_id, target_content = rows[index - 1]
    
    # Find original question (user message before target)
    async with get_db() as db:
        async with db.execute("""
            SELECT content FROM messages
            WHERE thread_id = ? AND created_at < (
                SELECT created_at FROM messages WHERE id = ?
            ) AND role = 'user'
            ORDER BY created_at DESC
            LIMIT 1
        """, (thread_id, target_message_id)) as cursor:
            row = await cursor.fetchone()
            original_question = row[0] if row else "the previous question"
    
    # Build critique prompt
    critique_prompt = f"""The user asked: "{original_question}"

{target_model.upper()} responded:

{target_content}

Please provide your thoughts on this response - what's good, what's missing, how you might approach it differently."""
    
    # Get mention for critique model
    critique_mentions = parse_mentions(content)
    if not critique_mentions:
        await websocket.send_json({
            "type": "error",
            "message": "No model specified for critique"
        })
        return
    
    critique_model = critique_mentions[0]
    if critique_model not in MODEL_ALIASES:
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown model: @{critique_model}"
        })
        return
    
    # Get context
    async with get_db() as db:
        async with db.execute("""
            SELECT role, content, model FROM messages
            WHERE thread_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (thread_id, settings.max_context_messages)) as cursor:
            rows = await cursor.fetchall()
    
    message_history = []
    for row in reversed(rows):
        role, msg_content, model = row
        message_history.append({"role": role, "content": msg_content})
    
    message_history.append({"role": "user", "content": critique_prompt})
    
    # Process critique
    provider_name, model_name = MODEL_ALIASES[critique_model]
    await process_model_request(
        websocket, thread_id, message_history, provider_name, model_name,
        critique_model, user_message_id, target_message_id=target_message_id
    )

async def process_model_request(
    websocket: WebSocket,
    thread_id: str,
    message_history: List[Dict],
    provider_name: str,
    model_name: str,
    mention: str,
    user_message_id: str,
    target_message_id: str = None
):
    """Process a single model request."""
    provider = get_provider(provider_name)
    if not provider:
        await websocket.send_json({
            "type": "error",
            "message": f"Provider {provider_name} not available"
        })
        return
    
    # Format messages for provider
    formatted_messages = format_messages_for_provider(
        message_history, provider_name, settings.use_system_prompt
    )
    
    # Create message ID for response
    response_id = generate_id()
    
    # Send start signal
    await websocket.send_json({
        "type": "response_start",
        "message_id": response_id,
        "model": mention,
        "provider": provider_name
    })
    
    # Stream response
    start_time = time.time()
    full_response = ""
    prompt_tokens = sum(provider.count_tokens(msg["content"]) for msg in formatted_messages)
    completion_tokens = 0
    is_complete = True
    
    try:
        timeout = getattr(settings, f"{provider_name}_timeout", 60)
        async for chunk in asyncio.wait_for(
            provider.stream_complete(formatted_messages, model_name),
            timeout=timeout
        ):
            full_response += chunk
            completion_tokens = provider.count_tokens(full_response)
            
            await websocket.send_json({
                "type": "chunk",
                "message_id": response_id,
                "content": chunk
            })
    except asyncio.TimeoutError:
        is_complete = False
        await websocket.send_json({
            "type": "error",
            "message": "Model took too long, try again?"
        })
    except Exception as e:
        is_complete = False
        await websocket.send_json({
            "type": "error",
            "message": f"[@{mention} unavailable] Try another model or @local instead?"
        })
    
    latency_ms = int((time.time() - start_time) * 1000)
    cost = calculate_cost(provider_name, model_name, prompt_tokens, completion_tokens)
    
    # Save response
    async with get_db() as db:
        await db.execute("""
            INSERT INTO messages (id, thread_id, role, content, model, is_complete, target_message_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (response_id, thread_id, "assistant", full_response, mention, is_complete, target_message_id))
        
        await db.execute("""
            INSERT INTO model_calls (id, message_id, provider, model_name, prompt_tokens, completion_tokens, cost_usd, latency_ms, finish_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            generate_id(), response_id, provider_name, model_name,
            prompt_tokens, completion_tokens, cost, latency_ms,
            "stop" if is_complete else "error"
        ))
        await db.commit()
    
    # Send completion
    await websocket.send_json({
        "type": "response_complete",
        "message_id": response_id,
        "tokens": prompt_tokens + completion_tokens,
        "latency_ms": latency_ms,
        "cost_usd": cost
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

