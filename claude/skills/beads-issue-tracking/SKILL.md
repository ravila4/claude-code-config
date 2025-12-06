---
name: beads-issue-tracking
description: Track bugs, features, and tasks using the bd (beads) CLI for git-versioned issue management. Use for any work that should persist across sessions or machines - discovered bugs, planned features, multi-session tasks. Use TodoWrite for session-level task breakdown showing immediate progress.
---

# Beads Issue Tracking

## Overview

bd (beads) is a git-backed issue tracker. Issues are stored in `.beads/issues.jsonl` and version-controlled, enabling work continuity across sessions and machines.

## When to Use bd vs TodoWrite

| Situation | Tool | Why |
|-----------|------|-----|
| Bug discovered during work | `bd create` | Persists for future sessions |
| Feature to implement later | `bd create` | Track across machines/sessions |
| Multi-session task | `bd create` | Survives compaction/context loss |
| Breaking down current work into steps | TodoWrite | Shows user real-time progress |
| Tracking progress within a session | TodoWrite | Visual feedback for user |

**Rule**: If it should survive the session, use bd. If it shows progress now, use TodoWrite.

## Essential Workflow

### Starting a Session

ALWAYS check for pending work when starting on a project with `.beads/`:

```bash
bd ready              # ALWAYS run this first - shows unblocked work
bd show <id>          # Review issue details
bd update <id> --status=in_progress  # Claim it
```

If no `.beads/` directory exists, either run `bd init` to set up beads or skip if the project doesn't use it.

### During Work

When discovering new work while implementing something else, ALWAYS link it:

```bash
bd create --title="Found edge case in validator" --type=bug --deps discovered-from:<current-id>
```

The `discovered-from` link preserves context about where issues originated.

### Completing Work

```bash
bd close <id>                    # Single issue
bd close <id1> <id2> <id3>       # Multiple issues (more efficient)
bd close <id> --reason="Fixed by adding null check"  # With explanation
```

### Session End

```bash
bd sync --flush-only    # Export changes to JSONL (git hooks handle the rest)
```

## Creating Issues

```bash
# Basic
bd create --title="Add retry logic to API client" --type=task

# With priority (0=critical, 1=high, 2=medium, 3=low, 4=backlog)
bd create --title="Security: validate input" --type=bug --priority=0

# Linked to discovery context (ALWAYS use when finding work during other work)
bd create --title="Edge case found" --type=bug --deps discovered-from:beads-abc
```

To add dependencies after creation, use `bd dep add`:
```bash
bd dep add <this-issue> <depends-on>  # this-issue depends on depends-on
```

### Issue Types

- `bug` - Something broken
- `feature` - New functionality
- `task` - Work item (tests, docs, refactoring)
- `epic` - Large feature with subtasks
- `chore` - Maintenance

## Querying Issues

```bash
bd ready                    # Unblocked, ready to work
bd list --status=open       # All open issues
bd list --status=in_progress # Currently active
bd blocked                  # Issues waiting on dependencies
bd show <id>                # Full details with dependencies
bd stats                    # Project overview
```

## Dependencies

```bash
# Add dependency: issue-A depends on issue-B (B blocks A)
bd dep add <issue-A> <issue-B>

# View what blocks an issue
bd show <id>
```

## Concrete Examples

**User asks to fix a bug:**
```
User: "Fix the null pointer in the parser"

1. bd create --title="Fix null pointer in parser" --type=bug --priority=1
2. bd update beads-xxx --status=in_progress
3. [Fix the bug using TDD]
4. bd close beads-xxx --reason="Added null check before access"
```

**Discovering issues during work:**
```
Working on beads-abc, find that tests are missing:

bd create --title="Add missing tests for parser" --type=task --deps discovered-from:beads-abc
```

**Starting fresh session:**
```
bd ready
# Shows: beads-def "Implement retry logic" (no blockers)
bd update beads-def --status=in_progress
[Continue work]
```

## Integration with Git

bd auto-syncs to `.beads/issues.jsonl`. At session end:
1. `bd sync --flush-only` - export pending changes to JSONL
2. `git add .beads/` and commit with your other changes

For health checks: `bd doctor`
