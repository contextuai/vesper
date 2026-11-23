# Using Vesper from VS Code (and other IDEs)

**Vesper** exposes an **OpenAI-compatible HTTP API** on `http://localhost:18741`. Any tool that speaks the OpenAI Chat Completions or legacy Completions protocol can use Vesper as its model backend — no internet, no API costs, and your code stays on your machine.

Tested with: **Continue.dev**, **Cline / Roo Code**, **Cursor**, **Aider**, **Tabby**, **Cody**, **Zed**, and any OpenAI SDK client.

## What you get

| Endpoint | Purpose |
|---|---|
| `GET  /v1/models` | List the models Vesper can run |
| `POST /v1/chat/completions` | Chat messages → reply (streaming or not) |
| `POST /v1/completions` | Text completion with Fill-in-the-Middle (FIM) for inline autocomplete |

- **No auth.** Vesper binds to `127.0.0.1` only, so the endpoint is reachable from your machine but not from the network.
- **Toggleable.** Enable or disable the local `/v1` server under **Settings → Developer**.
- **Streaming works.** Pass `"stream": true` and you'll get standard SSE `data: {...}` chunks.
- **Local models out of the box.** Anything you downloaded from **Models** is selectable by its model ID.

## Before you start

1. Make sure **Vesper** is running (open the desktop app, or start the backend via `./run.sh`) and that **Local OpenAI `/v1` Server** is enabled in **Settings → Developer**.
2. In the app, open **Models** and download at least one local GGUF model — `qwen2.5-coder-7b` or `qwen3.5-4b` are great starting points for coding tasks.
3. Confirm the endpoint is up:

   ```bash
   curl http://localhost:18741/v1/models
   ```

   You should see a JSON list with the models you've downloaded.

## VS Code — Continue.dev

[Continue](https://continue.dev) is a popular open-source coding assistant for VS Code and JetBrains IDEs.

1. Install the **Continue** extension.
2. Open `~/.continue/config.json` (Continue creates it on first run) and add Vesper as a custom provider:

   ```json
   {
     "models": [
       {
         "title": "Vesper — Qwen Coder",
         "provider": "openai",
         "model": "qwen2.5-coder-7b",
         "apiBase": "http://localhost:18741/v1",
         "apiKey": "not-needed"
       }
     ],
     "tabAutocompleteModel": {
       "title": "Vesper — FIM",
       "provider": "openai",
       "model": "qwen2.5-coder-7b",
       "apiBase": "http://localhost:18741/v1",
       "apiKey": "not-needed"
     }
   }
   ```

3. Reload the Continue panel and pick **Vesper — Qwen Coder** from the model dropdown.
4. Inline autocompletion (the `tabAutocompleteModel`) uses `/v1/completions` with FIM — works out of the box.

## VS Code — Cline / Roo Code

[Cline](https://github.com/cline/cline) (and its fork **Roo Code**) is a full agentic assistant.

1. Install Cline.
2. Open the gear icon → **API Provider** → **OpenAI Compatible**.
3. Fill in:
   - **Base URL:** `http://localhost:18741/v1`
   - **API Key:** anything (e.g. `local`) — required by the form but ignored
   - **Model ID:** `qwen2.5-coder-7b` (or whichever model you downloaded)
4. Save. Start a new task and Cline routes every call through Vesper.

## Cursor

Cursor accepts custom OpenAI-compatible endpoints.

1. **Settings → Models → Override OpenAI Base URL** → `http://localhost:18741/v1`
2. **OpenAI API Key** → anything non-empty.
3. **Models → Add a custom model** → enter your Vesper model ID (e.g. `qwen2.5-coder-7b`) and enable it.

Note: Cursor's own hosted tab-autocomplete calls Cursor's cloud unless turned off; the chat panel uses Vesper directly.

## Aider

[Aider](https://aider.chat) talks to OpenAI-compatible endpoints out of the box.

```bash
export OPENAI_API_BASE=http://localhost:18741/v1
export OPENAI_API_KEY=not-needed
aider --model qwen2.5-coder-7b
```

## Zed

In Zed's `~/.config/zed/settings.json`:

```json
{
  "assistant": {
    "default_model": {
      "provider": "openai",
      "model": "qwen2.5-coder-7b"
    },
    "openai": {
      "api_url": "http://localhost:18741/v1",
      "available_models": [
        { "name": "qwen2.5-coder-7b", "max_tokens": 32768 }
      ]
    }
  }
}
```

Drop your `OPENAI_API_KEY` env var in Zed's secret store with any string — it just has to be present.

## Plain curl / OpenAI Python SDK

```bash
curl http://localhost:18741/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen2.5-coder-7b",
    "messages": [
      {"role": "system", "content": "You are a senior Python engineer."},
      {"role": "user", "content": "Write a generator that yields Fibonacci numbers."}
    ],
    "stream": true
  }'
```

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:18741/v1",
    api_key="not-needed",  # required by the SDK, ignored by Vesper
)

stream = client.chat.completions.create(
    model="qwen2.5-coder-7b",
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True,
)
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")
```

## Inline autocomplete (Fill-in-the-Middle)

If a tool sends a `prompt` plus a `suffix`, Vesper runs the model in FIM mode — ideal for inline code completion:

```bash
curl http://localhost:18741/v1/completions \
  -d '{
    "model": "qwen2.5-coder-7b",
    "prompt": "def fib(n):\n    ",
    "suffix": "\n    return result",
    "max_tokens": 128
  }'
```

The Qwen Coder, DeepSeek Coder, and Code Llama families all support FIM and produce useful completions.

## Choosing a model

Open **Models** in Vesper to see what's downloaded. Some recommendations for coding work:

| Use case | Model | Why |
|---|---|---|
| General coding chat | `qwen2.5-coder-14b` | Strong reasoning + code, fits 16 GB laptops |
| Tight RAM (≤8 GB) | `qwen2.5-coder-7b` | Strong quality in 8 GB |
| Inline autocomplete (FIM) | `qwen2.5-coder-7b` or `deepseek-coder-6.7b` | Fast first-token latency |
| Long context (32k+) | `qwen2.5-coder-14b`, `phi-4` | Bigger context window |
| Reasoning-heavy refactors | `deepseek-r1-distill-qwen-14b` | Built-in chain-of-thought |

The model ID Vesper expects is the ID listed by `GET /v1/models`.

## Using cloud models through the same endpoint

The `/v1/chat/completions` endpoint routes to **any** provider — just prefix the model name. Your IDE keeps pointing at `http://localhost:18741/v1`; Vesper handles the dispatch.

### Step 1 — Save your provider keys

Open **Settings → AI Providers** and add a key for any provider you want to use. Vesper stores keys locally and never sends them anywhere except the provider's own API (and respects Airplane Lock / Local DLP policies).

### Step 2 — Pick the prefixed model name

| Provider | Model ID prefix | Example |
|---|---|---|
| Anthropic | `anthropic:` | `anthropic:claude-sonnet-4-20250514` |
| Google Gemini | `google:` | `google:gemini-2.0-flash` |
| OpenAI | `openai:` | `openai:gpt-4o` |
| AWS Bedrock | `bedrock:` | `bedrock:anthropic.claude-3-sonnet` |
| Ollama (local) | `ollama:` | `ollama:qwen2.5:7b` |
| OpenAI-Compatible server | `openai_compat:` | `openai_compat:mistral-7b-instruct` |
| Local GGUF | *(bare name)* | `qwen2.5-coder-7b` |

`GET /v1/models` returns all available IDs — local and cloud — in one list. Ollama models are discovered automatically if Ollama is running.

### curl example

```bash
curl http://localhost:18741/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "anthropic:claude-sonnet-4-20250514",
    "messages": [
      {"role": "system", "content": "You are a senior Python engineer."},
      {"role": "user", "content": "Explain async generators in two sentences."}
    ],
    "stream": true
  }'
```

### Continue.dev — mix local and cloud in one config

With the dispatcher live you can give each Continue.dev role a different model:

```json
{
  "models": [
    {
      "title": "Vesper — Claude (cloud)",
      "provider": "openai",
      "model": "anthropic:claude-sonnet-4-20250514",
      "apiBase": "http://localhost:18741/v1",
      "apiKey": "not-needed"
    },
    {
      "title": "Vesper — Qwen Coder (local)",
      "provider": "openai",
      "model": "qwen2.5-coder-7b",
      "apiBase": "http://localhost:18741/v1",
      "apiKey": "not-needed"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Vesper — FIM (local)",
    "provider": "openai",
    "model": "qwen2.5-coder-7b",
    "apiBase": "http://localhost:18741/v1",
    "apiKey": "not-needed"
  }
}
```

Use a fast local model for inline autocomplete (latency matters) and a larger or cloud model for complex chat tasks.

## Troubleshooting

**`Connection refused`** — Vesper isn't running, or the Local OpenAI `/v1` toggle in **Settings → Developer** is switched off.

**`Model not found`** — The model isn't downloaded yet. Open **Models**, download it, then refresh.

**Slow first response** — Local models cold-start on the first request while the GGUF maps into memory. Subsequent requests in the same session are faster.

**High RAM usage** — You loaded a model too large for your machine. Unload it in **Models** and choose a smaller quantization.
