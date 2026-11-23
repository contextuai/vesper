# Contributing to Vesper

Thank you for your interest in contributing to Vesper! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork** the repository on GitHub (`contextuai/vesper`)
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/vesper.git
   cd vesper
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feat/your-feature-name
   ```
4. **Make your changes** and test them thoroughly
5. **Commit** with a clear, descriptive message:
   ```bash
   git commit -m "feat: add new MCP connector preset"
   ```
6. **Push** to your fork and **open a Pull Request** targeting `main`

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation changes
- `style:` — Formatting, no code change
- `refactor:` — Code restructuring without feature change
- `test:` — Adding or updating tests
- `chore:` — Build, tooling, or dependency updates

## Code Style

### TypeScript (Frontend)

- **Strict mode** is enabled — no `any` types without justification
- Use functional components with hooks
- Use the `cn()` utility for conditional Tailwind classes
- Import paths use the `@/*` alias (maps to `src/*`)
- Format cleanly to match surrounding files

### Python (Backend)

- **Type hints** on all function signatures and return types
- Use **Pydantic v2** for request/response models
- All I/O should be async where integrated into FastAPI routes
- Follow PEP 8 naming conventions
- Docstrings on public functions and classes

## Testing

### Frontend

```bash
cd frontend
npx tsc --noEmit    # Type check
npm run build       # Production Vite bundle
npx playwright test # E2E tests (requires backend on 18741 & Vite on 1420)
```

### Backend

```bash
cd backend
CONTEXTUAI_MODE=desktop pytest tests/ -v
```

All pull requests must pass existing backend and frontend checks cleanly.

## What to Contribute

- **MCP & Tool Connectors** — Improve local tool integrations and MCP presets
- **Local AI & RAG Improvements** — Retrieval quality, quantization support, hardware fit tuning
- **Privacy & Security Hardening** — Local DLP patterns, audit/ABOM reporting, egress controls
- **Bug Fixes & UI Polish** — Accessibility, keyboard navigation, responsive layout
- **Documentation** — Keep guides, examples, and API references up to date

## Reporting Issues

When reporting a bug, please include:

- Your OS and architecture
- App version (**Settings → About**)
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Screenshots or error logs if applicable

## Code of Conduct

Be respectful, constructive, and inclusive. Treat every contributor the way you would want to be treated.

## Questions?

Open a GitHub Discussion or Issue on [contextuai/vesper](https://github.com/contextuai/vesper).

---

Thank you for helping make Vesper better for everyone!
