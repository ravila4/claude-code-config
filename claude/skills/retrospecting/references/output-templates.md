# Output Templates Reference

## Contents

- [Search Results Template](#search-results-template)
- [{rank}. {conversation_name}](#rank-conversation_name)
- [1. agent-32ee39cc](#1-agent-32ee39cc)
- [2. 387d92e8-cae5-42de-9927-801fd3f496ad](#2-387d92e8-cae5-42de-9927-801fd3f496ad)
- [Conversation Summary Template](#conversation-summary-template)
- [Overview](#overview)
- [User Journey](#user-journey)
- [Files Touched](#files-touched)
- [Tool Usage](#tool-usage)
- [Key Exchanges](#key-exchanges)
- [Errors Encountered](#errors-encountered)
- [Overview](#overview)
- [User Journey](#user-journey)
- [Tool Usage](#tool-usage)
- [Key Exchanges](#key-exchanges)
- [Detailed Implementation Plan](#detailed-implementation-plan)
- [Obsidian Format](#obsidian-format)
- [Files Touched](#files-touched)
- [Overview](#overview)
- [User Journey](#user-journey)
- [Files Touched](#files-touched)
- [Tool Usage](#tool-usage)
- [Empty Results Template](#empty-results-template)
- [Preview Truncation Rules](#preview-truncation-rules)
- [Implementation Plan](#implementation-plan)
- [File List Formatting](#file-list-formatting)
- [Match Highlighting (Future Enhancement)](#match-highlighting-future-enhancement)
- [Timestamp Formatting](#timestamp-formatting)
- [Sorting Rules](#sorting-rules)
- [Error Display](#error-display)
- [Errors Encountered](#errors-encountered)
- [Compact vs. Verbose Modes (Future)](#compact-vs-verbose-modes-future)
- [JSON Output (Future)](#json-output-future)
- [CSV Output (Future)](#csv-output-future)
- [Custom Templates (Future)](#custom-templates-future)
- [{file_name} (Score: {score})](#file_name-score-score)

## Search Results Template

### Standard Format

```markdown
# Search Results

Found {total_count} conversations

## {rank}. {conversation_name}
**Path:** `{file_path}`
**Score:** {relevance_score}
**Messages:** {message_count}

**First request:** {first_user_message_preview}...

**Files touched ({file_count}):**
- `{file_1}`
- `{file_2}`
- ...

**Top matches ({match_count}):**
- Line {line_num} ({message_type}, score {match_score})
  > {content_preview}...

{repeat for each result}

*Showing {limit} of {total_count} results. Use --limit to see more.*
```

### Example Output

```markdown
# Search Results

Found 93 conversations

## 1. agent-32ee39cc
**Path:** `/Users/user/.claude/projects/plink_merger/agent-32ee39cc.jsonl`
**Score:** 3920
**Messages:** 34

**First request:** Please conduct a comprehensive devils-advocate review of the plink_merger system...

**Files touched (5):**
- `/Users/user/scripts/plink_merger/plink_merger.py`
- `/Users/user/scripts/plink_merger/plink_merger_cli.py`
- `/Users/user/docs/ARCHITECTURE.md`
- `/Users/user/docs/MANIFEST_SYSTEM.md`
- `/Users/user/tests/test_plink_merger.py`

**Top matches (4):**
- Line 28 (assistant, score 1970)
  > Now let me generate the comprehensive architectural review:

    # Devil's Advocate Architecture Review: plink_merger System

    ## Executive Summary - Top 3 Critical Issues

    ### 1. **CRITICAL: GCS Validation...
- Line 31 (assistant, score 1420)
  > Let me generate and save the complete structured JSON review...
- Line 1 (user, score 330)
  > Please conduct a comprehensive devils-advocate review...

## 2. 387d92e8-cae5-42de-9927-801fd3f496ad
...

*Showing 10 of 93 results. Use --limit to see more.*
```

## Conversation Summary Template

### Standard Format

```markdown
# Conversation Summary: {file_name}

**Date:** {timestamp_formatted}
**File:** `{file_path}`

## Overview

- User messages: {user_message_count}
- Assistant responses: {assistant_response_count}
- Thinking blocks: {thinking_count}
- Tools used: {tool_use_count}
- Files touched: {file_touch_count}

## User Journey

What was requested:

{numbered_list_of_user_messages}

## Files Touched

{list_of_files_touched}

## Tool Usage

{ranked_list_of_tools_with_counts}

## Key Exchanges

### Exchange {n}

{assistant_message_preview}

*Tools: {tools_used}*
*Thinking blocks: {thinking_count}*

{repeat for top 5 exchanges}

*... and {remaining_count} more exchanges*

## Errors Encountered

{list_of_parsing_errors}
```

### Example Output

```markdown
# Conversation Summary: b3fde3c8-6427-46ee-8bf1-4cb2409a86f3

**Date:** 2025-11-13 00:43:08
**File:** `/Users/user/.claude/projects/plink_merger/b3fde3c8-6427-46ee-8bf1-4cb2409a86f3.jsonl`

## Overview

- User messages: 23
- Assistant responses: 21
- Thinking blocks: 0
- Tools used: 15
- Files touched: 0

## User Journey

What was requested:

1. [Image #1] I think we can improve the logs some more. In structured mode, I see what's in the screenshot...
2. [Request interrupted by user for tool use]
3. Let's see more details
4. hi, where were we?
5. let's continue

## Tool Usage

- **Task**: 5 times
- **AskUserQuestion**: 5 times
- **ExitPlanMode**: 5 times

## Key Exchanges

### Exchange 1

I need to understand the current logging structure to plan these improvements. Let me explore the codebase.

### Exchange 2

Now that I understand the logging structure, let me clarify a few things before presenting a plan.

*Tools: AskUserQuestion*

### Exchange 3

Perfect! Now I have all the information I need to create a plan.

*Tools: ExitPlanMode*

### Exchange 4

Let me provide more detailed implementation specifics:

## Detailed Implementation Plan

### 1. Fix GCS severity field mapping
**File:** `scripts/plink_merger/plink_merger_cli.py`
...

*... and 17 more exchanges*
```

## Obsidian Format

### Differences from Standard

1. **YAML Frontmatter:**
```markdown
---
date: 2025-11-13
type: claude-conversation
tags: [conversation, claude-code]
---
```

2. **Wikilinks for Files:**
```markdown
## Files Touched

- `[[scripts/plink_merger/plink_merger.py]]`
- `[[docs/ARCHITECTURE.md]]`
```

3. **H1 Title:**
```markdown
# Conversation: b3fde3c8-6427-46ee-8bf1-4cb2409a86f3
```

### Full Example

```markdown
---
date: 2025-11-13
type: claude-conversation
tags: [conversation, claude-code, plink-merger]
---

# Conversation: b3fde3c8-6427-46ee-8bf1-4cb2409a86f3

**Date:** 2025-11-13 00:43:08
**File:** `/Users/user/.claude/projects/plink_merger/b3fde3c8-6427-46ee-8bf1-4cb2409a86f3.jsonl`

## Overview

- User messages: 23
- Assistant responses: 21
- Thinking blocks: 0
- Tools used: 15
- Files touched: 0

## User Journey

What was requested:

1. [Image #1] I think we can improve the logs some more...
2. Let's see more details
...

## Files Touched

- `[[scripts/plink_merger/plink_merger.py]]`
- `[[docs/ARCHITECTURE.md]]`

## Tool Usage

- **Task**: 5 times
- **AskUserQuestion**: 5 times

...
```

## Empty Results Template

### No Conversations Found

```markdown
No conversations found matching the criteria.
```

**When shown:**
- No files match date range
- Keyword search yields zero matches
- File filter excludes all conversations

## Preview Truncation Rules

### Message Previews

**Length:** 200 characters max

**Truncation:**
```markdown
{first_200_chars}...
```

**Example:**
```markdown
I think we can improve the logs some more. In structured mode, I see what's in the screenshot. Here's my ideas: 1. "Downloading range 266/267" -> "Downloading range - Chunk 49: 266 out o...
```

### Content Match Previews

**Length:** 300 characters max

**Example:**
```markdown
> Now let me generate the comprehensive architectural review:

  # Devil's Advocate Architecture Review: plink_merger System

  ## Executive Summary - Top 3 Critical Issues

  ### 1. **CRITICAL: GCS Validation Gap**

  The current implementation lacks proper GCS URI valid...
```

### Key Exchange Previews

**Length:** 300 characters max, with tool/thinking annotations

**Example:**
```markdown
### Exchange 3

Perfect! Now I have all the information I need to create a plan. Let me present the implementation approach:

## Implementation Plan

### 1. Fix GCS Severity Field

We'll add the `severity` field to the structured logger output. This requires modifying the `StructuredFormatter` class in `plink_merger_cli.py...

*Tools: ExitPlanMode*
*Thinking blocks: 0*
```

## File List Formatting

### Short List (≤10 files)

Show all files:
```markdown
**Files touched (5):**
- `/path/to/file1.py`
- `/path/to/file2.py`
- `/path/to/file3.py`
- `/path/to/file4.py`
- `/path/to/file5.py`
```

### Long List (>10 files)

Show first 10, indicate more:
```markdown
**Files touched (27):**
- `/path/to/file1.py`
- `/path/to/file2.py`
...
- `/path/to/file10.py`
- *(... and 17 more)*
```

## Match Highlighting (Future Enhancement)

### Not Implemented

Current output shows plain text. Could add highlighting:

```markdown
> Now let me generate the **manifest** review for the **checkpoint** system.
```

### Implementation Ideas

1. **Markdown bold:**
   ```python
   text = re.sub(rf'\b({keyword})\b', r'**\1**', text, flags=re.IGNORECASE)
   ```

2. **ANSI colors (terminal):**
   ```python
   text = re.sub(rf'\b({keyword})\b', r'\033[1;33m\1\033[0m', text)
   ```

3. **HTML (browser):**
   ```python
   text = re.sub(rf'\b({keyword})\b', r'<mark>\1</mark>', text)
   ```

## Timestamp Formatting

### ISO 8601 Input

```json
"timestamp": "2025-11-13T00:43:08.123Z"
```

### Human-Readable Output

```python
dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
formatted = dt.strftime('%Y-%m-%d %H:%M:%S')
```

**Output:** `2025-11-13 00:43:08`

### Date Only (Obsidian Frontmatter)

**Output:** `2025-11-13`

## Sorting Rules

### Search Results

**Primary:** Relevance score (descending)
**Tie-break:** Arbitrary (file system order)

### Tool Usage

**Primary:** Frequency (descending)
**Tie-break:** Alphabetical

**Example:**
```markdown
- **Task**: 10 times
- **Read**: 8 times
- **Edit**: 5 times
- **AskUserQuestion**: 3 times
- **Write**: 2 times
```

### Files Touched

**Primary:** Alphabetical (ascending)

**Example:**
```markdown
- `/Users/user/docs/ARCHITECTURE.md`
- `/Users/user/scripts/plink_merger/plink_merger.py`
- `/Users/user/scripts/plink_merger/plink_merger_cli.py`
- `/Users/user/tests/test_plink_merger.py`
```

## Error Display

### Parsing Errors

```markdown
## Errors Encountered

- Line 42: Malformed JSON - Expecting ',' delimiter: line 1 column 234
- Line 105: Processing error - 'content' key missing from message
- Line 287: Malformed JSON - Unterminated string starting at: line 1 column 89
```

**Limit:** Show first 10 errors, indicate if more

```markdown
- Line 42: Malformed JSON...
- Line 105: Processing error...
...
- Line 287: Malformed JSON...
- *... and 5 more errors*
```

## Compact vs. Verbose Modes (Future)

### Compact (Default)

- Show preview snippets
- Limit file lists to 10
- Show top 3 matches per conversation

### Verbose (--verbose flag)

- Show full user messages
- Show all files touched
- Show all matches with full context

**Not implemented yet:** Could add flag for control.

## JSON Output (Future)

### Structured Data Export

```bash
uv run search_conversations.py --keyword "plink" --format json
```

**Output:**
```json
{
  "query": {
    "keywords": ["plink"],
    "file_filter": null,
    "since": null,
    "until": null
  },
  "results": [
    {
      "path": "/path/to/conversation.jsonl",
      "score": 3920,
      "message_count": 34,
      "files_touched": [...],
      "matches": [...]
    }
  ],
  "total_results": 93,
  "limit": 10
}
```

**Use cases:**
- Pipe to jq for filtering
- Import into other tools
- Automated processing

## CSV Output (Future)

### Tabular Export

```bash
uv run search_conversations.py --keyword "plink" --format csv
```

**Output:**
```csv
path,score,message_count,file_count,first_request
/path/to/conversation.jsonl,3920,34,5,"Please conduct a comprehensive..."
/path/to/conversation2.jsonl,2150,21,3,"I need to fix the manifest..."
```

**Use cases:**
- Import into Excel
- Data analysis
- Reporting

## Custom Templates (Future)

### User-Defined Formats

Allow custom templates with placeholders:

```markdown
## {file_name} (Score: {score})
Date: {date}
Messages: {message_count}

{first_user_message}

Files: {file_list}
```

**Implementation:**
```python
template = Path('~/.config/retrospecting/template.md').read_text()
output = template.format(**conversation_data)
```
