# Stinger Web Demo - Stable Version

## Quick Start (Recommended)

The stable demo uses a production build to avoid memory issues:

```bash
# From the web_demo directory
./start_stable_demo.py
```

This will:
1. Check prerequisites (Node.js, Python)
2. Install dependencies
3. Build the frontend (production mode)
4. Start the backend API server
5. Start the frontend static server
6. Open https://localhost:3000 in your browser

## Why Use Stable Mode?

The development server (`npm start`) has known memory issues with React 19. The stable mode:
- ✅ Uses production build (no memory issues)
- ✅ Serves static files efficiently
- ✅ Provides same functionality as dev mode
- ✅ Works reliably every time

## Manual Steps

If you prefer to run components separately:

### 1. Install Dependencies
```bash
# Install production server deps
npm install

# Install frontend deps
cd frontend && npm install

# Install backend deps
cd ../backend && pip install -r requirements.txt
```

### 2. Build Frontend
```bash
cd frontend
npm run build
```

### 3. Start Backend
```bash
# In one terminal
cd backend
python main.py
```

### 4. Start Frontend Server
```bash
# In another terminal (from web_demo root)
node serve-production.js
```

## Features

- 🛡️ **Multiple Guardrails**: PII detection, toxicity checking, prompt injection protection
- 💬 **Interactive Chat**: Real-time chat with OpenAI integration
- ⚙️ **Dynamic Settings**: Enable/disable guardrails on the fly
- 📋 **Audit Logging**: Complete audit trail of all interactions
- 🔒 **Secure**: HTTPS with self-signed certificates

## Troubleshooting

### Memory Issues with Dev Server
If you must use the development server:
1. Ensure `.env` file exists in frontend/ with memory optimizations
2. Use Node.js 18 or later
3. Close other applications to free memory

### Certificate Warnings
The demo uses self-signed certificates. Accept the warning in your browser.

### Backend Connection Issues
- Ensure Python environment has all dependencies
- Check that port 8000 is free
- Verify OpenAI API key is set (if using AI guardrails)

## Architecture

```
┌─────────────┐     HTTPS      ┌──────────────┐
│   Browser   │ ◄───────────► │ Frontend     │
│             │                │ (Port 3000)  │
└─────────────┘                └──────┬───────┘
                                      │ Proxy
                               ┌──────▼───────┐
                               │   Backend    │
                               │ (Port 8000)  │
                               │              │
                               │ • FastAPI    │
                               │ • Guardrails │
                               │ • OpenAI     │
                               └──────────────┘
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for AI-powered guardrails
- `DEMO_MODE`: Set automatically by start script
- `NODE_OPTIONS`: Memory settings (in frontend/.env)

### Ports
- Backend: https://localhost:8000
- Frontend: https://localhost:3000
- API Docs: https://localhost:8000/api/docs

## Next Steps

1. Try different guardrail combinations
2. Test with various prompts (including adversarial ones)
3. Review audit logs to understand guardrail decisions
4. Customize guardrail settings via the UI

---

For development or debugging, see the original README.md