---
name: daily-journal
description: Draft, organize, or update development journal entries. Use when user requests daily journal generation, work review, standup preparation, or asks "what did I work on today/this week?"
argumentHint: "[--date YYYY-MM-DD] [--git-only]"
userInvocable: true
---

# Daily Journal

Generate daily journal entries from git commits and Claude Code sessions.

## Usage

```bash
/daily-journal              # Generate today's journal
/daily-journal --date 2026-01-23  # Specific date
/daily-journal --git-only   # Skip total recall (faster)
```

## How It Works

1. **Git-first approach**: Scans `~/Projects/` for repos with commits on the specified date
2. **Total recall integration**: Discovers additional projects touched via Contextify session logs
3. **Main project detection**: Determines primary project by commit count and session activity
4. **Template-compliant output**: Generates markdown matching Ricardo's Obsidian template

## Running the Script

When the user invokes `/daily-journal`:

1. Run the script with appropriate flags:

```bash
cd /Users/ricardoavila/Projects/claude-code-config/claude/skills/daily-journal
uv run scripts/summarize_day.py [--date YYYY-MM-DD] [--git-only]
```

2. Show the generated markdown to the user
3. Ask if they want to save it to Obsidian (`~/Documents/Obsidian-Notes/Daily Log/YYYY-MM-DD.md`)

## Output Structure

The generated journal follows this template:

```markdown
---
date: YYYY-MM-DD
tags:
  - daily-log
  - [project-tags]
---

## Summary
*One-line: What was today's main focus?*

## Goals
- [x] Completed tasks (from commits)
- [ ] In-progress tasks

## Notes

### Main Project Name
**Commits:**
- commit message 1
- commit message 2

**Files changed:** N files

### Side Projects (if any)
Brief mention of other repos with activity

## Reflection
- **What worked:**
- **What didn't:**
- **Open questions:**
- **Tomorrow's focus:**

## Related
- [[Main Project Link]]
```

## CLI Options

| Flag | Description |
|------|-------------|
| `--date YYYY-MM-DD` | Generate journal for specific date (default: today) |
| `--git-only` | Skip Contextify session discovery (faster) |
| `--projects-dir PATH` | Custom projects directory (default: ~/Projects) |
| `--output FILE` | Write to file instead of stdout |

## Data Sources

### Git Commits (Primary)
- Scans all repos in `~/Projects/`
- Extracts commit messages and file change counts
- Ranks projects by activity level

### Total Recall / Contextify (Secondary)
- Uses `contextify-query activity` to find session activity
- Correlates sessions with git repos for better project detection
- Can be skipped with `--git-only` for faster generation

## Tips

- Run at end of day for best results (more commits to analyze)
- Use `--git-only` for quick checks during the day
- The script handles repos with no activity gracefully
- Side projects with single commits are included but not emphasized

## References

See `references/` for additional documentation on log formats and patterns.
