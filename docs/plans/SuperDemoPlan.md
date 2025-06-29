# Super Demo Implementation Plan

## Overview
This plan describes the implementation of a "SUPER DEMO" for the Stinger Guardrails Framework, featuring:
- A modern, attractive **React** chat interface (web-based)
- A local Python webserver backend (**FastAPI**)
- Real LLM backend (**OpenAI**)
- Stinger guardrails applied to both user input and LLM output
- Settings pane to select/toggle guardrails
- Clear UI feedback for blocked messages (with reason)
- All code runnable locally (no Docker required for now)
- **All demo code will be located in `demos/web_demo/` with separate `frontend/` and `backend/` subdirectories to keep it isolated from production code.**
- **Demonstrates the Conversation concept:** Uses Stinger's Conversation API to manage multi-turn context, showing how guardrails can leverage conversation history.
- **Showcases audit logging:** Includes a real-time log viewer window in the UI to display the audit log contents as the conversation progresses.

---

## Security

- The web app and backend will communicate over **HTTPS** (TLS/SSL), even in local development.
- A self-signed certificate will be generated for local use.
- The backend (FastAPI) will be configured to serve over HTTPS using the self-signed certificate.
- The frontend (React) will be configured to connect to the backend via `https://localhost:PORT`.
- CORS will be restricted to the local frontend origin.

**How to set up self-signed certificates for local development:**
1. Generate a self-signed certificate and private key (e.g., using OpenSSL):
   ```sh
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"
   ```
2. Configure FastAPI (with Uvicorn) to use these files:
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8000 --ssl-keyfile=key.pem --ssl-certfile=cert.pem
   ```
3. Configure the React frontend to connect to `https://localhost:8000` (and accept the self-signed cert in your browser).

---

## 1. Architecture

### Components
- **Frontend:**
  - Modern chat UI built with **React** (functional components, hooks)
  - CSS-in-JS (styled-components or CSS modules) for styling
  - Responsive layout: chat area (left), settings pane (right)
  - Settings pane: checkboxes for guardrails, grouped by Input/Output
  - Bot selector dropdown (placeholder for now)
  - Message bubbles for user/bot, with blocked message reason display
  - **Prompt Injection Screening Options:** UI controls to select between regular prompt injection screening and multi-turn (conversation-aware) screening.
  - **Audit Log Viewer:** A window/pane that displays the contents of the audit log in real time.
- **Backend:**
  - **FastAPI** server
  - Endpoints: `/chat` (POST), `/settings` (GET/POST), `/guardrails` (GET/POST), `/audit_log` (GET, for real-time log updates)
  - Integrates Stinger guardrails (input/output filtering)
  - Uses Stinger's Conversation API for multi-turn context management
  - Calls OpenAI API after input passes guardrails
  - Serves static files for frontend
  - **Located in `demos/web_demo/backend/`**
- **Frontend location:**
  - **Located in `demos/web_demo/frontend/`**

---

## 2. Guardrails to Include

### Input Filters
- Input Length (local)
- Rate Limit (local)
- PII (local)
- Profanity (local)
- Prompt Injection (local)
- Prompt Injection (conversation-aware, multi-turn)
- Toxicity (AI)
- Prompt Injection (AI)

### Output Filters
- PII (local)
- Profanity (local)
- Code Generation (local)
- Toxicity (AI)
- Prompt Injection (AI)

---

## 3. UI/UX Design
- **Inspiration:** See provided screenshot for layout and style
- **Modern, clean chat layout**: Chat area on left, settings pane on right
- **Settings pane**: Collapsible, checkboxes for each guardrail (grouped by input/output)
- **Prompt Injection Screening Options:** Toggle between regular and multi-turn screening
- **Bot selector**: Dropdown for different bots (placeholder)
- **Message bubbles**: User and bot, with blocked messages showing reason
- **Audit Log Viewer:** Real-time log window/pane, scrollable, shows latest audit log entries as messages are sent/received
- **Feedback icons**: Thumbs up/down, copy (optional for MVP)
- **Responsive design**: Works on desktop and mobile

---

## 4. Deliverables
- React frontend (chat UI, settings pane, guardrail toggling, prompt injection screening options, audit log viewer)
- FastAPI backend (Stinger integration, Conversation API, OpenAI integration, REST endpoints, audit log endpoint)
- End-to-end demo: user input → input guardrails → LLM → output guardrails → frontend
- Documentation for setup and usage (in `demos/web_demo/README.md`)

---

## 5. Out of Scope
- Dockerization (for now)
- Paid web testing tools
- Multi-user support (single session demo)
- **No mention in the top-level README until the demo exists.**

---

## 6. Timeline & Risks
- See original plan for estimates and risk notes (unchanged) 