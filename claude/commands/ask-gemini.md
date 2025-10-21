---
description: "Ask Gemini for second opinion or specialized knowledge"
argumentHint: "[question] (mention files for context)"
---

Consulting Gemini on: $ARGUMENTS

I'll use the gemini-consultant agent to get Gemini's perspective.

The agent will:
- Check for cached responses (< 24h old)
- Build query with file references (using @ syntax for large files)
- Call Gemini CLI
- Cache the response in `.memories/external-llm-cache/gemini/`
- Return a concise summary

{Launching gemini-consultant agent via Task tool}
