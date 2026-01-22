# Daily Journal Workflow Examples

## Contents
- [Scenario 1: End of Deep Work Day](#scenario-1-end-of-deep-work-day)
- [Scenario 2: Operational Day with Raw Commands](#scenario-2-operational-day-with-raw-commands)
- [Scenario 3: Incremental Journaling Throughout Day](#scenario-3-incremental-journaling-throughout-day)

## Scenario 1: End of Deep Work Day

**User:** "Can you draft today's journal?"

**Claude actions:**

1. Use daily-journal skill
2. Run `draft_journal_entry.py --mode auto`
3. Show draft with: Goals (from TodoWrite), Context (first user messages), Technical Work (git commits + files), Commands Used (bash history), Reflection placeholder

**Output:**

````markdown
---
date: 2025-11-12
tags: [daily-log, plink-file-merging, bioinformatics]
---

# 2025-11-12

Working on [[PLINK File Merging]]

## Goals

- [x] Fix GCS severity field mapping in logs
- [ ] Implement chunk status tracking
- [ ] Test manifest pre-generation

## Context

Improving plink_merger logging to include proper GCS severity fields and clearer chunk context...

## Technical Work

### Git Commits

- 76e8a97 - fix: sort overlap CSV by numeric position
- 4dd6bb1 - fix: handle concurrent manifest checkpoints

### Files Modified

- `scripts/plink_merger/plink_merger_cli.py`
- `scripts/plink_merger/plink_merger.py`

## Commands Used

```bash
# Test local merge with new logging
uv run pytest tests/test_plink_merger.py -v

# Check GCS log explorer severity
gcloud logging read "resource.type=batch_task" --limit=10
```

## Reflection

_What did I learn today?_
````

**User:** "Looks good, write it to my vault"

**Claude:** Uses obsidian-vault-manager to write to `~/Documents/Obsidian-Notes/Daily Log/2025-11-12.md`

## Scenario 2: Operational Day with Raw Commands

**User:** "I've been dumping commands all day. Can you organize my journal?"

**Claude actions:**
1. Read `~/Documents/Obsidian-Notes/Daily Log/2025-11-12.md`
2. Detect unstructured content (no headers, code blocks only)
3. Ask: "I see raw bash commands. Should I organize them into sections?"
4. If yes: Extract commands, add YAML frontmatter, create sections, show for approval

**Before:**
```markdown
uv run pytest
git commit -m "fix bug"
gcloud logging read...
cat manifest.csv
```

**After:**

````markdown
---
date: 2025-11-12
tags: [daily-log, debugging]
---

# 2025-11-12

## Commands Used

```bash
# Run tests
uv run pytest

# Check logs
gcloud logging read...

# Review manifest
cat manifest.csv
```

## Technical Work

### Git Commits

- abc1234 - fix bug
````

## Scenario 3: Incremental Journaling Throughout Day

**Mid-afternoon:**
User: "/daily-journal append context"

Claude: "Based on our conversation, I'll add this context:
_Working on fixing GCS severity field bug in plink_merger logging..._
Should I append to today's journal?"

**Before ending:**
User: "/daily-journal review"

Claude: "Today's journal is missing Reflection section. Based on our work, here's what you learned:
- GCS requires top-level `severity` field, not nested in jsonPayload
- Emoji indicators (✅/❌) improve log readability
Want me to add this?"
