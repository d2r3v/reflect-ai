# Technical Reference: Reflect AI

This document provides a deep technical reference for the Reflect AI codebase. For a high-level overview, see [README.md](README.md). For LLM-oriented context, see [CLAUDE.md](CLAUDE.MD).

---

## Execution Pipeline

The system is designed around a single conceptual pipeline that processes each user message:

```
User Message
    │
    ▼
┌──────────────────┐
│ ExecutionContext  │  Build per-turn state (user, conversation, message)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Safety Classifier│  Determine ResponseMode (reflect/vent/plan/grounding/crisis)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Memory Retrieval │  Fetch relevant past context (future)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Tool Execution   │  Run any tools the LLM requested (future)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Brain            │  Generate response using selected strategy
└────────┬─────────┘
         │
         ▼
   Response + Persist
```

Currently, memory retrieval and tool execution are scaffolded but not implemented. The **safety classifier and mode selector are live** — critical messages bypass the pipeline entirely and return a deterministic crisis response.

---

## Core Domain Types

### ExecutionContext (`core/context/execution.py`)

The central data structure that flows through the pipeline.

```python
class ExecutionContext(BaseModel):
    session_id: str
    user_id: Optional[str]
    conversation_id: Optional[str]
    message_content: str
    response_mode: ResponseMode          # defaults to REFLECT
    retrieved_memories: List[Dict]       # populated by memory layer
    tool_results: List[Dict]             # populated by tool executor
    metadata: Dict[str, Any]
```

### ResponseMode (`core/context/execution.py`)

```python
class ResponseMode(str, Enum):
    REFLECT = "reflect"       # empathetic, exploratory
    VENT = "vent"             # active listening
    PLAN = "plan"             # structured goal-oriented
    GROUNDING = "grounding"   # sensory grounding exercises
    CRISIS = "crisis"         # deterministic safety response
```

### Tool System (`core/tools/`)

```python
class ToolCall(BaseModel):        # LLM says "call this tool with these args"
    tool_name: str
    arguments: Dict[str, Any]

class ToolResult(BaseModel):      # Tool returns structured output
    tool_name: str
    success: bool
    output: Any
    error: Optional[str]

class Tool(ABC):                  # Implement this to add a new tool
    name: str                     # (abstract property)
    description: str              # (abstract property)
    async def run(**kwargs) -> ToolResult
```

**ToolRegistry** (`core/tools/registry.py`): Central discovery. `register(tool)`, `get(name)`, `list_tools()`, `describe_all()` (for LLM prompt injection).

### Brain (`core/brains/base.py`)

```python
class Brain(ABC):
    async def generate(ctx: ExecutionContext) -> str
```

Each response mode will eventually map to a different Brain implementation (e.g., `ReflectBrain`, `CrisisBrain`).

### Safety Service (`services/safety.py`)

Deterministic, keyword-based risk classifier (v1). No ML dependencies.

```python
class RiskLevel(str, Enum):
    LOW = "low"          # normal conversation
    MEDIUM = "medium"    # emotional distress
    HIGH = "high"        # severe distress, self-harm language
    CRITICAL = "critical" # active crisis, immediate danger

class SafetyService:
    classify_risk(message: str) -> RiskLevel    # tiered keyword matching
    map_risk_to_mode(risk: RiskLevel) -> ResponseMode
    get_crisis_response() -> str                # hardcoded 988 lifeline message
```

**Mapping**: `low→reflect`, `medium→vent`, `high→grounding`, `critical→crisis`

**Pipeline behavior**: HIGH/CRITICAL log a `SafetyEvent` to the DB. CRITICAL bypasses LLM generation entirely.

---

## Database Layer

### Engine & Sessions (`db/session.py`)

- Uses `create_async_engine` with the URL from `config.py` (resolved to an absolute path).
- `AsyncSessionLocal` is an `async_sessionmaker` with `expire_on_commit=False`.
- `get_db()` is a FastAPI dependency that yields an `AsyncSession`.

### Models

All models inherit from `TimestampedBase` which provides `created_at` and `updated_at`.

| Model | Table | Key Relations |
|---|---|---|
| `User` | `users` | `conversations` (one-to-many) |
| `Conversation` | `conversations` | `user` (many-to-one), `messages` (one-to-many, cascade) |
| `Message` | `messages` | `conversation` (many-to-one), `safety_events` (one-to-many, cascade) |
| `SafetyEvent` | `safety_events` | `message` (many-to-one, nullable), `user` (many-to-one) |

### Migrations

Managed via Alembic with the async template. `render_as_batch=True` is enabled for SQLite compatibility. Run `alembic upgrade head` from the `backend/` directory.

---

## Authentication

### Password Hashing

Uses `hashlib.pbkdf2_hmac("sha256", ...)` with 260,000 iterations and a random 16-byte hex salt. Format: `{salt}${derived_key_hex}`. No C-extension dependencies.

### JWT

- Signed with `HS256` using `JWT_SECRET` from config.
- `sub` claim contains the user's UUID string.
- Default expiry: 30 minutes.
- `get_current_user` dependency decodes the token, extracts the UUID, and loads the `User` from the DB. Returns 401 if anything fails.

---

## API Endpoints

### Auth (`/api/v1/auth`)

| Endpoint | Body | Response |
|---|---|---|
| `POST /register` | `{email, password}` | `{access_token, token_type}` (201) |
| `POST /login` | `{email, password}` | `{access_token, token_type}` (200) |

### Conversations (`/api/v1/conversations`) — All require Bearer auth

| Endpoint | Body | Response |
|---|---|---|
| `POST /` | `{title?}` | `ConversationOut` (201) |
| `GET /` | — | `ConversationOut[]` (200, newest first) |
| `GET /:id` | — | `ConversationDetail` with `messages[]` (200) |
| `POST /:id/messages` | `{content}` | `SendMessageResponse` — `{ messages: [user, assistant], response_mode: "reflect" }` (201) |

### Other

| Endpoint | Description |
|---|---|
| `GET /api/v1/health` | Health check |
| `GET /api/v1/chat/test` | Legacy test route (returns `{reply: "..."}`) |

---

## Frontend Architecture

### State Management

- **AuthContext**: Holds `{token, isLoading, isLoggedIn}`. Bootstraps from `expo-secure-store` on app launch. Exposes `signIn`, `signUp`, `signOut`.
- **No global conversation state**: Each screen fetches its own data via `conversationsService`. This is intentional to keep things simple before adding a state manager.

### Navigation

```
RootNavigator
├── AuthNavigator (when !isLoggedIn)
│   ├── LoginScreen
│   └── SignupScreen
└── AppNavigator (when isLoggedIn)
    ├── Home tab      → HomeScreen
    ├── Chat tab      → ChatScreen (accepts optional conversationId)
    ├── Mood tab      → MoodCheckinScreen
    ├── Memory tab    → MemoryInspectorScreen
    └── Crisis tab    → CrisisSupportScreen
```

### Networking

`api.ts` resolves the backend URL dynamically:
1. If `__DEV__` + `hostUri` available → use the host IP from Expo debugger
2. If Android emulator → `10.0.2.2:8000`
3. Fallback → `localhost:8000`

All authenticated requests go through `api.authGet` / `api.authPost` which read the token from `expo-secure-store`.
