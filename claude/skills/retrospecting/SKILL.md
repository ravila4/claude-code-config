---
name: retrospecting
description: Use when user asks to find past conversations, wants to know "what did we decide about X?", requests file modification history, or asks about previous work on a topic. Searches ~/.claude/projects JSONL logs by keyword, date, file path, and extracts design decisions from AskUserQuestion interactions.
---

# Retrospecting

## Overview

Search and analyze Claude Code conversation logs to find past decisions, extract implementation details, and review previous work. Handles keyword search, file-based search, and conversation summarization from `~/.claude/projects/*/*.jsonl` log files.

## When to Use This Skill

Use this skill when the user asks:
- **"Find conversations about X"** - Keyword search across all conversations
- **"What did we decide about Y?"** - Extract design decisions and clarifying questions
- **"Show conversations that touched file Z"** - Find conversations by file path
- **"Summarize that conversation"** - Deep dive into a specific session
- **"What work did I do on [topic/date]?"** - Time-based conversation review
- **"What questions did you ask about X?"** - Review clarifying questions answered

## Quick Start

**Search by keyword:**
```bash
cd skills/retrospecting
uv run scripts/search_conversations.py --keyword "plink manifest"
```

**Search with date filter:**
```bash
uv run scripts/search_conversations.py --keyword "refactor" --since 2025-11-01
```

**Search by file:**
```bash
uv run scripts/search_conversations.py --file "plink_merger.py"
```

**Summarize a conversation:**
```bash
uv run scripts/summarize_conversation.py /path/to/conversation.jsonl
```

## Core Workflows

### 1. Finding Conversations by Keyword

**Use case:** User wants to find past conversations about a specific topic.

**Example:** "Find conversations about manifest checkpoints"

**Command:**
```bash
uv run scripts/search_conversations.py --keyword "manifest checkpoint" --limit 5
```

**What it does:**
- Searches all JSONL files in `~/.claude/projects/`
- Scores relevance based on keyword frequency
- Ranks results by score (highest first)
- Shows preview of first user message, files touched, and top matches

**Output:** Markdown with ranked conversation list, including:
- File paths to conversations
- Relevance scores
- Message counts
- Files touched during conversation
- Previews of matching content

### 2. Finding Conversations by File

**Use case:** User wants to see conversations that modified a specific file.

**Example:** "Show conversations about plink_merger.py"

**Command:**
```bash
uv run scripts/search_conversations.py --file "plink_merger.py"
```

**What it does:**
- Extracts file paths from tool use blocks (Read, Edit, Write, Glob)
- Filters conversations that touched matching files
- Can combine with keyword search: `--keyword "refactor" --file "merger.py"`

**File matching:** Substring match (case-insensitive) on file paths.

### 3. Time-Based Search

**Use case:** User wants conversations from a specific time period.

**Example:** "What did I work on this week?"

**Command:**
```bash
uv run scripts/search_conversations.py --since 2025-11-05 --until 2025-11-12
```

**What it does:**
- Filters conversations by file modification time
- Dates are inclusive
- Can combine with keywords: `--keyword "bug fix" --since 2025-11-01`

**Date format:** YYYY-MM-DD

### 4. Summarizing a Conversation

**Use case:** User found a conversation and wants detailed summary.

**Example:** "Summarize that conversation about logging improvements"

**Steps:**
1. First, search to find the conversation:
   ```bash
   uv run scripts/search_conversations.py --keyword "logging improvements"
   ```

2. Then summarize the specific file:
   ```bash
   uv run scripts/summarize_conversation.py /path/from/search/results.jsonl
   ```

**What it does:**
- Extracts user journey (what was requested)
- Shows tool usage statistics (Read, Edit, Write, Task, etc.)
- Lists files touched during conversation
- Displays key exchanges with previews
- Reports any parsing errors encountered

**Output formats:**
- **Standard:** Basic markdown summary
- **Obsidian:** `--format obsidian` adds YAML frontmatter and wikilinks

### 5. Combined Search

**Use case:** Narrow down with multiple filters.

**Example:** "Find recent conversations about authentication that touched config files"

**Command:**
```bash
uv run scripts/search_conversations.py \
  --keyword "authentication" \
  --file "config" \
  --since 2025-11-01 \
  --limit 10
```

**Power tip:** Start broad, then narrow:
1. Search by keyword to see volume
2. Add file filter to narrow to specific area
3. Add date filter for recent work only

### 6. Extracting Design Decisions

**Use case:** User wants to review past architectural or implementation decisions.

**Example:** "What decisions did I make about error handling?"

**Command:**
```bash
uv run scripts/extract_decisions.py --search-all --topic "error" --since 2025-11-01
```

**What it does:**
- Finds all AskUserQuestion interactions
- Extracts questions and user's answers
- Filters by topic keyword
- Shows decision context and timestamps

**Single conversation:**
```bash
uv run scripts/extract_decisions.py /path/to/conversation.jsonl
```

### 7. File Modification History

**Use case:** Track when and how a specific file was modified.

**Example:** "Show me all changes to plink_merger.py"

**Command:**
```bash
uv run scripts/find_by_file.py "plink_merger.py" --since 2025-11-01
```

**What it does:**
- Finds conversations that touched the file
- Shows Read, Edit, Write operations
- Displays edit previews (old → new)
- Timeline of modifications with context

**With glob patterns:**
```bash
uv run scripts/find_by_file.py "scripts/**/*.py" --glob
```

### 8. Quick Browsing

**Use case:** Get overview of recent conversations before deep analysis.

**Example:** "What work did I do on plink_processing this week?"

**Command:**
```bash
uv run scripts/list_conversations.py --project plink_processing --since 2025-11-05
```

**What it does:**
- Lists conversations with metadata
- Shows message counts and file sizes
- Previews first user request
- Helps identify conversations for detailed analysis

**Compact view:**
```bash
uv run scripts/list_conversations.py --compact --limit 20
```

## Log Structure (Non-Obvious Details)

### Where Logs Live

Claude Code stores conversation logs in:
- **Primary location:** `~/.claude/projects/*/*.jsonl`
- **Debug logs:** `~/.claude/debug/*.txt` (not searched by these scripts)

### JSONL Format

Each line is a JSON object representing a message or event:

```json
{"type": "user", "message": {"role": "user", "content": "..."}}
{"type": "assistant", "message": {"role": "assistant", "content": [...]}}
{"type": "tool_result", ...}
```

**Message content structures:**
- **String:** Simple text message
- **List of objects:** Can contain text blocks, thinking blocks, and tool_use blocks

**Content block types:**
- `type: "text"` - Regular message text
- `type: "thinking"` - Internal reasoning (not counted in keyword search currently)
- `type: "tool_use"` - Tool invocations (Read, Edit, Write, etc.)

### File Path Extraction

File paths are extracted from tool_use blocks:
- **Read, Edit, Write:** `input.file_path`
- **NotebookEdit:** `input.notebook_path`
- **Glob:** `input.path` (if provided)
- **Bash:** Not parsed (command strings not analyzed for file refs)

## Scripts

### `search_conversations.py`

**Purpose:** Main search interface for finding conversations.

**Parameters:**
- `--keyword WORDS` - Space-separated keywords to search for
- `--file SUBSTRING` - Filter by file path substring
- `--since YYYY-MM-DD` - Start date (inclusive)
- `--until YYYY-MM-DD` - End date (inclusive)
- `--limit N` - Max results to show (default: 10)
- `--log-dir PATH` - Override log directory (default: ~/.claude/projects)

**Relevance scoring:**
- 10 points per keyword occurrence
- 5 point bonus for exact word match (not substring)
- Results sorted by total score (descending)

**Error handling:**
- Skips malformed JSON lines with warnings
- Continues on file read errors
- Returns empty results if no matches (not an error)

### `summarize_conversation.py`

**Purpose:** Generate detailed summary of a single conversation.

**Parameters:**
- `conversation` - Path to JSONL file (required, positional)
- `--format {standard|obsidian}` - Output format (default: standard)

**Extracted information:**
- User message count and content
- Assistant response count
- Thinking block count
- Tool usage statistics (by tool name)
- Files touched (from tool use blocks)
- Key exchanges with previews
- Any parsing errors encountered

**Output sections:**
- Overview (counts)
- User Journey (chronological requests)
- Files Touched (sorted list)
- Tool Usage (ranked by frequency)
- Key Exchanges (first 5 with previews)
- Errors Encountered (if any)

### `extract_decisions.py`

**Purpose:** Extract design decisions and clarifying questions (AskUserQuestion interactions).

**Parameters:**
- `conversation` - Path to JSONL file (single conversation mode)
- `--search-all` - Search all conversations in log directory
- `--topic KEYWORD` - Filter decisions by topic keyword
- `--since YYYY-MM-DD` - Start date
- `--until YYYY-MM-DD` - End date
- `--log-dir PATH` - Override log directory

**What it extracts:**
- Questions asked via AskUserQuestion tool
- User's answers to each question
- Context around decision points
- Timestamp of each decision

**Use case:** "What did we decide about authentication approach?" or "Show all architecture decisions from last month"

### `find_by_file.py`

**Purpose:** Find conversations that touched specific files with detailed operation history.

**Parameters:**
- `file_pattern` - File path or pattern (required, positional)
- `--glob` - Use glob pattern matching (e.g., `**/*.py`)
- `--since YYYY-MM-DD` - Start date
- `--until YYYY-MM-DD` - End date
- `--log-dir PATH` - Override log directory

**What it shows:**
- Which conversations modified the file
- What operations were performed (Read, Edit, Write)
- Context around each operation
- Timeline of file modifications
- Edit previews (old → new string)

**Use case:** "Show all conversations that modified plink_merger.py" or "When did we last change the config files?"

### `list_conversations.py`

**Purpose:** Quick browsing of all conversations with metadata.

**Parameters:**
- `--since YYYY-MM-DD` - Start date
- `--until YYYY-MM-DD` - End date
- `--project SUBSTRING` - Filter by project name
- `--limit N` - Limit number of results
- `--compact` - Show compact table format
- `--show-paths` - Include full file paths
- `--log-dir PATH` - Override log directory

**What it shows:**
- Conversation timestamp
- Message counts (user/assistant)
- Tool usage count
- First user request
- File size

**Use case:** "What conversations happened this week?" or "Browse recent plink_merger work"

## Tips for Effective Search

### Start Broad, Then Narrow

1. **Initial search:** Use general keywords to gauge volume
   ```bash
   uv run scripts/search_conversations.py --keyword "pipeline"
   ```

2. **Refine:** Add more specific terms or filters
   ```bash
   uv run scripts/search_conversations.py --keyword "pipeline error" --since 2025-11-01
   ```

3. **Pinpoint:** Add file filter for exact context
   ```bash
   uv run scripts/search_conversations.py --keyword "pipeline error" --file "plink_merger"
   ```

### Keyword Selection

**Effective keywords:**
- Technology names: "plink", "pytest", "docker"
- File names (without extension): "merger", "manifest"
- Problem types: "error", "bug", "refactor"
- Features: "validation", "checkpoint", "logging"

**Less effective:**
- Generic words: "the", "implement", "fix" (too common)
- Very long phrases (search is word-based, not phrase-based)

### Date Ranges

- **Recent work:** `--since 2025-11-01` (open-ended, all conversations since)
- **Specific week:** `--since 2025-11-05 --until 2025-11-12`
- **Single day:** `--since 2025-11-12 --until 2025-11-12`

### Combining with File Search

**Find conversations about topic X that touched file Y:**
```bash
uv run scripts/search_conversations.py --keyword "authentication" --file "config.py"
```

This is powerful for tracking "how did we change X when working on Y?"

## Obsidian Integration

When summarizing with `--format obsidian`:

```bash
uv run scripts/summarize_conversation.py conversation.jsonl --format obsidian > ~/Obsidian-Notes/Conversations/summary.md
```

**Differences:**
- YAML frontmatter with date, type, and tags
- Files shown as wikilinks: `[[file/path.py]]`
- Ready to drop into Obsidian vault

## References

See `references/` for detailed documentation:
- **log-structure.md** - Complete JSONL format specification
- **search-strategies.md** - Relevance scoring algorithms and optimization
- **output-templates.md** - Markdown format templates

## Limitations

**Current limitations:**
- Keyword search is substring-based, not semantic (no NLP)
- Thinking blocks not included in keyword search (only text/user/assistant content)
- Bash commands not parsed for file references
- No fuzzy matching (exact substring only)
- File modification time used (not conversation start time)

**Workarounds:**
- Use multiple keywords with OR semantics (space-separated)
- Check conversation summaries for thinking details
- Manually grep for specific command patterns if needed
- Try alternate spellings/terms if no results

## Future Enhancements

Potential additions (not yet implemented):
- Find conversations by agent type (Task tool with specific subagent)
- Semantic search (similarity-based, not keyword)
- Timeline view (visualize conversation activity over time)
- Git integration (link conversations to commits)
- Fuzzy keyword matching (typo tolerance)
- Result caching/indexing for faster searches
- Export to JSON/CSV formats
