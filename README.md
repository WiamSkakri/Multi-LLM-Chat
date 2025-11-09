# Multi-LLM Chatroom

A chat interface where you can @mention multiple LLMs (GPT, Claude, Gemini, Ollama) in a single conversation. Models can answer questions, critique each other, and respond in parallel - all with their authentic, unedited style.

## Features

- **@mention models** - Type `@gpt`, `@claude`, `@gemini`, or `@local` to get responses
- **Parallel responses** - Ask multiple models at once: `@gpt @claude Compare X and Y`
- **Critique mode** - Have one model critique another: `@claude critique @gpt`
- **Streaming responses** - Real-time streaming with cost and latency tracking
- **Local models** - Use Ollama for free local inference
- **Cost tracking** - See tokens, latency, and cost per response

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- (Optional) Ollama for local models

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file:

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `GOOGLE_API_KEY` - Your Google API key (for Gemini)
- `APP_PASSWORD` - Password to access the app

Optional:
- `OLLAMA_BASE_URL` - Default: `http://localhost:11434`
- `USE_SYSTEM_PROMPT` - Set to `true` to add model identity prompts (default: `false`)

### Frontend Setup

```bash
cd frontend
npm install
```

Create `.env.local`:

```bash
cp .env.local.example .env.local
# Edit with your settings
```

### Running Locally

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Ollama (optional):**
```bash
ollama serve
```

Open http://localhost:3000

### Docker Setup

```bash
# Create .env file in root with all required variables
docker-compose up
```

## Usage

### Basic @mentions

```
@gpt What are the trade-offs of quantized transformers?
@claude Explain Rust ownership
@local Summarize this paper
```

### Parallel requests

```
@gpt @claude @gemini Compare LoRA vs QLoRA trade-offs
```

### Critiques

```
@claude critique @gpt
```

This will have Claude critique GPT's most recent response. To target a specific response:

```
@claude critique @gpt #2
```

(Where `#2` means the 2nd most recent @gpt response)

## Architecture

- **Backend**: FastAPI with WebSocket streaming
- **Frontend**: Next.js 14 with React
- **Database**: SQLite (WAL mode for concurrency)
- **Providers**: OpenAI, Anthropic, Google Gemini, Ollama

## API Endpoints

- `GET /healthz` - Basic health check
- `GET /readyz` - Detailed readiness (database + providers)
- `GET /api/providers/status` - Provider availability status
- `WS /ws` - WebSocket endpoint for chat

## Configuration

See `backend/.env.example` for all configuration options:

- Model defaults
- Rate limits
- Context window settings
- Timeouts
- Cost limits

## Development

### Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm run dev
```

### Type Checking

```bash
cd backend
mypy . --ignore-missing-imports
```

## Testing

Manual smoke tests:

- [ ] `@gpt What is LoRA?` → response in <10s with metrics
- [ ] `@claude critique @gpt` → freeform critique appears
- [ ] `@gpt @claude compare X` → both responses stream in parallel
- [ ] `@local explain Y` → Ollama responds (when running)
- [ ] Cost badge shows reasonable estimate
- [ ] Errors are friendly and actionable

## Troubleshooting

**Ollama not responding:**
- Make sure Ollama is running: `ollama serve`
- Check `OLLAMA_BASE_URL` in `.env`

**WebSocket connection issues:**
- Check `ALLOWED_ORIGINS` includes your frontend URL
- Verify `APP_PASSWORD` matches in both frontend and backend

**Provider errors:**
- Check API keys are set correctly
- Verify provider status: `GET /api/providers/status`

## License

MIT
