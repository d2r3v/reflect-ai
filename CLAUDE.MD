# AI Context Guide (Reflect AI)

This file contains the core architectural, technological, and domain context needed for an LLM to assist effectively on the **Reflect AI: Memory-Aware Support Companion** project.

---

## 🏗 System Architecture & Stack

The application is definitively split between a mobile client and a Python backend.
- **Frontend (`/mobile`)**: React Native built with **Expo SDK 52**.
  - **Navigation**: `@react-navigation/native-stack`
  - **State**: React Context API (`AuthContext` for global session).
  - **Storage**: `expo-secure-store` (v14.0.1 for Expo 52 compatibility).
- **Backend (`/backend`)**: **FastAPI** (Async) running on Python >= 3.10.
  - **Database**: SQLite (via `aiosqlite` string `sqlite+aiosqlite:///./masc.db`).
  - **ORM**: SQLAlchemy 2.0 (Declarative Base, async sessions).
  - **Migrations**: Alembic (using `render_as_batch=True` due to SQLite constraint limits).
  - **Auth**: JWT Bearer + `python-jose`, using native PBKDF2 via `hashlib` (Bcrypt/passlib C-extensions are avoided due to Windows Python compatibility issues).

---

## 🛠 Engineering Rules & Anti-Patterns

1. **Keep it minimal and MVP-focused**: No Redis, no background workers (Celery), no websockets, no vector DBs, or extra framework blobs until strictly necessary.
2. **Business logic placement**: Do not put heavy business logic inside `/routes`. Use `/core`, `/lib`, or `/services`.
3. **Safety first**: Critical-risk behavior must be deterministic and must bypass normal LLM generation limits.
4. **Prompt storage**: Store prompt text in dedicated files or constants, not inline inside API handlers.
5. **No Telepathy allowed**: When providing user instructions for running commands, provide the exact commands (including `cd` steps and whether elevation is required).

---

## 📂 Backend Project Structure
- `src/core/`: Core domain logic (e.g., `auth`, `context`, `tools`, `brains`).
- `src/db/`: Database configuration (`base.py`, `session.py`) and ORM wrappers.
  - `src/db/models/`: Contains `user.py`, `conversation.py`, `message.py`, `safety_event.py`.
- `src/routes/`: FastAPI routers (`auth.py`, `chat.py`, `health.py`).
- `src/server/`: FastAPI app initialization and middleware wrapper (`app.py`).

---

## 🗄 Current Database Schema
- **`users` (`User`)**: `id`, `email`, `hashed_password`, `is_active`, `created_at`, `updated_at`.
- **`conversations` (`Conversation`)**: `id`, `user_id` (FK to users), `title`, timestamps.
- **`messages` (`Message`)**: `id`, `conversation_id` (FK to conversations), `role` (user/assistant/system), `content`, timestamps.
- **`safety_events` (`SafetyEvent`)**: `id`, `message_id` (FK to messages, nullable), `user_id` (FK to users), `level`, timestamps. (Placeholder for future safety routing layer).

---

## 🔒 Authentication Flow
1. **Frontend**: The user submits credentials to `authService.login`.
2. **Backend**: Checks `users` table via `AsyncSession`. If PBKDF2 hashes match, signs a JWT using the UUID.
3. **Frontend**: Parses response gracefully via custom `parseError` handler so 4xx/5xx texts don't crash `.json()`, stores token in `expo-secure-store`, updates `AuthContext`, and flips navigation stacks.
4. **Headers**: `api.ts` attaches `Authorization: Bearer <token>` natively to all future authenticated requests via `authGet` and `authPost`.

---

## 💻 Development Environment Context
- **OS**: The user is running **Windows**. 
- **WSL Limitations**: We encountered issues routing physical mobile device traffic through the WSL2 NAT. As a result, **we run the backend directly natively on Windows** using a standard `venv-win` virtual environment. 
- **Emulator Mapping**: The frontend `api.ts` maps `API_URL` to `10.0.2.2:8000` automatically for Android emulators, dropping back to the local ip for physical devices.
- **Starting Backend**: `.\venv-win\Scripts\Activate.ps1`, then `uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload`
- **Starting Frontend**: `npx expo start --android` (Use `--clear` if dependency mismatches occur).

---

## 🚀 Current Status & Next Up
- **Completed**: E2E Auth flow (Frontend + Backend), Database Initialization (Alembic + SQLite), Architecture structure.
- **Next Up**: Implementing the `POST /api/v1/conversations` and `GET /api/v1/conversations/{id}/messages` endpoints inside the chat domain. Hooking up LLM tools to the database entities.
