# Stinger Management Console

A simple, lightweight monitoring console for Stinger guardrails. No authentication required - just run and monitor!

## Features

- 📊 **Real-time Dashboard**: System overview with key metrics
- 🎯 **Guardrail Performance**: Track performance of each guardrail
- 💬 **Active Conversations**: Monitor ongoing conversations
- 📝 **Audit Log Explorer**: Search and filter security events
- ❤️ **System Health**: Monitor system status and API health

## Quick Start

### Option 1: Using the startup script (recommended)

```bash
# Start both backend and frontend
./start_console.sh

# Or run in background/detached mode (useful for tools with timeouts)
./start_console.sh --detached
```

### Option 2: Manual startup

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (in another terminal)
cd frontend
npm install
npm start
```

### Access the Console

Open **http://localhost:3001** in your browser

- Frontend UI: http://localhost:3001
- Backend API: http://localhost:8001

## Architecture

- **Backend**: FastAPI with simple REST endpoints (no auth)
- **Frontend**: React with smart polling (no WebSockets)
- **Data**: Uses existing Stinger audit logs and metrics

## Development

This console is designed to be simple:
- No authentication required
- No complex setup
- Just monitoring, no control
- Runs locally for operators

Perfect for development and small deployments where simplicity matters!