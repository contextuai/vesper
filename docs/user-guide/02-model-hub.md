# Model Hub

The **Models** / Model Hub view lets you configure which AI models are available in **Vesper**. You can download free local GGUF models that run on your hardware (with automatic RAM/VRAM fit scoring) or connect cloud providers via BYOK API keys.

![Model Hub](../screenshots/002-ModelHub-Selection.png)

---

## Getting Started

1. Open **Models** in the sidebar (or **Settings > AI Providers** for cloud keys).
2. Browse recommended local GGUF models or expand a cloud provider card.
3. Download a local model or enter your API key and click **Test Connection**.
4. Head to **Chat** to start using it.

## Cloud Providers

Vesper supports 6 cloud AI provider types under **Settings > AI Providers**:

| Provider | Models | Key Required |
|----------|--------|-------------|
| **Anthropic Claude** | Claude Sonnet, Opus, Haiku | Yes |
| **OpenAI** | GPT-4o, GPT-4o mini, GPT-4 Turbo, O1 Preview | Yes |
| **Google Gemini** | Gemini 2.0 Flash/Pro, Gemini 1.5 Flash | Yes |
| **AWS Bedrock** | Claude 3 Sonnet/Haiku, Titan | Yes (AWS credentials) |
| **Ollama** | Whatever you've pulled on the local server — discovered automatically | No (local server) |
| **OpenAI-Compatible** | Any `/v1` server — vLLM, LM Studio, llama.cpp server, TGI, LiteLLM, OpenRouter | Base URL required, key optional |

Anthropic, OpenAI, Google Gemini, and Ollama models are discovered live, so the list stays in step with what your account (or your local Ollama server) actually serves.

### Adding an API Key

1. Expand the provider card.
2. Paste your API key into the input field.
3. Click **Test Connection** to verify it works.
4. A green checkmark confirms the connection is active.

### Getting API Keys

- **Anthropic:** [console.anthropic.com](https://console.anthropic.com)
- **OpenAI:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Google:** [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

## Local AI Models

Local GGUF models run entirely on your machine (Apple Metal on Apple Silicon macOS; CPU in Windows and Linux release builds) — no internet, no API keys, completely private.

![Models Installed](../screenshots/003-ModelsInstalled.png)

### Built-in Catalog & Hardware X-Ray

Vesper ships with **41 curated GGUF models** across 9 families (Qwen 3.5 / 3 / 2.5 Coder, Gemma 4 / 3, DeepSeek R1, Llama 3, Mistral, Phi-4) plus live discovery across **140,000+ GGUF models on Hugging Face** and Enterprise `models.json` catalog overrides:

| Your RAM | Example Local Models | Best For |
|----------|----------------------|----------|
| **4 GB** | Qwen 3.5 0.8B, Gemma 3 1B, Llama 3.2 1B | Fast triage and quick local tests |
| **8 GB** | Qwen 3.5 4B, Qwen 3 8B, DeepSeek R1 7B, Qwen 2.5 Coder 7B | Daily chat and local IDE coding |
| **16 GB** | Qwen 3.5 9B, Qwen 3 14B, Phi-4 14B, DeepSeek R1 14B | Stronger reasoning and long context |
| **32 GB+** | Qwen 3.5 35B-A3B, Qwen 3 32B, Gemma 4 31B, DeepSeek R1 32B | Heavy analysis and local multi-step tasks |

### Downloading a Model

1. Open **Models** in the sidebar — Hardware X-Ray automatically scores each model against your detected RAM and GPU.
2. Find a model that fits your hardware and click **Download**.
3. A progress bar tracks the ranged-HTTPS download, followed by **SHA-256 verification** (required when Enterprise policy enforces checksums).
4. Once downloaded, the model appears with a **"Downloaded"** badge and is ready in **Chat**.

Models are stored in `~/.contextuai-solo/models/` as GGUF files.

### After Downloading

After downloading, click **Sync** to register the model in the app. It will then appear in the Chat model dropdown.

## AI Mode Toggle

The sidebar has an **AI Mode** toggle that switches between:

- **Local** (green) — only shows locally downloaded models
- **Cloud** (blue) — only shows cloud provider models

Use the **"All models"** button in Chat to see all models regardless of mode.

## Tips

- **Start with a cloud provider** if you want the best quality — Anthropic Claude or OpenAI GPT-4o are excellent choices.
- **Download a local model** if privacy is your priority or you don't have internet access.
- **Local models are slower** than cloud models but completely free and private.
- **You can use both** — switch between local and cloud models depending on the task.
- **Test your connection** after adding an API key to make sure it's working before starting a chat.
