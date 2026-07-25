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
│ Safety Classifier│  Determine RiskLevel + 3-state SafetyState → ResponseMode
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Memory Retrieval │  Inject recent stored insights into the prompt (SQLite RAG)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Tool Execution   │  Run any tools the LLM requested (future)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ BrainRouter      │  Select Brain based on ResponseMode
└────────┬─────────┘
         │          ├── CrisisBrain (deterministic, no LLM)
         │          └── CompanionBrain → LLMProvider → Anthropic / OpenAI
         ▼
   Response + Persist
```

Tool execution is scaffolded but not yet implemented. **Safety classification, mode selection, crisis bypass, sticky post-crisis cooldown, memory extraction/retrieval, conversation auto-titling, and real LLM generation via `CompanionBrain` are all live.**

### Post-Crisis Cooldown (Sticky Safety State)

After a crisis event, the system does not immediately trust "I'm fine." Instead, it enters a **post-crisis cooldown** with a classifier-driven exit.

**State Machine**:
```
NORMAL ──(CRITICAL)──→ CRISIS
CRISIS ──(LOW or MEDIUM)──→ POST_CRISIS
CRISIS ──(HIGH or CRITICAL)──→ CRISIS (stays)
POST_CRISIS ──(streak met + time met)──→ NORMAL
POST_CRISIS ──(HIGH or CRITICAL)──→ CRISIS (re-escalate)
```

**Recovery counter rules** (during POST_CRISIS):
| Classification | Counter effect |
|---|---|
| `LOW` | +1 |
| `MEDIUM` | hold (no change) |
| `HIGH`/`CRITICAL` | → re-escalate to CRISIS |

**Exit conditions** (both must be met):
- `post_crisis_low_streak >= POST_CRISIS_REQUIRED_LOW_STREAK` (default: 3)
- Elapsed time since crisis ≥ `POST_CRISIS_MIN_DURATION_SECONDS` (default: 300)

**Three separate concepts** (never conflated):
- `risk_level` — what the classifier says (never mutated)
- `safety_state` — conversation state (`normal`/`crisis`/`post_crisis`), stored on conversation
- `response_mode` — how we respond, floored at `VENT` during `post_crisis`

**Conversation-level state fields**: `safety_state`, `crisis_started_at`, `post_crisis_low_streak`

**Config**: `POST_CRISIS_REQUIRED_LOW_STREAK` and `POST_CRISIS_MIN_DURATION_SECONDS` in `config.py`.

**Frontend behavior**:
| State | Banner | Crisis Card |
|---|---|---|
| `normal` | None | No |
| `crisis` | Full warning (💛 "You're not alone") | Yes (with Call 988 button) |
| `post_crisis` | Soft blue (🫂 "We're still here") | No |

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

### Brain System (`core/brains/`)

```python
class Brain(ABC):
    async def generate(ctx: ExecutionContext) -> str

class CompanionBrain(Brain):   # mode-aware: sends per-mode system prompt to LLM
class CrisisBrain(Brain):      # deterministic: returns hardcoded 988 response, no LLM
```

#### BrainRouter (`core/brains/router.py`)

Maps `ResponseMode` → `Brain`:
- `CRISIS` → `CrisisBrain()`
- Everything else → `CompanionBrain(provider)`

#### CompanionBrain System Prompts

| Mode | Tone |
|---|---|
| `reflect` | Empathetic, exploratory, asks a follow-up question |
| `vent` | Active listening, validates feelings, minimal advice |
| `plan` | Structured, goal-oriented, breaks problems into steps |
| `grounding` | Calm, concise sensory/breathing exercises |

### LLM Provider (`core/llm/`)

```python
class LLMProvider(ABC):
    async def complete(messages, model, temperature, max_tokens) -> str

class AnthropicProvider(LLMProvider):  # wraps anthropic.AsyncAnthropic (default)
    def __init__(api_key, default_model="claude-sonnet-5")

class OpenAIProvider(LLMProvider):     # wraps openai.AsyncOpenAI
    def __init__(api_key, default_model)
```

`create_llm_provider()` (`core/llm/factory.py`) selects the implementation from `LLM_PROVIDER` (`anthropic` default, or `openai`); each provider carries its own `default_model`, so Brains stay agnostic. Config lives in `config.py` (`llm_provider`, `anthropic_api_key`/`anthropic_model`, `openai_api_key`/`openai_model`). `AnthropicProvider` splits the `system` message out to the top-level API parameter and disables extended thinking for fast chat replies.

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

### Memory Service (`services/memory.py`)

Lightweight, deterministic keyword-based memory. Plain string storage in SQLite — **no vector database**.

```python
class MemoryService:
    extract_memory(db, user_id, message, source_message_id=None) -> Memory | None
    retrieve_memories(db, user_id, limit=5) -> list[Memory]
```

- **Extraction**: scans each user message for trigger phrases mapped to a category — `coping_strategy`, `preference`, or `recurring_stressor` — and stores the relevant sentence. Exact-duplicate insights are skipped, and elevated-risk turns (crisis/grounding) are not stored.
- **Retrieval / injection**: `CompanionBrain` fetches the user's most recent insights and appends them to the system prompt so replies can reference the user's history.
- **Transparency**: surfaced to the client via `GET /api/v1/memories` and the Memory Inspector screen.

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
| `Memory` | `memories` | `user` (many-to-one); columns `category`, `content`, `source_message_id` |

### Migrations

Managed via Alembic with the async template. `render_as_batch=True` is enabled for SQLite compatibility. Run `alembic upgrade head` from the `backend/` directory. Latest migration `b7f3c2a19d40` adds the `memories` table.

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
| `POST /:id/messages` | `{content}` | `SendMessageResponse` — `{ messages: [...], response_mode, safety_state, title }` (201) |

> On its first message, a conversation is auto-titled from that message (LLM summary with a snippet fallback); the resolved `title` is returned in `SendMessageResponse`.

### Memories (`/api/v1/memories`) — Requires Bearer auth

| Endpoint | Body | Response |
|---|---|---|
| `GET /` | — | `MemoryOut[]` — `{ id, category, content, created_at }` (200, newest first) |

### Other

| Endpoint | Description |
|---|---|
| `GET /api/v1/health` | Health check |
| `GET /api/v1/chat/test` | Legacy test route (returns `{reply: "..."}`) |

---

## Frontend Architecture

### State Management

- **AuthContext**: Holds `{token, isLoading, isLoggedIn}`. Bootstraps the token from the cross-platform `storage` module on app launch. Exposes `signIn`, `signUp`, `signOut`.
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

`api.ts` resolves the backend URL dynamically in dev:
1. Derive the host from Expo's `hostUri` (the machine running Metro) → `http://<host>:8000/api/v1`
2. On the Android emulator, `localhost`/`127.0.0.1` is rewritten to `10.0.2.2` (the emulator's alias for the host machine)
3. Fallback → `localhost:8000`

All authenticated requests go through `api.authGet` / `api.authPost`, which read the token from the cross-platform `storage` module (`storage.ts`): `expo-secure-store` on native, `localStorage` on web.

---

## Current Status

**Completed**: Auth (E2E), Database (Alembic + SQLite), Conversation CRUD (frontend + backend), Execution architecture scaffolding, Safety risk classifier with mode selection, crisis bypass, sticky post-crisis cooldown, safety event logging, **LLM response generation via `CompanionBrain`/`CrisisBrain` (Anthropic default, OpenAI optional)**, **SQLite RAG memory (extraction, retrieval, prompt injection, Memory Inspector)**, conversation auto-titling, and crisis-aware frontend UI.

**Next up**: Pass conversation history into the LLM context (currently only the most recent user message is sent), and upgrade keyword-based memory to semantic (vector) retrieval.

