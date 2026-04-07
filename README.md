# Reflect AI: Memory-Aware Support Companion

![Architecture: FastAPI + React Native](https://img.shields.io/badge/Architecture-FastAPI_%7C_React_Native-blue)
![Auth: JWT](https://img.shields.io/badge/Auth-JWT_Bearer-green)

**Reflect AI** is a memory-aware support companion that persists context across conversations and adapts responses based on user state and safety signals.

Instead of treating each message as isolated, it builds a structured understanding of the user over time — enabling more consistent, contextual, and safer interactions.

## What it does

- Maintains conversation memory across sessions
- Retrieves relevant past context when generating responses
- Routes responses through safety-aware modes (e.g., normal, supportive, crisis)
- Provides a structured backend for building reliable, stateful AI systems

**Example flow:**
1. User sends a message
2. System retrieves relevant memory
3. Safety layer classifies risk level
4. Response mode is selected
5. LLM generates a context-aware reply
6. Message and context updates are persisted

## Motivation

Most AI chat systems treat conversations as stateless interactions.
Reflect AI explores how persistent memory, structured execution, and safety-aware routing can create more reliable and context-aware AI systems.

The goal is not just to generate responses, but to build a system that:
- remembers
- reasons about context
- and behaves safely under different conditions

## System Architecture

The project is built with a clear separation between mobile client and backend logic:

- **Backend (`/backend`)**: Built with **FastAPI**. It handles authentication, AI model orchestration, and memory management. 
  - A modular execution pipeline (context → tools → response) designed for future orchestration and multi-step reasoning.
- **Frontend (`/mobile`)**: Built with **React Native (Expo)**. Features end-to-end authentication, secure on-device state management, and a protected navigation stack.

## Key Features

- **Working End-to-End Flow**  
  Authenticated users can create conversations, send messages, and receive responses via a live backend API.

- **Memory-Aware Conversations**  
  Context persists across sessions and is selectively retrieved to inform responses.

- **End-to-End Authentication**  
  JWT-based auth with secure on-device token storage and automatic session restoration.

- **Safety-Aware Response Routing (WIP)**  
  Incoming messages can be classified and routed through different response modes.

- **Extensible Execution Architecture**  
  Designed to support tools, structured context, and future orchestration layers.

## Quick Start & Setup

### 1. Backend Setup

The backend runs natively on Python.

```powershell
cd backend
python -m venv venv-win
.\venv-win\Scripts\Activate.ps1
pip install fastapi "uvicorn[standard]" pydantic pydantic-settings python-dotenv python-jose[cryptography] passlib[bcrypt] email-validator

# Run the server
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

*Note: Binding to `0.0.0.0` ensures the server is accessible to mobile emulators and physical devices over your local network. Configure secrets via `.env` based on `.env.example`.*

### 2. Frontend Setup

Requires Node.js and Expo CLI.

```bash
cd mobile
npm install

# Start the Expo development server
npx expo start --android
```

## Project Structure

```text
reflect-ai/
├── backend/
│   ├── src/
│   │   ├── core/           # Core domain logic (auth, context, tools)
│   │   ├── routes/         # API endpoint definitions 
│   │   ├── server/         # FastAPI app factory
│   │   ├── config.py       # Configuration and environment mappings
│   │   └── main.py         # Entrypoint
│   └── pyproject.toml
├── mobile/
│   ├── src/
│   │   ├── constants/      # Global styling constants
│   │   ├── context/        # React context (e.g., AuthContext)
│   │   ├── navigation/     # React Navigation stacks
│   │   ├── screens/        # UI Views
│   │   └── services/       # API and SecureStore layers
│   ├── App.tsx             # Root component
│   └── app.json            # Expo config
└── setup-wsl-port.ps1      # WSL port forwarding script
```

## Security

- Authentication and authorization are enforced at the API layer.
- Sensitive tokens are stored securely on-device.
- Backend never exposes raw credentials or secrets.
- Passwords are hashed using PBKDF2 with no platform-specific dependencies.

## Future Work

- Full tool orchestration layer
- Streaming execution pipeline
- Advanced safety policies and evaluation
- Hybrid local + hosted LLM routing
