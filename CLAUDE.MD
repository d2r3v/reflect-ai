# AI Context Guide (Reflect AI)

This file contains the full architectural, technological, and domain context needed for any LLM to assist effectively on this project.

---

## System Architecture & Stack

The application is split between a mobile client and a Python backend.

- **Frontend (`/mobile`)**: React Native built with **Expo SDK 52**.
  - **Navigation**: `@react-navigation/native-stack` + `@react-navigation/bottom-tabs`
  - **State**: React Context API (`AuthContext` for global session).
  - **Storage**: `expo-secure-store` (v14.0.1).
  - **API Layer**: `services/api.ts` provides `authGet` / `authPost` helpers that auto-attach Bearer tokens.
  - **Conversation Service**: `services/conversations.ts` wraps all conversation CRUD.

- **Backend (`/backend`)**: **FastAPI** (Async) running on Python >= 3.10.
  - **Database**: SQLite via `aiosqlite`. Path is resolved absolutely via `pathlib` in `config.py`.
  - **ORM**: SQLAlchemy 2.0 (Declarative Base, async sessions via `AsyncSessionLocal`).
  - **Migrations**: Alembic (async template, `render_as_batch=True` for SQLite).
  - **Auth**: JWT Bearer via `python-jose`. Passwords hashed with native PBKDF2 (`hashlib`). No C-extension dependencies.

---

## Engineering Rules

1. **MVP-focused**: No Redis, Celery, websockets, or vector DBs until strictly necessary.
2. **Business logic placement**: Do not put logic inside `/routes`. Use `/core`, `/lib`, or `/services`.
3. **Safety first**: Critical-risk behavior must be deterministic and bypass normal generation.
4. **Prompt storage**: Store prompt text in dedicated files or constants, not inline in handlers.
5. **No Telepathy**: When providing run commands, provide the exact commands including `cd` steps.

---

## Backend Project Structure

```
src/
├── config.py                 # Pydantic settings (DB URL resolved absolutely)
├── main.py                   # Entrypoint
├── core/
│   ├── auth/
│   │   ├── security.py       # hash_password, verify_password, JWT create/decode
│   │   └── dependencies.py   # get_current_user FastAPI dependency
│   ├── context/
│   │   └── execution.py      # ExecutionContext, ResponseMode enum
│   ├── tools/
│   │   ├── base.py           # Tool ABC, ToolCall, ToolResult models
│   │   └── registry.py       # ToolRegistry (discovery + describe_all)
│   └── brains/
│       └── base.py           # Brain ABC (generate method)
├── db/
│   ├── base.py               # DeclarativeBase + TimestampedBase
│   ├── session.py            # AsyncEngine + get_db dependency
│   └── models/
│       ├── user.py           # User (email, hashed_password, is_active)
│       ├── conversation.py   # Conversation (user_id FK, title)
│       ├── message.py        # Message (conversation_id FK, role, content)
│       └── safety_event.py   # SafetyEvent (message_id FK, user_id FK, level)
├── routes/
│   ├── auth.py               # POST /register, POST /login
│   ├── conversations.py      # POST/GET /conversations, GET /:id, POST /:id/messages
│   ├── chat.py               # Legacy test endpoint (GET /chat/test)
│   └── health.py             # GET /health
├── server/
│   └── app.py                # FastAPI factory + CORS + router registration
├── services/
│   ├── conversation.py       # ConversationService stub (future orchestration)
│   └── safety.py             # SafetyService: RiskLevel enum, keyword classifier, crisis response
└── orchestration/
    └── __init__.py            # Documented pipeline contract (not yet implemented)
```

---

## Frontend Project Structure

```
src/
├── context/
│   └── AuthContext.tsx        # Global auth state + token persistence
├── navigation/
│   ├── types.ts              # Route param types (Chat takes optional conversationId)
│   ├── RootNavigator.tsx     # Auth/App stack split based on AuthContext
│   ├── AuthNavigator.tsx     # Login + Signup screens
│   └── AppNavigator.tsx      # Bottom tabs: Home, Chat, Mood, Memory, Crisis
├── screens/
│   ├── HomeScreen.tsx        # Conversation list (real API) + "New Conversation" action
│   ├── ChatScreen.tsx        # Message list + send (real API, lazy conversation creation)
│   ├── LoginScreen.tsx       # Wired to auth.ts
│   ├── SignupScreen.tsx      # Wired to auth.ts
│   └── ...                   # MoodCheckin, MemoryInspector, CrisisSupport (shells)
├── services/
│   ├── api.ts                # Base URL resolution + authGet/authPost with Bearer
│   ├── auth.ts               # login/signup/logout + SecureStore persistence
│   └── conversations.ts     # listConversations, getConversation, createConversation, sendMessage
└── constants/
    └── colors.ts             # Design tokens
```

---

## Database Schema

All tables use UUID primary keys and `created_at`/`updated_at` timestamps.

- **`users`**: `id`, `email` (unique, indexed), `hashed_password`, `is_active`
- **`conversations`**: `id`, `user_id` (FK → users, cascade delete, indexed), `title`, `safety_state`, `crisis_started_at`, `post_crisis_low_streak`
- **`messages`**: `id`, `conversation_id` (FK → conversations, cascade delete, indexed), `role`, `content`
- **`safety_events`**: `id`, `message_id` (FK → messages, nullable), `user_id` (FK → users), `level`, `response_mode`, `crisis_bypass`

---

## Authentication Flow

1. User submits credentials → `authService.login()` → `POST /api/v1/auth/login`
2. Backend: looks up User by email via `AsyncSession`, verifies PBKDF2 hash, signs JWT with user UUID as `sub`
3. Frontend: stores token in `expo-secure-store`, updates `AuthContext`, flips nav stack
4. All subsequent requests use `api.authGet`/`authPost` which auto-attach `Authorization: Bearer <token>`
5. Protected routes use `get_current_user` dependency which decodes the JWT and loads the User from DB

---

## Execution Architecture (Scaffolded, Not Yet Implemented)

The future pipeline is: **context → tools → response**

| Type | Purpose |
|---|---|
| `ExecutionContext` | Per-turn state: user, conversation, message, response mode, memory slots, tool results |
| `ResponseMode` | Enum: `reflect`, `vent`, `plan`, `grounding`, `crisis` |
| `Tool` (ABC) | Base class for callable tools. Declares `name`, `description`, `run()` |
| `ToolCall` | LLM-produced request to invoke a tool |
| `ToolResult` | Structured output from tool execution |
| `ToolRegistry` | Central registry for tool discovery and LLM prompt injection |
| `Brain` (ABC) | Response generation strategy. Takes `ExecutionContext`, returns response string |

The orchestrator (not yet built) will: build context → classify safety → retrieve memory → execute tools → select brain → generate response.

---

## Safety Classification Pipeline

Every `POST /conversations/:id/messages` runs this pipeline:

1. Store user message → flush to get UUID
2. `SafetyService.classify_risk()` — deterministic keyword matching
3. `map_risk_to_mode()` — maps `RiskLevel` → `ResponseMode`
4. Build `ExecutionContext` with the resolved mode
5. If `HIGH` or `CRITICAL` → log a `SafetyEvent` to the database
6. If `CRITICAL` → bypass LLM entirely, return hardcoded 988 crisis response
7. Otherwise → generate response (mocked for now)

### Risk Classification Rules (v1)

| RiskLevel | → ResponseMode | Trigger examples |
|---|---|---|
| `low` | `reflect` | "I had a good day", normal conversation |
| `medium` | `vent` | "so alone", "can't cope", "nobody cares" |
| `high` | `grounding` | "hurt myself", "don't want to be here" |
| `critical` | `crisis` | "kill myself", "want to die", "end my life" |

Keyword lists are in `services/safety.py`.

### Post-Crisis Cooldown

When a `crisis` event occurs, the system locks into a sticky `post_crisis` state instead of abruptly dropping back to `normal`. 
- **Exit Strategy:** 3 consecutive `LOW` risk messages **AND** 5 minutes elapsed since crisis. (Configurable in `config.py`)
- **Flooring:** During `post_crisis`, the `response_mode` is floored at `vent` regardless of the classifier output, ensuring a supportive tone.
- **Re-escalation:** Any `HIGH` or `CRITICAL` message immediately re-escalates the state to `crisis`.

---

## Conversation API Endpoints

All conversation routes require Bearer auth. Users can only access their own data.

| Method | Path | Response |
|---|---|---|
| `POST` | `/api/v1/conversations` | `ConversationOut` |
| `GET` | `/api/v1/conversations` | `ConversationOut[]` (newest first) |
| `GET` | `/api/v1/conversations/:id` | `ConversationDetail` (with ordered messages) |
| `POST` | `/api/v1/conversations/:id/messages` | `SendMessageResponse` — `{ messages: [...], response_mode: "reflect" }` |

**Note**: The assistant reply is currently mocked. `response_mode` is returned so the frontend can adapt UI behavior per mode.

---

## Development Environment

- **OS**: Windows (backend runs natively, not in WSL)
- **Python venv**: `backend/venv-win/`
- **Start backend**: `cd backend && .\venv-win\Scripts\Activate.ps1 && alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload`
- **Start frontend**: `cd mobile && npx expo start --android`
- **Emulator**: `api.ts` auto-maps to `10.0.2.2:8000` on Android emulator, falls back to LAN IP for physical devices

---

## Current Status

**Completed**: Auth (E2E), Database (Alembic + SQLite), Conversation CRUD (frontend + backend), Execution architecture scaffolding, Safety risk classifier with mode selection and crisis bypass.

**Next up**: LLM integration (connect a Brain implementation to a real model), then wire it through the orchestrator to replace the mocked assistant reply.
