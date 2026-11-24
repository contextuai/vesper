# Settings

Settings is where you configure AI providers, customize your brand voice, adjust appearance, export local data, manage privacy/security & ABOM compliance, and toggle developer options.

![Settings](../screenshots/014-Settings.png)

---

## Getting Started

Navigate to **Settings** from the sidebar. The page has **7 tabs**.

## Tab 1: AI Providers

Configure the cloud and Ollama AI models available throughout **Vesper** (downloaded GGUF models live under **Models** in the sidebar as well). See the [Model Hub guide](02-model-hub.md) for detailed setup instructions.

**6 cloud/external provider types** alongside built-in Local GGUF models:

| Provider | Key Required | Notes |
|----------|-------------|-------|
| Local AI (Built-in) | No | Free GGUF models running locally (Apple Metal on macOS; CPU in Windows/Linux release builds; CUDA/Vulkan when compiled from source) |
| Anthropic Claude | Yes | Claude Sonnet, Opus, Haiku |
| OpenAI | Yes | GPT-4o, GPT-4o mini, o-series |
| Google Gemini | Yes | Gemini Flash / Pro |
| AWS Bedrock | Yes | Bedrock models via AWS credentials |
| Ollama | No | Local models via Ollama server. Expand the card, enter your server URL, and click **Test Connection** — Vesper probes the running Ollama server and displays a connected/saved indicator once verified |
| OpenAI-Compatible | No (base URL required, key optional) | Any `/v1` server — vLLM, LM Studio, llama.cpp server, TGI, LiteLLM, OpenRouter |

Anthropic, OpenAI, Google Gemini, and Ollama model lists are discovered live from your account (or your local Ollama server), so they stay in step with what's actually available.

For each cloud provider:
1. Expand the card.
2. Paste your API key.
3. Click **Test Connection** to verify.

## Tab 2: Brand Voice

Define your business identity so Vesper writes in your brand's tone and style.

**Fields:**

- **Business Name** — your company or brand name
- **Industry** — select from 12 options (Technology, Marketing & Advertising, Finance & Banking, Healthcare, Education, E-commerce & Retail, Creative & Design, Consulting, Legal, Real Estate, Manufacturing, Other)
- **Brand Description** — what your business does and what makes it unique
- **Target Audience** — who you're writing for
- **Content Topics** — subjects you frequently cover

A **Brand Voice Preview** updates dynamically as you type. Click **Save Brand Voice** to apply.

## Tab 3: Appearance

Customize how Vesper looks:

- **Theme**: **Light**, **Dark**, or **System** (follows your OS setting)
- **Color Theme**: **Vesper Emerald** (default), Warm Ember (Terracotta), Nocturne (Indigo), Cobalt Sapphire, Amethyst Quartz, or Cyber Lagoon
- **Font Size**: **Small**, **Medium**, or **Large**

## Tab 4: Data & Export

Manage your local SQLite data:

- **Export Data**: Downloads a JSON backup of your conversations, connectors, settings, and workflows.
- **Import from File**: Restores data from a previous JSON backup.
- **Clear All Data**: Permanently deletes local data after confirmation.

## Tab 5: Security & Audit

Enterprise privacy, redaction, and compliance controls:

- **Local DLP (On-Device PII & Secret Redaction)**: Automatically detects and redacts API keys, email addresses, SSNs, and custom organization patterns before prompts leave your machine, with a live redaction tester.
- **Local SQLite Audit Log & ABOM Export**: Browse recorded inference, tool, DLP, and policy events and export 1-click **JSON** or **CSV** compliance reports plus an **AI Bill of Materials (ABOM)** listing installed GGUF models, SHA-256 digests, Airplane Lock posture, and DLP status.
- **Enterprise Policy & Model Catalog**: Configure a custom `models.json` URL or local path (works offline under Airplane Lock), toggle **Exclusive Catalog Mode**, inspect IT-locked fields (`policy.json` / env vars), and enforce **SHA-256 verification**.

## Tab 6: Developer

- **Local OpenAI `/v1` Server**: Enable or disable Vesper's local `/v1/models`, `/v1/chat/completions`, and `/v1/completions` server on port `18741` (`http://127.0.0.1:18741/v1`) and open the Server Inspector.
- **Advanced Mode**: Toggle sidebar visibility for **Agents**, **Workspace (Crews)**, **Automations**, **Memory**, and **Approvals** (off by default for a focused 5-tab Vesper experience).

## Tab 7: About

- **App name and version** — Vesper (`v1.2.0`)
- **Edition controls** — Option to **Unlock Full ContextuAI Solo** (or switch back to Vesper Lite view) in-place without losing downloaded models
- **Updates** — Check if a newer release is available
