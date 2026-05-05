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
│ Memory Retrieval │  Score + fetch top-5 relevant memories → ctx.retrieved_memories
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
         │          └── CompanionBrain → LLMProvider → OpenAI
         ▼
   Response + Persist (messages + memories in same transaction)
```

**Live**: Safety classification, mode selection, crisis bypass, sticky post-crisis cooldown, real LLM generation, memory extraction and retrieval.

**Future**: Tool execution, orchestrator.

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
    response_mode: ResponseMode          # set by safety layer
    retrieved_memories: List[Dict]       # set by memory layer [{category, content}, ...]
    tool_results: List[Dict]             # populated by tool executor (future)
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

class CompanionBrain(Brain):   # mode-aware: per-mode system prompt + memory context
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

If `ctx.retrieved_memories` is non-empty, a context block is appended to the system prompt:

```
Context from previous conversations with this person:
- [dealing with] stressed about work pressure
- [copes by] journaling helps
- [preference] prefers: just listen

Use this context naturally. Do not announce that you remember it.
```

The block is silent — it informs tone and framing without the model saying "I remember you said...".

### LLM Provider (`core/llm/`)

```python
class LLMProvider(ABC):
    async def complete(messages, model, temperature, max_tokens) -> str

class OpenAIProvider(LLMProvider):  # wraps openai.AsyncOpenAI
    def __init__(api_key, default_model)
```

The provider is configured in `config.py` (`openai_api_key`, `openai_model`) and instantiated in the conversation route. Swapping the provider requires no changes to any Brain.

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

**Pipeline behavior**: MEDIUM/HIGH/CRITICAL log a `SafetyEvent` to the DB. CRITICAL bypasses LLM and memory extraction entirely.

---

## Memory System

### Overview

`MemoryService` (`services/memory.py`) extracts durable per-user facts from messages, persists them to the `user_memories` table, and retrieves relevant context before each response. All extraction is deterministic regex — no ML dependency.

The memory pipeline runs on every non-crisis message:
1. **Retrieve** — scored memories injected into `ExecutionContext` before brain generation
2. **Extract** — new facts parsed from the user's message after generation
3. **Persist** — new facts written to DB in the same transaction as the messages

Crisis messages (`ResponseMode.CRISIS`) skip both retrieval injection and extraction to keep that path purely deterministic.

### Memory Categories

| Category | What it stores | Example |
|---|---|---|
| `stressor` | Things causing distress | `"stressed about work pressure"` |
| `coping` | Activities / strategies that help | `"journaling helps"` |
| `preference` | How they want to be treated | `"prefers: just listen"` |
| `goal` | Things they're working toward | `"trying to sleep better"` |
| `support_need` | What kind of support they want | `"needs to vent, not be fixed"` |
| `personal_context` | Factual identity info | `"occupation: nurse"`, `"has two kids"` |

### Extraction Rules (v1)

26 compiled regex patterns, applied per message with `re.IGNORECASE`. All patterns require `confidence >= 0.70` to keep a fact.

| Category | Pattern examples | Confidence |
|---|---|---|
| `stressor` | "stressed/overwhelmed/anxious about X", "struggling with X", "my [thing] has been hard" | 0.75–0.85 |
| `coping` | "[gerund] helps me", "I find X calming", "when I X, I feel better" | 0.75–0.85 |
| `preference` | "I prefer you to X", "please don't X", "I don't want you to X" | 0.80–0.85 |
| `goal` | "I'm trying to X", "my goal is X", "I really want to X" | 0.75–0.85 |
| `support_need` | "need to vent", "not looking for advice", "need someone to listen" | 0.80–0.90 |
| `personal_context` | "I'm a [nurse/teacher/...]", "I work as X", "I have N kids", "I live alone" | 0.85–0.90 |

`personal_context` uses a fixed profession allowlist to avoid extracting vague or unwanted identity claims.

A `keywords` list is extracted from each fact's content by tokenising, lowercasing, removing stop words, and keeping words ≥ 3 chars. This list drives retrieval scoring.

### Deduplication

Before inserting a new fact, `persist_memories` loads all active memories for the user and checks for duplicates:

```
same category + keyword overlap ratio >= 50%  →  reinforce (increment times_reinforced, update last_reinforced_at)
otherwise  →  insert as new row
```

This means "work stress" observed on multiple days accumulates a reinforcement count rather than creating duplicate rows.

### Retrieval Scoring

`retrieve_memories(user_id, query, db, limit=5)` loads all active memories and scores each:

```
score = (keyword_overlap × 2.0) + (recency × 1.0) + (reinforcement × 0.5)
```

| Component | Formula | Range |
|---|---|---|
| `keyword_overlap` | `len(memory_keywords ∩ query_keywords)` | 0–N |
| `recency` | `max(0, 1 - days_since_reinforced / 30)` | 0.0–1.0 |
| `reinforcement` | `min(times_reinforced / 5, 1.0)` | 0.0–1.0 |

Top 5 by score are returned as `[{"category": ..., "content": ...}]` and placed into `ctx.retrieved_memories`. No minimum threshold — new users with few memories still get their best available context.

### UserMemory Model (`db/models/user_memory.py`)

| Column | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `user_id` | UUID FK → users | CASCADE delete, indexed |
| `category` | VARCHAR(50) | One of 6 categories above |
| `content` | TEXT | Human-readable fact |
| `keywords` | TEXT | JSON array of significant words |
| `source_message_id` | UUID FK → messages | Nullable, SET NULL on delete — provenance only |
| `times_reinforced` | INTEGER | Incremented on re-observation |
| `last_reinforced_at` | DATETIME(tz) | Used for recency scoring |
| `is_active` | BOOLEAN | Soft delete (supports future "forget this" feature) |

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
| `UserMemory` | `user_memories` | `user` (many-to-one, cascade) |

### Migrations

Managed via Alembic with the async template. `render_as_batch=True` is enabled for SQLite compatibility. Run `alembic upgrade head` from the `backend/` directory.

| Revision | Description |
|---|---|
| `34da07402df8` | Initial schema: users, conversations, messages, safety_events |
| `2b8f7a3e9c15` | Add user_memories table |

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
| `POST /:id/messages` | `{content}` | `SendMessageResponse` — `{ messages: [...], response_mode, safety_state }` (201) |

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

---

## Current Status

**Completed**: Auth (E2E), Database (Alembic + SQLite), Conversation CRUD (frontend + backend), Execution architecture scaffolding, Safety risk classifier with mode selection, crisis bypass, sticky post-crisis cooldown, safety event logging, LLM response generation via `CompanionBrain`/`CrisisBrain` with OpenAI, crisis-aware frontend UI, **structured memory system** (extraction, deduplication, retrieval scoring, `ExecutionContext` injection, `CompanionBrain` prompt integration).

**Next up**: Pass conversation history into the LLM context (currently only the most recent user message is sent). Then wire the Tool system and build the orchestrator.
