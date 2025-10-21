---
description: "Ask Codex for code improvements or best practices"
argumentHint: "[question] (mention files for context)"
---

Consulting Codex: $ARGUMENTS

I'll use the codex-consultant agent to get Codex's suggestions.

The agent will:
- Check for cached responses (< 24h old)
- Build query with file references (using @ syntax for large files)
- Call Codex CLI
- Cache the response in `.memories/external-llm-cache/codex/`
- Return a concise summary with code examples

{Launching codex-consultant agent via Task tool}
