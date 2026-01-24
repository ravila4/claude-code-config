---
name: daily-journal
description: Draft, organize, or update development journal entries. Use when user requests daily journal generation, work review, standup preparation, or asks "what did I work on today/this week?"
argumentHint: "[draft|organize|append|review]"
userInvocable: true
---

# Daily Journal

## Table of Contents

- [User Invocation](#user-invocation)
- [Subcommands](#subcommands)
  - [draft](#daily-journal-draft)
  - [organize](#daily-journal-organize)
  - [append](#daily-journal-append-section)
  - [review](#daily-journal-review)
- [Integration](#integration)
- [Overview](#overview)
- [When to Use This Skill](#when-to-use-this-skill)
- [Quick Start](#quick-start)
- [Batch Mode Workflow](#batch-mode-workflow-traditional)
- [Scripts](#scripts)
  - [generate_daily_log.py](#generate_daily_logpy)
  - [extract_user_journey.py](#extract_user_journeypy)
  - [extract_thinking.py](#extract_thinkingpy)
  - [conversation_flow.py](#conversation_flowpy)
  - [draft_journal_entry.py](#draft_journal_entrypy)
- [Journal Modes](#journal-modes)
- [Log Locations](#log-locations)
- [Output Format](#output-format)
- [Section Population](#section-population)
- [References](#references)
- [Example Workflows](#example-workflows)
- [Tips](#tips)

## User Invocation

When invoked via `/daily-journal`, route based on arguments:

**If no subcommand specified:**
Use AskUserQuestion to ask what the user needs:
- Draft new journal entry for today
- Organize existing raw/unstructured content
- Append content to specific section
- Review current journal and suggest improvements

**If context is unclear:**
Ask clarifying questions:
- Which date? (if not today)
- Which section to append to? (if appending)
- Full or minimal journal? (if drafting)
- What content should be included? (if appending)

## Subcommands

### `/daily-journal draft`

Generate complete journal entry from today's activity.

**Actions:**
1. Run `draft_journal_entry.py --mode auto`
2. Show the complete markdown draft
3. Ask if user wants to write it to Obsidian vault

**Best for:** End of day journal generation

### `/daily-journal organize`

Organize raw/unstructured content in today's journal.

**Actions:**
1. Read today's journal from `~/Documents/Obsidian-Notes/Daily Log/YYYY-MM-DD.md`
2. Detect if it's unstructured (no headers, mostly code blocks)
3. Extract commands, outputs, and notes
4. Organize into structured sections
5. Show organized version for approval
6. Update the file if approved

**Best for:** When raw commands/notes need structure

### `/daily-journal append [section]`

Add content to a specific section of today's journal.

**Actions:**
1. Extract relevant content from current conversation
2. Format it for the requested section
3. Show what will be appended
4. Update the journal file if approved

**Section options:** context, commands, reflection, questions, commits

**Best for:** Incremental journaling throughout the day

### `/daily-journal review`

Show current state of today's journal with improvement suggestions.

**Actions:**
1. Read today's journal
2. Analyze completeness (missing sections, empty placeholders)
3. Suggest improvements based on today's conversations
4. Ask if user wants to fill gaps

**Best for:** Quick check before ending the day

## Integration

This skill integrates with:
- **obsidian-vault skill**: For reading/writing journal files
- **Current conversation**: For extracting relevant content to append

---

## Overview

Generate comprehensive daily journal entries from Claude Code conversation logs. Analyzes debug logs and JSONL conversation files to create structured markdown summaries showing what was accomplished, which sessions were active, and what git changes were made.

## When to Use This Skill

Use this skill when:

- **End of day reflection**: Generate journal entry summarizing the day's work
- **Before standups**: Quick summary of yesterday's accomplishments
- **Weekly reviews**: Batch generate entries for the past week
- **Documentation**: Create records of development sessions for future reference
- **User asks**: "What did I work on today?" or "Generate my daily journal"

## Quick Start

Generate today's journal:

```bash
cd /path/to/skills/daily-journal
uv run scripts/generate_daily_log.py
```

Generate for specific date:

```bash
uv run scripts/generate_daily_log.py --date 2025-11-12
```

Save to file:

```bash
uv run scripts/generate_daily_log.py --output ~/journal-2025-11-12.md
```

## Batch Mode Workflow (Traditional)

For comprehensive session analysis:

**Step 1:** Run `generate_daily_log.py` - Gets session summary with classification (ACTIVE/BLOCKED/MINIMAL)

**Step 2:** For ACTIVE sessions, run analysis scripts:

- `extract_user_journey.py` - What was requested
- `extract_thinking.py` - Internal reasoning and tools
- `conversation_flow.py` - Tagged narrative

**Step 3:** Compile findings into journal entry manually

## Scripts

### `generate_daily_log.py`

**Purpose:** Main orchestration script for daily journal generation.

**Parameters:**

- `--date YYYY-MM-DD` - Date to analyze (default: today)
- `--output FILE` - Save report to file (default: stdout)
- `--repo PATH` - Git repository path for commit extraction (default: current directory)

**What it does:**

- Finds debug and JSONL logs for specified date
- Classifies sessions by activity level (ACTIVE, BLOCKED, MINIMAL)
- Extracts git commits from repository
- Generates initial markdown report with session counts and git activity
- Provides commands for deep analysis of ACTIVE sessions

**Output:** Markdown report with:

- Session summary (counts by type)
- Git activity (commits with stats)
- Commands for running detailed analysis scripts on ACTIVE sessions

### `extract_user_journey.py`

**Purpose:** Extract user requests and goals from a conversation.

**Parameters:**

- `conversation_file` - Path to JSONL file (required, positional)

**What it does:**

- Finds all user messages in chronological order
- Extracts request text from each message
- Shows what was asked for and when
- Useful for understanding session objectives

**Output:** Chronological list of user requests with timestamps

### `extract_thinking.py`

**Purpose:** Extract Claude's thinking blocks and tool usage.

**Parameters:**

- `conversation_file` - Path to JSONL file (required, positional)

**What it does:**

- Extracts thinking blocks showing internal reasoning
- Lists tools used (Read, Edit, Write, Bash, Task, etc.)
- Shows tool frequency and patterns
- Reveals problem-solving approach

**Output:**

- Thinking blocks with context
- Tool usage summary (ranked by frequency)
- Timeline of reasoning steps

### `conversation_flow.py`

**Purpose:** Create tagged narrative of conversation with action labels.

**Parameters:**

- `conversation_file` - Path to JSONL file (required, positional)

**What it does:**

- Generates flow with action tags (PLANNING, EXECUTING, DEBUGGING, REFLECTING, etc.)
- Analyzes conversation rhythm and pace
- Highlights key decision points
- Tags messages by activity type

**Output:**

- Tagged conversation narrative
- Flow metrics (time per phase, transitions)
- Key decision points highlighted

### `draft_journal_entry.py`

**Purpose:** Generate draft journal entry from today's activity with flexible sections.

**Parameters:**

- `--date YYYY-MM-DD` - Date to analyze (default: today)
- `--mode {full|quick|auto}` - Journal mode (default: auto)
  - **full**: All sections including placeholders for reflection
  - **quick**: Minimal sections (goals, commits, files)
  - **auto**: Adaptive - only sections with content
- `--project PATH` - Git repository path (default: current directory)
- `--output FILE` - Save draft to file (default: stdout)

**What it does:**

- Extracts todos from TodoWrite tool uses
- Captures context from initial user messages
- Lists bash commands run (filtered for significance)
- Shows files modified (Edit/Write operations)
- Identifies open questions and uncertainties
- Extracts git commits for the day
- Detects project focus and generates tags
- Populates only relevant sections (auto mode)

**Output:** Complete markdown journal entry ready for review with:

- YAML frontmatter (date, tags)
- Summary (one-line focus)
- Goals section with todo checkboxes
- Notes with project/task subsections (commits, files, commands)
- Reflection with structured bullets
- Related section with project wikilinks

**Use when:** User requests journal draft, at end of conversation, or when organizing raw content.

## Journal Modes

Three approaches to journaling:

- **Batch Mode** - End-of-day comprehensive review using log analysis scripts
- **Draft Mode** - Quick journal generation with `draft_journal_entry.py`
- **Incremental Mode** - Build journal progressively throughout the day

See `references/modes_and_workflows.md` for detailed workflows and integration with Obsidian vault manager.

## Log Locations

Claude Code stores logs in two locations:

- **Debug logs**: `~/.claude/debug/*.txt` - System-level logs with tool execution
- **JSONL logs**: `~/.claude/projects/*/*.jsonl` - Full conversation history with messages, thinking, and tool use

Both are searched by date using `find` with `-newermt` flags.

## Output Format

Journal entries use the Daily Log template structure:

```
---
date: YYYY-MM-DD
tags: [daily-log, ...]
---

## Summary
*One-line: What was today's main focus?*

## Goals
- [ ] Task 1
- [ ] Task 2

## Notes
*What happened today. Use subsections for different topics/projects.*

### Project/Task Name
*Technical details, commits, commands, investigation work.*

## Reflection
- **What worked:**
- **What didn't:**
- **Open questions:**
- **Tomorrow's focus:**

## Related
- [[Project Name]]
```

Designed for Obsidian vault storage with cross-references and tags.

## Section Population

When generating journal drafts, populate sections based on available content:

- **Always include:** YAML frontmatter, Summary, Goals, Notes, Reflection, Related
- **Goals section:** Populated with todos from conversation, or placeholder tasks if none
- **Notes section:** Project/task subsections containing commits, files, commands
- **Reflection section:** Structured bullets with open questions if any exist

See `references/section_guide.md` for complete population logic and decision criteria for auto/full/quick modes.

## References

See `references/` for detailed information:

- **log-formats.md** - JSONL structure and message types
- **session-patterns.md** - Common conversation patterns
- **high-signal-patterns.md** - What indicates important sessions
- **limitations-caveats.md** - Known issues and workarounds
- **modes_and_workflows.md** - Detailed workflow explanations and Obsidian integration
- **section_guide.md** - Complete section population logic for journal drafts
- **workflow_examples.md** - Step-by-step scenario walkthroughs

## Example Workflows

See `references/workflow_examples.md` for detailed scenarios:

- Scenario 1: End of deep work day with draft generation
- Scenario 2: Organizing raw commands into structured journal
- Scenario 3: Incremental journaling throughout the day

## Tips

**For better journals:**

- Use `/daily-journal draft` at end of day for quick generation
- Use `--mode full` for deep work days needing reflection
- Use `--mode auto` (default) for adaptive structure
- Let Claude organize raw content - don't force manual structure

**For different work styles:**

- **Batch mode**: End of day, run draft script, review, write
- **Incremental mode**: Use `/daily-journal append` throughout day
- **Hybrid mode**: Dump raw content, organize at end with `/daily-journal organize`

**For retrospective analysis:**

- Use total-recall to search past Claude conversation logs by topic
- Generate multiple days: `for d in 11 12 13; do draft_journal_entry.py --date 2025-11-$d; done`
- Compare structured vs raw days to refine your workflow
