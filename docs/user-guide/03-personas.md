# Tools & MCP (Connectors)

> **Vesper v1.2.0 Note:** Legacy SQL warehouse connectors (`PostgreSQL`, `MySQL`, `MSSQL`, `Snowflake`) were retired in Vesper v1.2.0. Use **MCP Server** presets or custom REST API connectors below instead.

**Tools & MCP** (`/personas`) lets you create and manage Model Context Protocol (MCP) servers, web search connectors, REST API tools, file tools, and custom instruction assistants you can attach directly inside Chat.

![Tools & MCP](../screenshots/004-Personas.png)

---

## Getting Started

1. Navigate to **Tools & MCP** from the sidebar.
2. Pick a 1-click quick-start preset (**Local Filesystem MCP**, **Git / Repo MCP**, **Web Search & Grounding**) or click **Add MCP / Connector**.
3. Once created, select your connector from the **Connector** dropdown in Chat.

## Connector Types

Vesper focuses on lightweight, local-first connectors and assistants:

| Type | What it does |
|------|-------------|
| **MCP Server** | Connects to stdio or SSE Model Context Protocol servers for external tools |
| **Web Researcher** | Searches the web, fetches URLs, and extracts information |
| **API Connector** | Connects to REST APIs, GraphQL endpoints, and webhooks |
| **File Operations** | Reads, writes, and manages files in an allowed directory |
| **MongoDB** | Connects to MongoDB NoSQL databases |
| **Custom Assistant** | Custom instructions, expertise, and behavior prompts |

## Creating a Persona

The creation wizard has 2 steps:

![Create Persona](../screenshots/005-CreatePersona.png)

### Step 1: Choose a Type

- Browse the type grid — each card shows an icon, name, and description.
- Use the **search box** to filter types by name.
- Click a type card to select it and move to Step 2.

### Step 2: Configure Details

Fill in the persona details:

- **Name** (required) — Give your persona a recognizable name (e.g., "Sales DB Analyst").
- **Category** — Choose from General, Technical, Creative, Business, or Custom.
- **Description** — A short summary of what this persona does.
- **Credentials** — Type-specific fields appear based on the type you selected:
  - Database types: host, port, database name, username, password
  - API Connector: base URL, API key
  - MCP Server: server URL, transport type
  - Web Researcher: max results setting
- **System Prompt** — Custom instructions that define how the AI behaves when using this persona.

Click **Create** to save.

### Test Connection

For integration types (MongoDB, MCP Server, API Connector), a **Test Connection** button lets you verify credentials before saving.

## Managing Connectors

### Editing

Hover over a connector card and click the **pencil icon** to edit. The edit form opens directly on Step 2 with all fields pre-populated.

### Deleting

Hover over a connector card and click the **trash icon**. A confirmation dialog appears — click **Delete** to confirm.

### Searching and Filtering

- **Search** — Use the search box to filter connectors by name or description.
- **Category filter** — Click a category button (All, General, Technical, Creative, Business, Custom) to filter by category.
- Both filters work together.

## Using Connectors in Chat

1. Open the **Chat** page.
2. Click the **Connector** dropdown in the input area.
3. Select a connector — Vesper will attach its tools and system prompt to the conversation.
4. Select **"None (default)"** to return to standard chat behavior.

## Tips

- **Start with an MCP preset** (**Local Filesystem MCP** or **Git / Repo MCP**) to give Vesper tool access to your files or repo cleanly.
- **Keep system prompts specific** — the more detailed your instructions, the more consistent the assistant's behavior.
- **Test connections before chatting** — it's frustrating to discover bad credentials mid-conversation.
- **Create category-specific connectors** to quickly switch between different work contexts.
