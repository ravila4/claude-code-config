---
description: "Get multi-perspective review from internal agents + external LLMs"
argumentHint: "[file(s) or component to review]"
---

# Multi-Agent Review: $ARGUMENTS

Launching multi-perspective-reviewer agent for comprehensive review...

The agent will coordinate:

**Internal Reviewers:**
- python-code-reviewer (code quality, style, maintainability)
- architecture-devils-advocate (design critique, alternatives)

**External Perspectives:**
- Gemini (Google's perspective)
- GPT-5 (OpenAI's perspective via Cursor)
- Codex (code improvements and best practices)

The agent will synthesize all perspectives and identify:
- **Consensus issues** (all/most reviewers agree)
- **Divergent opinions** (interesting conflicts to explore)
- **Prioritized actions** (ordered by impact)

{Launching multi-perspective-reviewer agent via Task tool}

---

Detailed reviews will be cached in:
- `.memories/reviews/YYYY-MM-DD-multi-perspective-{topic}.json`
- `.memories/external-llm-cache/{gemini,gpt5,codex}/...`
