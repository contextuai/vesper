# CLAUDE.md

This file provides guidance when working with code in the **Vesper** (`contextuai/vesper`) repository.

## Project Overview

**Vesper** is a local-first, privacy-focused desktop AI workstation built with **Tauri v2** (Rust), **React 19** (TypeScript + Vite), and a **FastAPI** Python backend running as a PyInstaller sidecar process on port **18741**. All user data is stored locally in SQLite (`~/.contextuai-solo/data/contextuai.db`).

- **Default Edition (`lite` — Vesper)**: Set in `backend/settings.py` (`CONTEXTUAI_EDITION`, default `"lite"`) and `frontend/src/config/edition.ts` (`VITE_APP_EDITION`, default `"lite"`). Exposes a clean 5-tab sidebar (**Chat**, **Local Docs**, **Models**, **Tools & MCP**, **Settings**) with the Vesper Emerald theme and built-in **Memory & Recall** drawer in Chat.
- **Opt-In Advanced Mode & Full Solo**:
  - **Settings → Developer → Advanced Mode** toggles sidebar access to **Agents** (`/agents`), **Workspace** (`/crews`), **Automations** (`/automations`), **Memory** (`/memory`), and **Approvals** (`/approvals`).
  - **Settings → About → Unlock Full ContextuAI Solo** (`POST /api/v1/desktop/unlock-solo`, reversible via `POST /api/v1/desktop/switch-lite`) enables the 96-agent business library, blueprints, and the top-center `Solo | Coder` pill (`Cmd/Ctrl+Shift+M`).

## Commands

### Frontend (run from `frontend/`)
```bash
npm install                  # Install dependencies
npm run dev                  # Vite dev server on port 1420
npx tsc --noEmit             # Strict TypeScript check
npm run build                # Type check + Vite production bundle
npm run tauri dev            # Run full Tauri desktop app (dev mode)
npm run tauri build          # Build platform installers (.exe/.msi/.dmg/.deb/.rpm)
npx playwright test          # Run E2E tests (requires backend on 18741 & Vite on 1420)
npx playwright test tests/e2e/some-test.spec.ts  # Run a single E2E spec
```

### Backend (run from `backend/`)
```bash
pip install -r requirements.txt   # Install dependencies
CONTEXTUAI_MODE=desktop uvicorn app:app --host 127.0.0.1 --port 18741 --reload
CONTEXTUAI_MODE=desktop python __main__.py --host 127.0.0.1 --port 18741
CONTEXTUAI_MODE=desktop pytest tests/ -v
```

### Windows Release Build (from repo root)
```powershell
.\build.ps1                  # PyInstaller sidecar + flatten + Tauri .exe/.msi build
```

## Architecture

### Three-Layer Desktop App
```
Tauri Shell (Rust)  →  React SPA (port 1420)  →  FastAPI Sidecar (port 18741)
```

- **Tauri shell** (`frontend/src-tauri/src/`): Window management, system tray (`Vesper`), sidecar process lifecycle (`sidecar.rs`), IPC commands (`commands.rs`), `productName: "Vesper"` in `tauri.conf.json`.
- **React frontend** (`frontend/src/`): Routes in `routes/`, reusable UI in `components/ui/`, API clients in `lib/api/`, transport layer in `lib/transport.ts`.
- **FastAPI backend** (`backend/`): Entry point is `app.py` (`__main__.py` for frozen sidecar builds). Routers in `routers/`, business logic in `services/`, data access in `repositories/`, adapters in `adapters/`.

### Frontend-Backend Communication
- **Tauri mode**: React → Tauri IPC (`api_request`) → HTTP to sidecar
- **Dev / Browser mode**: React → direct HTTP fetch to `http://127.0.0.1:18741/api/v1`
- **Streaming**: SSE over HTTP via `streamRequest()` in `transport.ts`, using `AbortController` to cancel mid-stream. Backend `LocalModelService` serializes local GGUF inference safely with async locks.

### Database: SQLite with MongoDB-Compatible API
- `adapters/sqlite_adapter.py` — Async SQLite wrapper (`aiosqlite`)
- `adapters/motor_compat.py` — `DatabaseProxy` / `CollectionProxy` preserving Motor-style queries (`$set`, `$in`, `$regex`, `$gt`, etc.) over `_id TEXT PRIMARY KEY, data JSON NOT NULL`
- DB path: `~/.contextuai-solo/data/contextuai.db`

### Local AI Models (`routers/local_models.py`, `services/local_model_service.py`)
GGUF models stored in `~/.contextuai-solo/models/`. Inference via `llama-cpp-python` with automatic GPU offload (Apple Metal / NVIDIA CUDA / Vulkan) and CPU fallback, tunable via `LOCAL_MODEL_GPU_LAYERS`.
- Hardware-aware model recommendations via `services/hardware.py` and `services/model_fit_engine.py`.
- OTA model catalog discovery via `services/hf_hub_discovery.py` (`https://raw.githubusercontent.com/contextuai/vesper/main/catalog/models.json`).
- Frontend `AiModeProvider` (`contexts/ai-mode-context.tsx`) detects local models (`provider` case-insensitive `"local"` or `local:`/`local-` prefixes) and syncs with `chat.tsx` (`aiModeRef` + sequence guard).

### Smart Context Bypass & Hybrid RAG (`routers/knowledge_base.py`, `routers/personal_docs.py`, `services/rag_service.py`)
- Uses bundled `all-MiniLM-L6-v2` ONNX embeddings (384-dim, SQLite-backed) combined with BM25 lexical scoring for hybrid RAG retrieval and clickable `[1]`, `[2]` citations.
- When dropped files fit within the active model's context window (`n_ctx`), Smart Context Bypass injects full text directly rather than lossy chunking.
- Folder mappings auto-sync on schedule (`services/personal_docs_scheduler.py`) with configurable caps (`PERSONAL_DOCS_MAX_*`) and large-folder friction prompts.

### Security, Local DLP, Audit & Enterprise Governance (`v1.2.0`)
- **Privacy Shield & Airplane Lock** (`routers/privacy.py`, `services/net_guard.py`): Tracks outbound requests in an egress ledger and blocks non-loopback network traffic when Airplane Lock is active.
- **On-Device Local DLP** (`routers/dlp.py`, `services/dlp_service.py`): Pre-flight local regex/entity redactor for API keys, emails, SSNs, and org patterns (`VESPER_DLP_POLICY_PATH`).
- **SQLite Audit Log & ABOM Export** (`routers/audit.py`, `services/audit_service.py`, `repositories/audit_repository.py`): Records local audit events and exports JSON/CSV **AI Bill of Materials (ABOM)** snapshots (`VESPER_AUDIT_DB_PATH`). GGUF SHA-256 checksums are persisted to `VESPER_SHA256_CACHE_PATH` (`~/.contextuai-solo/data/model_sha256_cache.json`) and hashed asynchronously on a background worker for large models.
- **Enterprise Policy & Catalog Override** (`routers/enterprise.py`, `services/enterprise_policy.py`): Precedence: env vars (`VESPER_AIRPLANE_LOCK_ENFORCED`, `VESPER_CATALOG_URL`, `VESPER_CATALOG_EXCLUSIVE`, `VESPER_REQUIRE_SHA256`) → admin policy file (`VESPER_POLICY_FILE`, `~/.contextuai-solo/policy.json`, or OS path) → user settings (`VESPER_ENTERPRISE_SETTINGS_PATH`).

### Local OpenAI-Compatible `/v1` Server (`routers/openai_compat.py`)
- Exposes `GET /v1/models`, `POST /v1/chat/completions`, and `POST /v1/completions` on `http://localhost:18741/v1` across local GGUF models and configured BYOK providers (`services/model_dispatcher.py`).
- Can be toggled on/off in **Settings → Developer** (`routers/local_models.py` `/server-config`).

### Retired Surfaces (`v1.2.0`)
- Legacy `/connections` (**Distributions**), social publishing/pollers (`reddit_*`, `twitter_*`, `distribution_service.py`), and legacy SQL warehouse connectors (`postgres_connector.py`, `mysql_connector.py`, `mssql_connector.py`, `snowflake_connector.py`, `bedrock_service.py`, `autobuild/`, `codemorph/`) were retired in `#75` and `#80`. `/connections` redirects to `/settings`, and legacy social/distribution API endpoints return `404`.
- Pending pre-v1.2 social approvals left in local SQLite are filtered and retired on startup via `ApprovalService.retire_legacy_social_approvals()`.
- Connectors live under **Tools & MCP** (`/personas`) with MCP server presets (`Local Filesystem MCP`, `Git / Repo MCP`), REST API connectors, web search, and local file tools.

### Key Configuration & Port Convention
- `backend/settings.py` — Centralized env-var config (`EDITION = "lite"`, port `18741`).
- `frontend/src-tauri/tauri.conf.json` — Tauri config (`productName: "Vesper"`, identifier `com.contextuai.solo`).
- `frontend/vite.config.ts` — Path alias `@/` → `./src/`, dev port `1420`.
- Backend sidecar always runs on **port 18741** (`sidecar.rs`, `transport.ts`, `settings.py`).

### camelCase / snake_case Mismatch
Backend API returns camelCase (`messageType`, `messageId`, `sessionId`) while frontend types use snake_case (`message_type`, `message_id`, `session_id`). `normalizeMessage()` in `lib/api/chat-client.ts` bridges this gap.

## Code Conventions

- **Branching**: NEVER commit directly to `main` (branch-protected). Create a topic branch (`feat/<x>`, `fix/<x>`, `docs/<x>`, `chore/<x>`) and open a PR.
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
- **TypeScript**: Strict mode, functional components with hooks, `@/*` alias, `cn()` helper.
- **Python**: Type hints on signatures, Pydantic v2 models, async FastAPI I/O, PEP 8.
- **Theming**: Dark/light mode (`class` strategy) with **Vesper Emerald** (`sovereign-emerald`) default for Vesper Lite.

## Testing
- **E2E (Playwright)**: `frontend/tests/e2e/` (Chromium, single worker; global setup seeds wizard completion and `local` AI mode). Requires backend on `18741` and Vite on `1420`.
- **Backend (pytest)**: `backend/tests/` (`CONTEXTUAI_MODE=desktop`).
