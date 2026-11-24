# Vesper

### Quiet, sovereign AI on your desktop — by ContextuAI

[![Website](https://img.shields.io/badge/Website-contextuai.com%2Fvesper-1D5C43.svg)](https://contextuai.com/vesper)
[![Docs](https://img.shields.io/badge/Docs-contextuai.com%2Fdocs-10B981.svg)](https://contextuai.com/docs)
[![GitHub](https://img.shields.io/badge/GitHub-contextuai%2Fvesper-181717.svg)](https://github.com/contextuai/vesper)
[![License](https://img.shields.io/badge/License-Apache%202.0%20with%20Commons%20Clause-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.2.0-brightgreen.svg)]()
[![Tauri](https://img.shields.io/badge/Built%20with-Tauri%20v2-FFC131.svg)](https://tauri.app/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python%203.11+-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://sqlite.org/)

**Vesper** is a privacy-first desktop AI workstation built for individuals, engineers, and security-conscious teams. Run local GGUF models on your own hardware or bring your own cloud API keys — with private local document RAG, MCP tool calling, on-device PII/secret redaction, zero-egress Airplane Lock, and an exportable SQLite audit log + AI Bill of Materials (ABOM).

Everything runs locally on your machine. No accounts. No cloud sync. No telemetry.

<p align="center">
  <a href="https://github.com/contextuai/vesper/releases/latest"><img src="https://img.shields.io/badge/Download-Latest%20Release-10B981?style=for-the-badge&logo=github" alt="Download Latest Release"></a>
</p>

> **Ready to try it?** Download the installer for your platform from the [Releases page](https://github.com/contextuai/vesper/releases/latest) — Windows (`.exe`/`.msi`), macOS (`.dmg`), or Linux (`.deb`/`.rpm`). No build steps required.
>
> **New here?** Read the [User Guide](docs/user-guide/README.md) to get started.

> **Which model should I run?** For general local use, **Qwen 3.5 4B / 9B** or **Gemma 4** deliver strong speed and tool calling on 8–16 GB laptops. Lightweight `1B–1.5B` models are great for fast triage and quick tests. Vesper automatically checks your RAM and GPU VRAM in **Models** to recommend the best fit.

![Vesper Preview](docs/solo-preview.gif)

<details>
<summary><strong>View screenshots</strong></summary>

| | |
|:---:|:---:|
| ![Chat](docs/screenshots/001-dashboard-chat.png) **Chat & Workspace** | ![Model Hub](docs/screenshots/002-ModelHub-Selection.png) **Model Hub** |
| ![Models Installed](docs/screenshots/003-ModelsInstalled.png) **Installed Models** | ![Tools & MCP](docs/screenshots/004-Personas.png) **Tools & MCP** |
| ![Settings](docs/screenshots/014-Settings.png) **Settings** | ![Knowledge & Agents](docs/screenshots/006-AgentLibrary.png) **Agents (Advanced Mode)** |

</details>

---

## Core Vesper Features (`v1.2.0`)

### Focused 5-Tab Navigation
Vesper defaults to a clean, zero-bloat workspace:
- **Chat** — Streaming chat with file attachments, collapsible reasoning blocks, clickable RAG citations, inline tool-approval prompts, and a built-in **Memory & Recall** drawer.
- **Local Docs** — Private local knowledge bases for uploaded files and auto-synced folders on disk.
- **Models** — Hardware-aware GGUF discovery, download, SHA-256 verification, and runtime controls.
- **Tools & MCP** — Connect Model Context Protocol (MCP) servers, REST APIs, web search, and local file/document tools.
- **Settings** — AI providers (BYOK), Brand Voice, Appearance, Data & Export, Security & Audit, Developer (`/v1` server & Advanced Mode), and About.

### Smart Context Bypass & Hybrid RAG (`Local Docs`)
- **Upload or map whole folders** (PDF, DOCX, TXT, Markdown, HTML, RTF, CSV, JSON) with scheduled auto-sync (`manual` / `1h` / `6h` / `24h`) and large-folder guardrails.
- **Smart Context Bypass**: Dropped chat files that fit within your active model's context window (`n_ctx`) are injected directly in full instead of lossy chunking.
- **Hybrid BM25 + Vector Search**: Larger folders use combined lexical BM25 and dense vector search powered by a bundled local embedding model (`all-MiniLM-L6-v2` ONNX) stored in SQLite, returning answers with clickable `[1]`, `[2]` file and page citations.

### Privacy Shield, Local DLP & Enterprise Governance
- **Airplane Lock & Privacy Shield**: Live outbound egress ledger and a strict **Airplane Lock** kill-switch that blocks all non-loopback network calls at runtime (`EgressBlockedError`). Can be policy-locked by IT administrators via environment variables or OS policy files.
- **On-Device Local DLP**: Pre-flight local scanner that automatically redacts sensitive PII and secrets (API keys, emails, SSNs, and custom org regex rules) before prompts leave your machine.
- **SQLite Audit Log & 1-Click ABOM Export**: Tamper-evident local audit trail paired with 1-click **JSON** and **CSV** exports of your AI Bill of Materials (installed GGUF filenames, sizes, SHA-256 digests, integrity verification status, DLP posture, Airplane Lock state, and audit counts).
- **Enterprise Model Catalog Override**: Point Vesper to an internal `models.json` over HTTPS, `file://`, or a local filesystem path (works offline under Airplane Lock), optionally enforce **Exclusive Catalog Mode**, and require **SHA-256 verification** on GGUF downloads and loads.

### Local OpenAI-Compatible `/v1` Server
Point **Cursor**, **Continue.dev**, **Cline**, **Aider**, **Zed**, or any OpenAI SDK client at `http://localhost:18741/v1` to power local coding and IDE autocomplete with your downloaded GGUF models or saved provider keys. Manage the server toggle in **Settings → Developer**.

### Opt-In Advanced Mode & Full Solo Unlock
Need multi-agent orchestration?
- Enable **Advanced Mode** in **Settings → Developer** to reveal **Agents**, **Workspace (Crews)**, **Automations**, **Memory**, and **Approvals** in the sidebar.
- Use **Unlock Full ContextuAI Solo** in **Settings → About** whenever you want the 96-agent business library, 10 workflow blueprints, and the **Coder** project mode (`Cmd/Ctrl+Shift+M`) enabled in-place with zero reinstallation.

---

## Hardware & Local Model Fit

Vesper inspects your system RAM and GPU automatically to score model fit and recommend compatible GGUF quantizations. Pre-built **macOS (Apple Silicon)** releases use **Apple Metal**; pre-built **Windows and Linux** release binaries currently run CPU inference (CUDA and Vulkan offload are available when building `llama-cpp-python` from source):

| Your RAM | Example Local Models |
|----------|----------------------|
| 4 GB | Qwen 3.5 0.8B, Gemma 3 1B, Llama 3.2 1B |
| 8 GB | Qwen 3.5 4B, Qwen 3 8B, DeepSeek R1 7B, Mistral 7B, Qwen 2.5 Coder 7B |
| 16 GB | Qwen 3.5 9B, Qwen 3 14B, Phi-4 14B, DeepSeek R1 14B, Qwen 2.5 Coder 14B |
| 32 GB+ | Qwen 3.5 35B-A3B, Qwen 3 32B, DeepSeek R1 32B, Gemma 3 27B |

Set `LOCAL_MODEL_GPU_LAYERS=0` to force CPU execution, or connect **Anthropic Claude**, **OpenAI**, **Google Gemini**, **AWS Bedrock**, **Ollama**, or any **OpenAI-Compatible** `/v1` endpoint in **Settings → AI Providers**.

Pair Vesper's local `/v1` server (`http://localhost:18741/v1`) with **[Hey Spark](https://github.com/contextuai/hey-spark)** (MIT open-source local voice assistant) or your IDE (**Cursor**, **Continue.dev**, **Cline**, **Aider**, **Zed**) for a 100% local voice + coding stack.

---

## System Requirements

Vesper is a native Tauri v2 desktop app (~500 MB installed). Running cloud providers via BYOK requires minimal resources; running local GGUF models depends on the model size you choose.

### Supported Platforms

| OS | Versions | Installer |
|----|----------|-----------|
| **Windows** | Windows 10 (1809+) or Windows 11, 64-bit | `.exe` (NSIS) or `.msi` (`x64`) |
| **macOS** | macOS 12 Monterey or later | `.dmg` — **Apple Silicon only** (M1/M2/M3/M4) |
| **Linux** | Ubuntu 22.04+, Fedora 38+, or equivalent glibc distro | `.deb`, `.rpm`, or `.AppImage` (`x86_64`) |

---

## Download & Install

**[Download the latest release](https://github.com/contextuai/vesper/releases/latest)** — pre-built installers for all platforms, no build steps needed.

| Platform | Installer | How to Install |
|----------|-----------|----------------|
| **Windows** | `Vesper_*_x64-setup.exe` / `.msi` | Run the installer. If SmartScreen warns "Windows protected your PC", click **"More info"** → **"Run anyway"** |
| **macOS** | `Vesper_*.dmg` | Open the DMG, drag **Vesper.app** to Applications, then clear Gatekeeper's quarantine flag once in Terminal |
| **Linux** | `.deb` / `.rpm` / `.AppImage` | Install with `dpkg -i`, `rpm -i`, or `chmod +x` for AppImage |

**macOS Gatekeeper fix** — After dragging the app to Applications, run this once in Terminal:

```bash
xattr -cr "/Applications/Vesper.app"
```

### Feedback & Issues

1. Check your version under **Settings → About**.
2. [Open a GitHub Issue](https://github.com/contextuai/vesper/issues/new) with your OS, version, and steps to reproduce.

---

## For Developers

<details>
<summary><strong>Architecture</strong></summary>

```
+-------------------+     +-------------------------+     +--------------------+
|                   |     |                         |     |                    |
|   Tauri v2 Shell  |     |   FastAPI Backend       |     |   AI Providers     |
|   (Rust)          |     |   (Python 3.11+)        |     |   (Local / BYOK)   |
|                   |     |                         |     |                    |
|  +-------------+  |     |  +-------------------+  |     |  - Local GGUF      |
|  | Vite + React|  | --> |  | SQLite Database   |  | --> |  - Ollama / v1     |
|  | SPA (1420)  |  | API |  | (via async adapter)|  |     |  - Anthropic       |
|  +-------------+  |     |  +-------------------+  |     |  - OpenAI / Gemini |
|                   |     |  Port 18741             |     |  - AWS Bedrock     |
+-------------------+     +-------------------------+     +--------------------+
```

- **Frontend**: React 19 SPA served by Vite dev server (port `1420`) or bundled into the Tauri desktop shell
- **Backend**: FastAPI on `127.0.0.1:18741` with SQLite via an async adapter layer
- **Data Storage**: Local user state stays under `~/.contextuai-solo/` (`~/.contextuai-solo/data/contextuai.db` and `~/.contextuai-solo/models/`)

</details>

<details>
<summary><strong>Project Structure</strong></summary>

```
vesper/
├── frontend/           # Tauri v2 + React 19 + Vite desktop app
│   ├── src/            # React components, routes, hooks, and API clients
│   ├── src-tauri/      # Tauri Rust shell configuration
│   └── tests/e2e/      # Playwright E2E test suite
├── backend/            # FastAPI server (Python 3.11+, SQLite)
│   ├── app.py          # Application entry point
│   ├── adapters/       # Database, auth, storage, scheduler adapters
│   ├── routers/        # API route handlers (chat, rag, dlp, audit, enterprise, v1)
│   ├── services/       # Business logic, inference, RAG, DLP, audit & policy
│   └── tests/          # Pytest unit and integration test suite
├── agent-library/      # Built-in agent templates (unlocked in Full Solo / Advanced Mode)
├── blueprints/         # 10 pre-built workflow templates
├── coder-templates/    # Starter projects for Coder mode
├── docs/user-guide/    # Per-module user guides
├── run.sh              # Convenience backend launcher (Linux/macOS)
├── run-tests.ps1       # Test runner (backend + frontend)
└── LICENSE             # Apache 2.0 with Commons Clause
```

</details>

<details>
<summary><strong>Quick Start (Development)</strong></summary>

### Prerequisites

- **Node.js 20+**
- **Python 3.11+**
- **Rust** (for Tauri desktop builds only)

### Installation

```bash
git clone https://github.com/contextuai/vesper.git
cd vesper

cd frontend && npm install
cd ../backend && pip install -r requirements.txt
```

### Running in Dev Mode

**Terminal 1 — Backend:**

```bash
cd backend
CONTEXTUAI_MODE=desktop python __main__.py --host 127.0.0.1 --port 18741
```

**Terminal 2 — Frontend:**

```bash
cd frontend
npm run dev
```

Open **http://localhost:1420**.

### Building Desktop Installers

```bash
# On Windows, build the frozen PyInstaller sidecar + NSIS/MSI installers:
./build.ps1

# Or directly via Tauri (once sidecar is built):
cd frontend && npm run tauri build
```

</details>

<details>
<summary><strong>Testing</strong></summary>

```powershell
# Backend tests (from backend/)
$env:CONTEXTUAI_MODE = "desktop"
pytest tests/ -v

# Frontend type check, build & Playwright E2E (from frontend/)
npx tsc --noEmit
npm run build
npx playwright test
```

</details>

### Contributing

Please read our [Contributing Guide](CONTRIBUTING.md) before opening a pull request.

---

## License

Vesper is released under the [Apache License 2.0 with Commons Clause](LICENSE).

See the [LICENSE](LICENSE) file for full details.

---

<p align="center">
  <strong>Built with care by ContextuAI</strong><br>
  <em>Quiet, sovereign intelligence on your metal.</em>
</p>
