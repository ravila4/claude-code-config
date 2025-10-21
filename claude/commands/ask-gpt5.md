---
description: "Ask GPT-5 (via Cursor) for second opinion or alternative approach"
argumentHint: "[question] (mention files for context)"
---

Consulting GPT-5: $ARGUMENTS

I'll use the gpt5-consultant agent to get GPT-5's perspective via Cursor AI.

The agent will:
- Check for cached responses (< 24h old)
- Build query with file references (using @ syntax for large files)
- Call cursor-agent CLI
- Cache the response in `.memories/external-llm-cache/gpt5/`
- Return a concise summary

{Launching gpt5-consultant agent via Task tool}
