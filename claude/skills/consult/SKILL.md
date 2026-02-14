---
name: consult
description: Consult external LLMs (Gemini, GPT, Claude variants) for second opinions, debugging, or alternative perspectives. Use when user asks to "consult", "ask", or wants external LLM opinions on code, architecture, or debugging problems.
argumentHint: "<model-or-provider> [question]"
userInvocable: true
---

# Consulting External LLMs

## Contents
- [Usage Patterns](#usage-patterns)
- [Routing](#routing)
- [Workflow](#workflow)
- [Reference](#reference)

## Usage Patterns

**User-invoked:**
```
/consult gemini "Why is this DataFrame returning NaN?"
/consult codex "How can I improve this function?"
/consult gpt-5.2 "Review this architecture"
```

**Natural language (Claude interprets):**
- "Consult gemini on this plan" → cursor-agent with gemini-3-pro
- "Consult codex on this function" → codex exec
- "Ask gemini and codex" → parallel Task calls

For multiple consultants, launch parallel Task calls with this skill.

## Routing

| CLI | Command | Use For |
|-----|---------|---------|
| cursor-agent | `cursor-agent --model {model} --print --output-format text "{query}"` | Default, widest selection |
| codex | `codex exec -m {model} "{query}"` | Codex-specific models |
| claude | `claude -m {model} -p "{query}"` | Claude models directly |
| opencode | `opencode run -m {model} "{query}"` | OpenCode models |

**Routing table:**

| Request | Routes To | Model |
|---------|-----------|-------|
| gemini | cursor-agent | gemini-3-pro |
| gpt-5.2 | cursor-agent | gpt-5.2 |
| gpt-5.3 | cursor-agent | gpt-5.3-codex |
| opus | cursor-agent | opus-4.6-thinking |
| codex | codex exec | gpt-5.1-codex |
| claude | claude | sonnet |
| opencode | opencode | (run `opencode models`) |

Run `cursor-agent models` or `opencode models` for full lists.

## Workflow

### 1. Parse Request
From `$ARGUMENTS` or natural language:
- Extract model/provider name
- Remaining text is the question
- Identify file paths mentioned

### 2. Build Query
```
Role: {inferred: debugger, architect, reviewer, etc.}

Question: {user question}

Files for context:
@/absolute/path/to/file.py

Context summary: {< 200 words}
```

### 3. Call CLI
Route per table above. Use @ file references for files > 100 lines.

### 4. Return Result
If response > 500 lines, summarize key points.

Return structured response:
```json
{
  "model": "gemini-3-pro",
  "cli": "cursor-agent",
  "insights": [
    "Key insight 1",
    "Key insight 2"
  ],
  "recommendations": [
    "Action 1",
    "Action 2"
  ],
  "code_examples": "```python\n# if applicable\n```",
  "raw_response_truncated": false
}
```

Then present a human-readable summary. Note when response differs from Claude's analysis.

## Reference

See [references/consultants.md](references/consultants.md) for model selection guidance.
