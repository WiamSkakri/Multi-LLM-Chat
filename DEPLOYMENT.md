# Deploying Multi-LLM Chat to Render

This guide walks you through deploying your Multi-LLM Chat application to Render step by step.

## Prerequisites

Before you begin, make sure you have:

1. A [Render account](https://render.com) (free tier available)
2. Your GitHub repository pushed to GitHub
3. API keys for:
   - OpenAI (from [platform.openai.com](https://platform.openai.com))
   - Anthropic (from [console.anthropic.com](https://console.anthropic.com))
   - Google AI (from [makersuite.google.com](https://makersuite.google.com/app/apikey))
4. A secure password for your app (you'll create this)

## Deployment Options

There are two ways to deploy on Render:

### Option 1: Automatic Deployment (Recommended)

Using the `render.yaml` Blueprint file for infrastructure as code.

### Option 2: Manual Deployment

Creating services manually through the Render dashboard.

---

## Option 1: Automatic Deployment with render.yaml

This is the easiest and recommended approach.

### Step 1: Prepare Your Repository

1. Make sure all changes are committed:
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

### Step 2: Create a New Blueprint on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository (authorize Render if needed)
4. Select your **Multi-LLM-Chat** repository
5. Render will automatically detect the `render.yaml` file

### Step 3: Configure Environment Variables

Render will prompt you to set these **secret** environment variables:

#### Backend Service Variables:
```
OPENAI_API_KEY=sk-...your-key...
ANTHROPIC_API_KEY=sk-ant-...your-key...
GOOGLE_API_KEY=AIza...your-key...
APP_PASSWORD=your-secure-password-here
ALLOWED_ORIGINS=https://your-frontend-name.onrender.com
```

**Important:**
- Choose a strong `APP_PASSWORD` (this protects your app)
- For `ALLOWED_ORIGINS`, you'll need to come back and update this after Step 4 when you get your frontend URL

#### Frontend Service Variables:
```
NEXT_PUBLIC_APP_PASSWORD=your-secure-password-here
```

**Note:** This must match the backend `APP_PASSWORD`

### Step 4: Deploy

1. Click **"Apply"** to create both services
2. Render will:
   - Create a backend service (Python/FastAPI)
   - Create a frontend service (Node.js/Next.js)
   - Install dependencies
   - Build and deploy both services

This takes about 5-10 minutes.

### Step 5: Update CORS Settings

Once deployed, you'll see two service URLs:

- Backend: `https://multi-llm-chat-backend.onrender.com`
- Frontend: `https://multi-llm-chat-frontend.onrender.com`

1. Go to your **backend** service in Render Dashboard
2. Go to **"Environment"** tab
3. Update `ALLOWED_ORIGINS` to include your frontend URL:
   ```
   https://multi-llm-chat-frontend.onrender.com
   ```
4. Click **"Save Changes"** (this will redeploy the backend)

### Step 6: Test Your Deployment

1. Open your frontend URL: `https://multi-llm-chat-frontend.onrender.com`
2. Enter your `APP_PASSWORD`
3. Try a test message: `@gpt Hello world!`

---

## Option 2: Manual Deployment

If you prefer to deploy manually or need more control:

### Step 1: Deploy the Backend

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name:** `multi-llm-chat-backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free

5. Add Environment Variables (click "Advanced"):
   ```
   PYTHON_VERSION=3.11.0
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   GOOGLE_API_KEY=AIza...
   APP_PASSWORD=your-secure-password
   ALLOWED_ORIGINS=https://your-frontend-url.onrender.com
   DEFAULT_GPT_MODEL=gpt-4o-mini
   DEFAULT_CLAUDE_MODEL=claude-haiku-4-5-20251001
   DEFAULT_GEMINI_MODEL=gemini-2.0-flash-exp
   ```

6. Add Health Check Path: `/healthz`
7. Click **"Create Web Service"**
8. Wait for deployment (5-10 minutes)
9. **Save your backend URL** (e.g., `https://multi-llm-chat-backend.onrender.com`)

### Step 2: Deploy the Frontend

1. Click **"New +"** → **"Web Service"** again
2. Connect the same repository
3. Configure:
   - **Name:** `multi-llm-chat-frontend`
   - **Runtime:** Node
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Start Command:** `cd frontend && npm start`
   - **Plan:** Free

4. Add Environment Variables:
   ```
   NODE_VERSION=20.0.0
   NEXT_PUBLIC_API_URL=wss://your-backend-url.onrender.com
   NEXT_PUBLIC_HTTP_API_URL=https://your-backend-url.onrender.com
   NEXT_PUBLIC_APP_PASSWORD=your-secure-password
   ```

   **Replace** `your-backend-url` with your actual backend URL from Step 1

5. Click **"Create Web Service"**
6. Wait for deployment

### Step 3: Update Backend CORS

1. Go back to your **backend** service
2. Update `ALLOWED_ORIGINS` with your frontend URL:
   ```
   https://multi-llm-chat-frontend.onrender.com
   ```
3. Save (this will trigger a redeploy)

---

## Post-Deployment Configuration

### Custom Domain (Optional)

1. In Render Dashboard, go to your **frontend** service
2. Click **"Settings"** → **"Custom Domain"**
3. Add your domain and follow DNS instructions
4. Update backend's `ALLOWED_ORIGINS` to include your custom domain

### Monitoring

Render provides:
- **Logs**: View real-time logs for debugging
- **Metrics**: CPU, Memory, Request rates
- **Health Checks**: Automatic monitoring of `/healthz` endpoint

### Cost Management

On the **Free tier**:
- Services sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds (cold start)
- 750 hours/month of runtime per service

To prevent sleeping:
- Upgrade to **Starter plan** ($7/month per service)
- Or use a service like [UptimeRobot](https://uptimerobot.com/) to ping every 14 minutes

### Database Persistence

The SQLite database (`chat.db`) is **ephemeral** on Render free tier. For persistence:

1. Add a **Render Disk** (Paid feature):
   - Go to service → Settings → Disks
   - Mount path: `/app/backend/chat.db`

2. Or upgrade to PostgreSQL (recommended for production):
   - This requires code changes to use PostgreSQL instead of SQLite

---

## Troubleshooting

### Backend won't start

**Check logs:**
1. Go to backend service → Logs
2. Look for errors like:
   - Missing environment variables
   - Python version issues
   - Dependency installation failures

**Common fixes:**
- Ensure `PYTHON_VERSION=3.11.0` is set
- Verify all required env vars are set
- Check that `requirements.txt` is in the `backend/` directory

### Frontend won't connect to backend

**Symptoms:** "Connecting..." message forever, or WebSocket errors

**Check:**
1. Backend `ALLOWED_ORIGINS` includes frontend URL
2. Frontend `NEXT_PUBLIC_API_URL` uses `wss://` (not `ws://`)
3. Frontend `NEXT_PUBLIC_HTTP_API_URL` uses `https://` (not `http://`)
4. `APP_PASSWORD` matches in both services

**Test backend directly:**
```bash
curl https://your-backend-url.onrender.com/healthz
# Should return: {"status":"ok"}
```

### API Keys not working

**Check:**
1. Keys are correctly copied (no extra spaces)
2. Keys have proper permissions
3. Check service logs for API error messages

### Cold Starts (Free Tier)

**Symptoms:** First request takes 30+ seconds

**This is normal** on free tier. Options:
- Upgrade to paid tier to prevent sleeping
- Use UptimeRobot to ping services every 14 minutes
- Educate users about initial delay

### Rate Limiting Issues

If you're hitting rate limits:

1. Adjust in backend environment variables:
   ```
   DAILY_COST_LIMIT=10.00
   IP_RATE_LIMIT=120
   ```

2. Monitor costs at `/api/providers/status`

---

## Environment Variables Reference

### Backend Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `ANTHROPIC_API_KEY` | Anthropic API key | `sk-ant-...` |
| `GOOGLE_API_KEY` | Google AI API key | `AIza...` |
| `APP_PASSWORD` | App access password | `mySecurePassword123` |
| `ALLOWED_ORIGINS` | Frontend URLs for CORS | `https://frontend.onrender.com` |

### Backend Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFAULT_GPT_MODEL` | `gpt-4o-mini` | Default OpenAI model |
| `DEFAULT_CLAUDE_MODEL` | `claude-haiku-4-5-20251001` | Default Anthropic model |
| `DEFAULT_GEMINI_MODEL` | `gemini-2.0-flash-exp` | Default Google model |
| `DAILY_COST_LIMIT` | `5.00` | Max daily spend in USD |
| `MAX_CONTEXT_MESSAGES` | `20` | Messages to include in context |
| `IP_RATE_LIMIT` | `60` | Requests per minute per IP |
| `USE_SYSTEM_PROMPT` | `false` | Add model identity prompts |

### Frontend Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend WebSocket URL | `wss://backend.onrender.com` |
| `NEXT_PUBLIC_HTTP_API_URL` | Backend HTTP URL | `https://backend.onrender.com` |
| `NEXT_PUBLIC_APP_PASSWORD` | App password (matches backend) | `mySecurePassword123` |

---

## Security Best Practices

1. **Strong Password**: Use a strong, unique `APP_PASSWORD`
2. **API Key Security**: Never commit API keys to git
3. **CORS Configuration**: Only allow your frontend domain
4. **Rate Limiting**: Keep `IP_RATE_LIMIT` and `DAILY_COST_LIMIT` reasonable
5. **Monitor Costs**: Regularly check API usage and costs
6. **Update Dependencies**: Keep packages updated for security patches

---

## Updating Your Deployment

### When you make code changes:

1. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your changes"
   git push origin main
   ```

2. Render auto-deploys on push (if auto-deploy is enabled)
3. Or manually deploy: Service → Manual Deploy → Deploy latest commit

### When you change environment variables:

1. Go to service → Environment tab
2. Update the variable
3. Click Save Changes (this triggers a redeploy)

---

## Getting Help

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Render Community**: [community.render.com](https://community.render.com)
- **Logs**: Always check service logs first for errors
- **Health Check**: Visit `/healthz` and `/readyz` endpoints

---

## Next Steps

After successful deployment:

1. Test all features:
   - `@gpt` mentions
   - `@claude` mentions
   - `@gemini` mentions
   - Parallel requests: `@gpt @claude compare X and Y`
   - Critiques: `@claude critique @gpt`

2. Monitor costs and usage
3. Set up custom domain (optional)
4. Configure monitoring/alerting
5. Share with users!

---

## Production Checklist

- [ ] Backend deployed and healthy (`/healthz` returns OK)
- [ ] Frontend deployed and accessible
- [ ] WebSocket connection working
- [ ] All 3 LLM providers responding
- [ ] CORS configured correctly
- [ ] Strong `APP_PASSWORD` set
- [ ] API keys working and valid
- [ ] Cost limits configured
- [ ] Logs are clean (no errors)
- [ ] Test all @mention functionality
- [ ] Test parallel requests
- [ ] Test critique functionality
- [ ] Monitor first 24 hours for issues

---

Good luck with your deployment! Your Multi-LLM Chat should now be live and accessible to the world.
