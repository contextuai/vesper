# Connections & Channels Reference Guide

> **Note (Vesper v1.2.0):** The legacy **Distributions** hub (`/connections`), social publishing flows (`LinkedIn`, `Twitter/X`, `Instagram`, `Facebook`), and `Reddit` polling were **retired** in Vesper v1.2.0. Visiting `/connections` now redirects to `/settings`.
>
> Use **Tools & MCP** (`/personas`) to connect MCP servers, REST APIs, and local tools, and configure privacy/redaction controls under **Settings → Security & Audit**. The Telegram webhook notes below remain applicable only for advanced webhook/approval setups when **Advanced Mode** is enabled.

---

## Telegram Bot (Advanced Webhook Reference)

**Type:** Token paste

### Setup Steps

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a display name (e.g., `"My Vesper Assistant"`) and username (e.g., `my_vesper_assistant_bot`)
4. Export `TELEGRAM_BOT_TOKEN` in the backend environment
5. Expose local port `18741` for webhook delivery if receiving inbound messages:

```bash
ngrok http 18741
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook?url=YOUR_NGROK_URL/api/v1/channels/telegram/webhook"
```

Remove the webhook when finished:

```bash
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/deleteWebhook"
```

### Auto-Reply & Approval Queue

1. Enable **Advanced Mode** in **Settings → Developer** to view the **Approvals** (`/approvals`) and **Workspace** (`/crews`) surfaces.
2. Link a trigger via API (`/api/v1/triggers/`) with `"approval_required": true` if you want human review before outbound replies are sent.
3. Pending non-social approvals surface both in `/approvals` and inline in **Chat**.
