# Claude Code Customization: Complete Decision Framework

## Overview

Claude Code now has **five** customization mechanisms:
1. **Slash Commands** (`.claude/commands/`)
2. **Subagents** (`.claude/agents/`)
3. **Skills** (`.claude/skills/`)
4. **Plugins** (`.claude/plugins/`)
5. **MCP Servers** (external processes)

This document clarifies when to use each, based on official Anthropic documentation and real-world usage patterns.

---

## Quick Reference

| Mechanism | Context | Invocation | Sharing | Best For |
|-----------|---------|------------|---------|----------|
| **Slash Command** | Main conversation | User types `/cmd` | Manual copy | Quick user shortcuts |
| **Subagent** | Isolated | Model or command invokes | Manual copy | Heavy specialized tasks |
| **Skill** | Main conversation | Model auto-invokes | Plugin marketplace | Reusable workflows |
| **Plugin** | N/A (container) | One-time install | Official/custom marketplace | Bundling multiple components |
| **MCP Server** | External process | Model uses as tool | npm/manual install | External data/services |

---

## Detailed Breakdown

### 1. Slash Commands

**What:** Markdown files with frontmatter in `.claude/commands/`

**How invoked:** User explicitly types `/command-name`

**Context:** Executes in main conversation (has access to all history)

**Use for:**
- Quick user-triggered operations
- Simple template expansions
- Commands that need conversation context
- User-facing shortcuts

**Example:**
```markdown
---
name: commit
description: Create a git commit
---
Create a git commit with a conventional commit message for the current changes.
```

**Don't use for:**
- Heavy processing that pollutes context
- Model-decided automation (use skills instead)
- External service integration (use MCP instead)

---

### 2. Subagents (Task tool)

**What:** Specialized agents defined in `.claude/agents/`

**How invoked:**
- Model decides (via Task tool)
- Commands launch them
- Other agents call them

**Context:** Isolated - starts with clean slate each time

**Use for:**
- Heavy, multi-step workflows
- Specialized domain expertise
- Tasks that would pollute main context
- Learning/memory storage workflows

**Example:** `python-debugger`, `architecture-devils-advocate`, `gemini-consultant`

**Don't use for:**
- Simple operations (overhead of context isolation)
- Tasks needing conversation history
- User-facing shortcuts (use commands)

---

### 3. Skills

**What:** Model-invoked workflows in `.claude/skills/`

**How invoked:** Model automatically decides when relevant

**Context:** Main conversation (like inline expansion)

**Use for:**
- **Workflows the model should autonomously use**
- Team-specific patterns/conventions
- Reusable automation that works across projects
- Things you want Claude to "just know how to do"

**Example use cases from Anthropic:**
- `pdf` - Extract and analyze PDF content
- `xlsx` - Work with Excel files
- `skill-creator` - Interactive skill generation
- Custom team workflows (coding standards, deployment patterns)

**Key insight:** Skills are like "teaching Claude a new capability" that it can use contextually

**Don't use for:**
- User-triggered operations (use commands)
- Heavy isolated work (use subagents)
- External services (use MCP)

---

### 4. Plugins

**What:** Containers that bundle commands, agents, skills, and MCP servers

**How invoked:** Install once with `/plugin install`

**Context:** N/A - plugins are just installation packages

**Use for:**
- **Distributing related customizations together**
- Team/organization standard tooling
- Marketplace-shareable functionality
- Cross-project consistency

**Structure:**
```
my-plugin/
├── plugin.json          # Metadata
├── commands/            # Slash commands
├── agents/              # Subagents
├── skills/              # Skills
└── mcp-servers/         # MCP server configs
```

**Example:** A "Python testing" plugin might include:
- `/test-python` command
- `python-test-engineer` agent
- `pytest-runner` skill
- pytest-mcp server for test discovery

**Don't use for:**
- Single-purpose tools (just use the base mechanism)
- Project-specific code (not reusable)

---

### 5. MCP Servers

**What:** External processes that provide tools/resources/prompts

**How invoked:** Model uses as tools when needed

**Context:** External process, communicates via stdio

**Use for:**
- **External data access** (databases, APIs, filesystems)
- **Stateful services** (running processes, caching)
- **Complex tools** that don't fit Claude's tool model
- **Language-specific functionality** (Python, Node.js, etc.)

**Example:**
- `@modelcontextprotocol/server-filesystem` - File access
- `@deepwiki/mcp-server` - Repository documentation
- Custom database query server

**Don't use for:**
- Simple prompts (use skills)
- Pure Claude logic (use agents/skills)
- User shortcuts (use commands)

---

## The TTS Status Notifier Example

You asked about `tts-status-notifier` - should it be an agent or a skill?

### Current: Subagent
```
/notify → launches tts-status-notifier agent
          agent generates summary
          agent calls TTS script
          returns confirmation
```

**Why this works:**
- Context isolation (don't pollute main with audio generation details)
- Other agents can call it via Task tool
- Wrapper command provides user-friendly interface

### Alternative: Skill

A skill would make sense if you want **Claude to autonomously decide** when to notify you:

```markdown
---
name: tts-notify
description: Generate audio notification when completing long tasks
---
When you complete a complex multi-step task, use this skill to:
1. Summarize the work completed
2. Generate casual TTS-optimized summary
3. Play audio notification

Usage: Automatically invoke after tasks exceeding 2+ minutes
```

**Pros:**
- Model decides when notifications are appropriate
- No explicit `/notify` needed
- Can be shared across projects via plugin

**Cons:**
- Less explicit control
- Might notify when you don't want it to

### Recommendation: Both!

```
1. Skill for autonomous notifications:
   .claude/skills/tts-notify/SKILL.md
   → Model auto-invokes after long tasks
   → Calls shared TTS script

2. Command for explicit notifications:
   /notify → simple wrapper
   → User forces notification

3. Agent for complex scenarios:
   Other agents call tts-status-notifier
   when they complete heavy work
```

---

## Decision Tree

### Start Here: What are you building?

```
┌─ User types something to trigger it
│  └─→ COMMAND (/foo)
│
├─ Claude should decide when to use it
│  ├─ Simple, inline workflow
│  │  └─→ SKILL
│  └─ Heavy, isolated processing
│     └─→ SUBAGENT (model-invoked)
│
├─ External service/data access needed
│  └─→ MCP SERVER
│
└─ Bundling multiple components
   └─→ PLUGIN (contains commands/agents/skills/MCP)
```

---

## Overlap Analysis

### Skills vs Commands
- **Commands:** User triggers explicitly
- **Skills:** Model triggers autonomously
- **Overlap:** Both can do simple workflows
- **Choose:** Do you want user control (command) or model autonomy (skill)?

### Skills vs Agents
- **Skills:** Inline in main context, lightweight
- **Agents:** Isolated context, heavy processing
- **Overlap:** Both are model-invoked
- **Choose:** Does it pollute context (agent) or stay focused (skill)?

### Skills vs MCP
- **Skills:** Claude-native workflows
- **MCP:** External services/data
- **Overlap:** Both extend capabilities
- **Choose:** Pure logic (skill) or external access (MCP)?

### Plugins vs Everything
- **Plugins are containers** - they don't replace anything
- Use plugins when you want to **bundle and share** multiple customizations
- A plugin can contain commands, agents, skills, AND MCP servers

---

## Real-World Patterns

### Pattern 1: External LLM Consultation
```
Command:  /ask-gemini $QUESTION
          ↓
Agent:    gemini-consultant (isolated, caches response)
          ↓
Result:   Summary in main context
```

**Could also be:**
```
Skill:    gemini-consultant
          Model auto-invokes when it wants second opinion
          Uses MCP server for Gemini API access
```

### Pattern 2: Testing Workflow
```
Plugin:   python-testing-suite
          ├── commands/test-python.md      (user trigger)
          ├── agents/python-test-engineer.md (heavy work)
          ├── skills/pytest-runner/        (auto test)
          └── mcp-servers/pytest-explorer/ (test discovery)
```

### Pattern 3: TTS Notifications
```
Skill:    tts-notify/                (autonomous)
          Calls: ~/scripts/tts.sh
Command:  /notify                    (user trigger)
Agent:    tts-status-notifier       (explicit by other agents)

All call same underlying script
```

---

## Migration Guide

### From Commands to Skills
If you have commands that:
- You wish Claude would just "know to use"
- Don't need explicit user triggering
- Work well inline

→ Convert to skills

### From Agents to Skills
If you have agents that:
- Don't need context isolation
- Are lightweight, focused workflows
- Would benefit from autonomous invocation

→ Consider skills instead

### From Everything to Plugins
If you have:
- Multiple related commands/agents/skills
- Team-wide standards to distribute
- Reusable across projects

→ Bundle into a plugin

---

## Open Questions

1. **Skill → Skill calls:** Can skills invoke other skills? (Likely yes, they're just expanded prompts)
2. **Skill → Agent calls:** Can skills launch agents via Task tool? (Need to test)
3. **Plugin marketplace:** How do private/team marketplaces work?
4. **Skill discoverability:** How does model know which skills to consider?

---

## Summary

**When in doubt:**
- User triggers → **Command**
- Model decides, inline → **Skill**
- Model decides, isolated → **Agent**
- External access → **MCP**
- Bundle & share → **Plugin**

The real insight: **Skills are the missing piece** between commands (user-triggered) and agents (heavy/isolated). They let you teach Claude new patterns that it autonomously applies.

---

**Last Updated:** 2025-10-19
**Status:** Living document - update as patterns emerge
