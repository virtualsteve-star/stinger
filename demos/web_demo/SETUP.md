# Stinger Web Demo Setup Guide

This guide helps you get the Stinger Web Demo running quickly.

## Prerequisites

1. **Python 3.8+** with Stinger installed
2. **Node.js 16+** and npm
3. **OpenAI API Key** (for LLM responses)

## Quick Setup

### 1. Configure OpenAI API Key

The demo uses Stinger's centralized API key management system. Set your API key as an environment variable:

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

**To get an API key:**
- Go to https://platform.openai.com/account/api-keys
- Sign in and create a new secret key
- Copy the key (starts with `sk-`)

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3. Start the Demo

**Option A: Start Both Services**
```bash
# Terminal 1: Start backend
cd backend
python main.py

# Terminal 2: Start frontend  
cd frontend
npm start
```

**Option B: Use the E2E Test Script**
```bash
# Automatically starts both services and runs validation
python test_demo_e2e.py
```

### 4. Access the Demo

Open your browser to:
- **Frontend**: https://localhost:3000
- **Backend API**: https://localhost:8000/api/docs

Accept the SSL certificate warning (self-signed certificate for demo).

## Troubleshooting

### "401 Incorrect API key" Error
- Ensure `OPENAI_API_KEY` environment variable is set
- Check that your API key is valid and active
- Restart the backend after setting the environment variable

### "Pipeline not initialized" Error
- Check backend logs for guardrail loading errors
- Ensure Stinger is properly installed
- Try restarting the backend

### SSL Certificate Warnings
- This is normal for the demo (uses self-signed certificates)
- Click "Advanced" → "Proceed to localhost" in your browser

### Frontend Won't Load
- Ensure both backend (port 8000) and frontend (port 3000) are running
- Check that no other services are using these ports
- Try clearing browser cache

## Demo Features

✅ **Real-time Guardrails**: See Stinger's security filters in action  
✅ **Dynamic Configuration**: Enable/disable guardrails on the fly  
✅ **Multiple Presets**: Switch between different security profiles  
✅ **Audit Trail**: Real-time security event logging  
✅ **Conversation Context**: Multi-turn conversation support  

## Next Steps

- Try different message types to trigger various guardrails
- Experiment with enabling/disabling different security filters
- View the audit log to see security events
- Test different preset configurations

Need help? Check the main Stinger documentation or file an issue.