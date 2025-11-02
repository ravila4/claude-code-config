# Using Claude Code Skills with OpenAI Codex

This document explains how to use the skills from this repository with OpenAI Codex, following an approach inspired by [Jesse's Superpowers blog post](https://blog.fsck.com/2025/10/27/skills-for-openai-codex/).

## Overview

The skills in this repository are designed to be LLM-agnostic. While they were originally created for Claude Code, they can be adapted for use with other AI coding assistants, including OpenAI Codex.

## Setup

The setup has already been completed for this repository. Here's what was done:

### 1. Directory Structure

```
~/.codex/
├── AGENTS.md              # Bootstrap instructions for Codex
├── skills/                # Symlink to claude/skills directory
└── scripts/
    ├── bootstrap          # Skill discovery and setup
    ├── list-skills        # List all available skills
    └── use-skill          # View a specific skill's documentation
```

### 2. Symlinks Created

```bash
~/.codex/skills → /Users/ricardoavila/Projects/claude-code-agents/claude/skills
```

This allows Codex to access the same skills that Claude Code uses, without duplicating the skill files.

### 3. Configuration Files

**AGENTS.md** - Main configuration file that Codex reads on startup:
- Contains bootstrap command
- Lists all available skills
- Provides tool mapping guidance
- Explains how to use skills

## Using Skills with Codex

### Bootstrap Command

When starting a new session with Codex, run the bootstrap command to see all available skills:

```bash
~/.codex/scripts/bootstrap
```

This will display:
- All available skills with descriptions
- Instructions for using skills
- Tool mapping for Codex compatibility

### Listing Skills

To see a formatted list of all skills:

```bash
~/.codex/scripts/list-skills
```

### Using a Specific Skill

To view the documentation for a specific skill:

```bash
~/.codex/scripts/use-skill <skill-name>
```

Examples:
```bash
~/.codex/scripts/use-skill mermaid-diagrams
~/.codex/scripts/use-skill test-driven-development
~/.codex/scripts/use-skill document-skills/pdf
```

### In Codex Sessions

When working with Codex:

1. **Identify relevant skill**: Ask Codex to check available skills or run `bootstrap`
2. **Load the skill**: Ask Codex to read the skill file using `use-skill`
3. **Follow the guidance**: The skill provides step-by-step instructions
4. **Adapt tool usage**: Use the tool mapping provided in AGENTS.md

## Tool Mapping

Since Codex doesn't have the same native tools as Claude Code, use these equivalents:

| Claude Code Tool | Codex Equivalent |
|------------------|------------------|
| `TodoWrite` | `update_plan` |
| `Skill` tool | Read and follow SKILL.md file |
| `Task` (subagents) | Manual task execution |
| `Read/Write/Edit` | Native file operation tools |

## Key Differences from Claude Code

1. **No Native Skill Tool**: Codex doesn't have a built-in skill invocation mechanism. Instead, you explicitly read the SKILL.md file and follow its instructions.

2. **Manual Task Management**: Instead of TodoWrite, use Codex's `update_plan` feature to track progress.

3. **Direct Tool Usage**: Skills may reference Claude Code-specific tools. Translate these to Codex equivalents using the mapping table.

4. **Literal Instruction Following**: According to Jesse's testing, Codex may actually be better at following skill instructions literally, without adding unnecessary interpretation.

## Available Skills

Run `~/.codex/scripts/list-skills` to see the full list. Current skills include:

- **mermaid-diagrams**: Visual documentation with Mermaid
- **graphviz-diagrams**: Architecture diagrams with Graphviz
- **test-driven-development**: TDD workflow guidance
- **legacy-code-testing**: Techniques for testing legacy code
- **docker-optimization**: Docker image optimization
- **obsidian-vault**: Obsidian note management
- **prompt-optimization**: Prompt engineering best practices
- **mcp-builder**: MCP server creation guide
- And more...

## Adding New Skills

Skills are maintained in the `claude/skills/` directory of this repository. Any new skills added there will automatically be available to Codex through the symlink.

To create a new skill, use the `skill-creator` skill:

```bash
~/.codex/scripts/use-skill skill-creator
```

## Maintenance

### Updating Skills

Since `~/.codex/skills` is symlinked to the repository, updating skills in the repository automatically makes them available to Codex.

### Adding Personal Skills

To add Codex-specific personal skills that shouldn't be in the Claude Code repository, you can:

1. Create a separate directory (e.g., `~/.codex/personal-skills`)
2. Modify the bootstrap script to search this directory as well
3. Personal skills will take precedence over repository skills if names conflict

## Inspiration

This setup was inspired by Jesse's [Superpowers for Codex](https://blog.fsck.com/2025/10/27/skills-for-openai-codex/) blog post, which demonstrated that skills can be effectively ported across different AI coding assistants.

## References

- [Jesse's Superpowers Blog Post](https://blog.fsck.com/2025/10/27/skills-for-openai-codex/)
- [Claude Code Skills Documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/)
- [Superpowers Repository](https://github.com/obra/superpowers)
