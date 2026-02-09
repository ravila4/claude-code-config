---
name: session-recall
description: Search and retrieve past Claude Code conversations using the `sr` CLI tool. This skill should be used when the user asks about previous sessions, wants to find past discussions, needs to recall how something was implemented, or references work done in earlier conversations. Also use when context from past sessions would help the current task.
---

# Session Recall

Search past Claude Code sessions using full-text keyword search or semantic vector search.

The `sr` CLI is installed via `uv tool install -e` and available on PATH.

## When to Use

- User asks "how did we do X last time?" or "what was that command we used?"
- User references a past conversation or decision
- Finding prior implementations, debugging approaches, or architectural decisions
- Searching for when/where a topic was discussed across projects

## Search Modes

### FTS (keyword) -- default, fast, no model needed

```bash
sr search "docker installation" --mode fts -n 5
```

FTS uses SQLite FTS5 with BM25 ranking. Good for exact terms, function names, error messages, and specific keywords.

**Flat results** (default): returns individual message hits ranked by relevance.

**Grouped results** (`-g`): groups hits by session, shows best hit per session with optional context:

```bash
sr search "pytest fixtures" --mode fts -n 10 -g -c 2 --sessions 3
```

- `-g` groups by session
- `-c 2` shows 2 messages of context around each hit
- `--sessions 3` limits to top 3 sessions

### Semantic -- requires Ollama running

```bash
sr search "how to handle authentication" --mode semantic -n 5
```

Semantic search embeds the query and finds similar conversation windows via vector similarity. Good for conceptual queries, paraphrased ideas, and finding discussions about a topic even when exact words differ.

Semantic results are always grouped by session. Use `-c` for context:

```bash
sr search "error handling patterns" --mode semantic -c 3
```

## Filtering

Filter by project path substring with `-p`:

```bash
sr search "migration" --mode fts -p session-log
sr search "pipeline design" --mode semantic -p aou_qc
```

## Other Commands

List sessions:
```bash
sr sessions
sr sessions -p session-log    # filter by project
```

View a full conversation (accepts ID prefix):
```bash
sr show 313cfa44
```

Search plan content:
```bash
sr plans-search "embedding architecture"
```

Show plans for a session:
```bash
sr plans 313cfa44
```

Index stats:
```bash
sr status
```

## Choosing a Mode

| Need | Mode |
|------|------|
| Exact term, function name, error text | `fts` |
| Conceptual question, paraphrased idea | `semantic` |
| Quick lookup, Ollama not running | `fts` |
| "Find discussions about X" | `semantic` |

## Tips

- Start with FTS for specific terms -- it's instant and needs no model.
- Use semantic when FTS misses because the exact words weren't used.
- The `-c` context flag is valuable for understanding the surrounding conversation.
- Session ID prefixes work everywhere (minimum 8 chars to be unambiguous).
- Indexing runs automatically on session end. Embedding runs hourly via launchd.
