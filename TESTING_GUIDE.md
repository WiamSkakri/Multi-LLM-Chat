# Testing Guide

## Current Status

✅ **Backend is running** on http://localhost:8000
⏳ **Frontend is starting** (may take 30-60 seconds)

## Quick Test Steps

### 1. Check Backend Health
```bash
curl http://localhost:8000/healthz
# Should return: {"status":"ok"}

curl http://localhost:8000/readyz
# Shows detailed status of database and providers
```

### 2. Access Frontend
Once the frontend is ready, open:
**http://localhost:3000**

### 3. Test Basic Functionality

#### Test @mention (requires API keys)
1. Open http://localhost:3000
2. Type: `@gpt What is LoRA?`
3. Press Enter or click Send
4. You should see a streaming response

#### Test Local Model (Ollama)
1. Make sure Ollama is running: `ollama serve`
2. Type: `@local Explain Rust ownership`
3. Should get a response from local model

#### Test Critique
1. First ask: `@gpt What are the trade-offs of quantized transformers?`
2. Wait for response
3. Then ask: `@claude critique @gpt`
4. Should see Claude critiquing GPT's response

#### Test Parallel Requests
1. Type: `@gpt @claude Compare LoRA vs QLoRA`
2. Both models should respond in parallel

## Troubleshooting

### Backend Issues

**Database shows "disconnected":**
- The database file exists, this might be a false positive
- Check backend logs for errors
- Database will be created automatically on first use

**Provider unavailable:**
- Check if API keys are set in `backend/.env`
- For local: Make sure `ollama serve` is running
- Check provider status: `curl http://localhost:8000/api/providers/status`

### Frontend Issues

**WebSocket connection fails:**
- Check that `APP_PASSWORD` matches in both `.env` files
- Check CORS settings in backend `.env`: `ALLOWED_ORIGINS=http://localhost:3000`
- Check browser console for errors

**Frontend not loading:**
- Wait 30-60 seconds for Next.js to compile
- Check terminal for compilation errors
- Try: `cd frontend && npm run dev`

### Missing API Keys

If you don't have API keys yet:
- The app will still run
- You can test with `@local` if Ollama is running
- Add API keys to `backend/.env` to test other providers

## Environment Files

**Backend** (`backend/.env`):
- `APP_PASSWORD=test123` (default for testing)
- Add your API keys here

**Frontend** (`frontend/.env.local`):
- `NEXT_PUBLIC_APP_PASSWORD=test123` (must match backend)
- URLs are already configured

## Next Steps

1. **Add API Keys** (optional):
   - Get keys from OpenAI, Anthropic, Google
   - Add to `backend/.env`
   - Restart backend

2. **Test Ollama** (optional):
   ```bash
   # Install Ollama if not installed
   brew install ollama  # macOS
   
   # Start Ollama
   ollama serve
   
   # Pull a model
   ollama pull llama3
   ```

3. **Test the UI**:
   - Open http://localhost:3000
   - Try different @mentions
   - Check cost badges
   - Test streaming

## Stopping Servers

Press `Ctrl+C` in the terminals where servers are running, or:

```bash
# Kill backend
pkill -f "uvicorn main:app"

# Kill frontend  
pkill -f "next dev"
```


