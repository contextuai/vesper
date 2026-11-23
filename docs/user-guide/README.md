# Vesper — User Guide

Welcome to **Vesper** (by ContextuAI), your private, local-first desktop AI workstation. This guide covers Vesper's core 5-tab workspace as well as optional Advanced Mode / Full Solo modules.

## Core Modules (`Vesper v1.2.0` Default Navigation)

| # | Module | What it does |
|---|--------|-------------|
| 1 | [Chat](01-chat.md) | Stream conversations with local GGUF or cloud models, attach files with Smart Context Bypass, and inspect your built-in **Memory & Recall** drawer |
| 2 | Local Docs (`/knowledge`) | Upload files or map local folders for hybrid BM25 + vector RAG with clickable `[1]`, `[2]` citations |
| 3 | [Models](02-model-hub.md) | Hardware-aware GGUF model downloads, GPU acceleration, and BYOK cloud AI providers |
| 4 | [Tools & MCP](03-personas.md) | Connect Model Context Protocol (MCP) servers, REST APIs, web search, and custom tool behaviors |
| 5 | [Settings](09-settings.md) | AI providers, Brand Voice, Appearance, Data & Export, **Security & Audit** (Local DLP, SQLite Audit Log, ABOM Export, Enterprise Policy), **Developer** (`/v1` server & Advanced Mode), and **About** |
| 6 | [IDE & OpenAI `/v1` Server](10-openai-endpoint.md) | Use Vesper as the local model backend for Cursor, Continue.dev, Cline, Aider, or Zed |

## Optional Modules (Advanced Mode / Unlock Full Solo)

Enable **Advanced Mode** under **Settings → Developer** to reveal Agents, Workspace (Crews), Automations, Memory, and Approvals in the sidebar, or use **Settings → About → Unlock Full ContextuAI Solo** for the 96-agent library and Coder workspace:

| Module | What it does |
|--------|--------------|
| [Agents](04-agents.md) | Browse pre-built business specialists organized by kind |
| [Workspace / Crews](05-crews.md) | Multi-agent workflows and run history |
| [Blueprints](06-blueprints.md) | Pre-built workflow templates |
| [Workspace (Legacy)](07-workspace.md) | Legacy standalone workspace overview |
| [Vesper Coder](11-coder.md) | Multi-role coding workspace (`Solo \| Coder` toggle when Full Solo is unlocked) |
| [Distributions (Retired)](08-connections.md) | Retired in Vesper v1.2.0 (`/connections` now redirects to `/settings`) |

## Quick Start

1. **Open Vesper** — No account or login required.
2. **Download a local model or add an API key** — Open **Models** to download a GGUF model matched to your RAM/VRAM, or visit **Settings → AI Providers** for cloud BYOK.
3. **Start chatting** — Head to **Chat**, pick a model, attach files or connect **Local Docs**, and send your first message.
4. **Connect tools** — Open **Tools & MCP** to attach local filesystem, Git, or custom MCP servers.

## Where is my data stored?

All user data stays on your machine:

- **Database:** `~/.contextuai-solo/data/contextuai.db` (SQLite)
- **Local models:** `~/.contextuai-solo/models/` (GGUF files)
- **Exports:** Downloaded to your default Downloads folder (including JSON backups, JSON/CSV audit logs, and ABOM snapshots)

## Screenshots

Screenshots referenced in these guides are located in [`docs/screenshots/`](../screenshots/).

| Screenshot | Module |
|-----------|--------|
| ![Chat](../screenshots/001-dashboard-chat.png) | Chat |
| ![Model Hub](../screenshots/002-ModelHub-Selection.png) | Model Hub |
| ![Models Installed](../screenshots/003-ModelsInstalled.png) | Model Hub |
| ![Tools & MCP](../screenshots/004-Personas.png) | Tools & MCP |
| ![Agent Library](../screenshots/006-AgentLibrary.png) | Agents (Advanced Mode) |
| ![Crews](../screenshots/008-CrewHome.png) | Crews (Advanced Mode) |
| ![Settings](../screenshots/014-Settings.png) | Settings |
