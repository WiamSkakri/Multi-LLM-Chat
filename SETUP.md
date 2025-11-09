# Setup Guide

## Quick Start

1. **Backend Setup:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   uvicorn main:app --reload
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   cp .env.local.example .env.local
   # Edit .env.local
   npm run dev
   ```

3. **Ollama (Optional):**
   ```bash
   ollama serve
   ```

## Environment Variables

### Backend (.env)
- `OPENAI_API_KEY` - Required for @gpt
- `ANTHROPIC_API_KEY` - Required for @claude  
- `GOOGLE_API_KEY` - Required for @gemini
- `APP_PASSWORD` - Password to access app
- `OLLAMA_BASE_URL` - Default: http://localhost:11434
- `USE_SYSTEM_PROMPT` - Default: false

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL` - WebSocket URL (default: ws://localhost:8000)
- `NEXT_PUBLIC_HTTP_API_URL` - HTTP API URL (default: http://localhost:8000)
- `NEXT_PUBLIC_APP_PASSWORD` - Must match backend APP_PASSWORD

## Testing

1. Open http://localhost:3000
2. Try: `@gpt What is LoRA?`
3. Try: `@claude critique @gpt`
4. Try: `@gpt @claude Compare X and Y`

## Troubleshooting

- **WebSocket errors**: Check CORS settings in backend .env
- **Provider unavailable**: Check API keys and provider status at `/api/providers/status`
- **Ollama not working**: Make sure `ollama serve` is running

