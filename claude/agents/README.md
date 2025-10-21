# Claude Skills

Best practices for building skills can be found here: [Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
Use this when building new skills to ensure consistency across the ecosystem.

# Agent Capability Matrix

This document provides an overview of all agents in the ecosystem, their capabilities, and integration points.

## Core Python Development Agents

| Agent                    | Purpose                                                    | Learning Mode | Stores Patterns | Key Integrations                                     |
| ------------------------ | ---------------------------------------------------------- | ------------- | --------------- | ---------------------------------------------------- |
| **python-debugger**      | Debug Python code, trace errors, performance profiling     | Yes (0.7)     | `.memories/`    | memory-keeper, python-code-reviewer                  |
| **python-code-reviewer** | Review code for clarity, correctness, maintainability      | Yes (0.7)     | `.memories/`    | memory-keeper, python-debugger                       |
| **python-test-engineer** | Create test suites, apply Feathers' legacy code techniques | Yes (0.7)     | `.memories/`    | memory-keeper, python-code-reviewer, python-debugger |

## Architecture & Design Agents

| Agent                            | Purpose                                                            | Learning Mode | Stores Patterns | Key Integrations                                                 |
| -------------------------------- | ------------------------------------------------------------------ | ------------- | --------------- | ---------------------------------------------------------------- |
| **software-architect**           | System design, architecture analysis, technical planning           | Yes (0.7)     | `.memories/`    | mermaid-expert, architecture-devils-advocate, memory-keeper      |
| **architecture-devils-advocate** | Critical evaluation of architectural designs                       | No            | N/A             | software-architect                                               |
| **mermaid-expert**               | Create and debug Mermaid diagrams for documentation                | Yes (0.7)     | `.memories/`    | visual-design-critic, software-architect, obsidian-vault-manager |
| **visual-design-critic**         | Critique diagrams and visualizations for clarity and effectiveness | Yes (0.7)     | `.memories/`    | mermaid-expert, memory-keeper                                    |

## Knowledge & Memory Agents

| Agent                      | Purpose                                              | Learning Mode | Stores Patterns              | Key Integrations                               |
| -------------------------- | ---------------------------------------------------- | ------------- | ---------------------------- | ---------------------------------------------- |
| **memory-keeper**          | Central pattern storage, learning across sessions    | Always active | `.memories/`, Obsidian vault | All agents (central hub)                       |
| **obsidian-vault-manager** | Manage Obsidian notes, documentation, knowledge base | Yes (0.7)     | Obsidian vault               | memory-keeper, mermaid-expert, python-debugger |

## External Consultants

| Agent                          | Purpose                                    | Learning Mode | Stores Patterns                        | Key Integrations                                                          |
| ------------------------------ | ------------------------------------------ | ------------- | -------------------------------------- | ------------------------------------------------------------------------- |
| **gemini-consultant**          | Google Gemini integration with 24h caching | No            | `.memories/external-llm-cache/gemini/` | multi-perspective-reviewer, memory-keeper                                 |
| **gpt5-consultant**            | GPT-5 via Cursor with 24h caching          | No            | `.memories/external-llm-cache/gpt5/`   | multi-perspective-reviewer, memory-keeper                                 |
| **codex-consultant**           | Codex CLI integration with 24h caching     | No            | `.memories/external-llm-cache/codex/`  | multi-perspective-reviewer, memory-keeper                                 |
| **multi-perspective-reviewer** | Synthesize multiple reviewer perspectives  | Yes (0.7)     | `.memories/reviews/`                   | All consultant agents, python-code-reviewer, architecture-devils-advocate |

## Code Analysis & Documentation Agents

| Agent              | Purpose                                                                            | Learning Mode | Stores Patterns | Key Integrations                                      |
| ------------------ | ---------------------------------------------------------------------------------- | ------------- | --------------- | ----------------------------------------------------- |
| **code-explainer** | Comprehensive code explanation with visual diagrams and knowledge base integration | Yes (0.7)     | `.memories/`    | mermaid-expert, obsidian-vault-manager, memory-keeper |

## Data & Visualization Agents

| Agent              | Purpose                                                                                                      | Learning Mode | Stores Patterns | Key Integrations                    |
| ------------------ | ------------------------------------------------------------------------------------------------------------ | ------------- | --------------- | ----------------------------------- |
| **dataviz-master** | Publication-quality scientific and bioinformatics data visualization in Python (matplotlib, seaborn, plotly) | Yes (0.7)     | `.memories/`    | visual-design-critic, memory-keeper |

## DevOps & Infrastructure Agents

| Agent                | Purpose                                                    | Learning Mode | Stores Patterns | Key Integrations |
| -------------------- | ---------------------------------------------------------- | ------------- | --------------- | ---------------- |
| **docker-optimizer** | Optimize Docker images for size, security, and performance | Yes (0.7)     | `.memories/`    | memory-keeper    |

## Utility Agents

| Agent                              | Purpose                                    | Learning Mode | Stores Patterns | Key Integrations |
| ---------------------------------- | ------------------------------------------ | ------------- | --------------- | ---------------- |
| **pr-description-writer**          | Generate PR descriptions from git diffs    | No            | N/A             | None             |
| **prompt-optimization-specialist** | Refine and optimize prompts                | No            | N/A             | None             |
| **tts-status-notifier**            | Audio notifications for long-running tasks | No            | N/A             | None             |

## Integration Map

### Central Hub

**memory-keeper** ↔ All agents (provides patterns, stores learnings)

### Key Workflows

**Code Development:**

```
python-code-reviewer → memory-keeper
         ↓
python-debugger → memory-keeper
         ↓
python-test-engineer → memory-keeper
```

**Architecture Design:**

```
software-architect → mermaid-expert → visual-design-critic
         ↓                   ↓                    ↓
architecture-devils-advocate  ←  (iterate)  →  refine
         ↓                   ↓                    ↓
    feedback            obsidian-vault-manager   ↓
                                ↓                ↓
                         memory-keeper
```

**Multi-Perspective Review:**

```
python-code-reviewer ──┐
architecture-devils-advocate ──┤
gemini-consultant ──┤
gpt5-consultant ──┤         multi-perspective-reviewer
codex-consultant ──┘                    ↓
                              memory-keeper
```

## Learning Mode

Agents with learning mode active (confidence threshold in parentheses):

- python-debugger (0.7)
- python-code-reviewer (0.7)
- python-test-engineer (0.7)
- software-architect (0.7)
- mermaid-expert (0.7)
- visual-design-critic (0.7)
- obsidian-vault-manager (0.7)
- multi-perspective-reviewer (0.7)
- code-explainer (0.7)
- docker-optimizer (0.7)
- dataviz-master (0.7)
- memory-keeper (always active - implements learning for others)

## Pattern Storage Locations

| Storage        | Used By                               | Purpose                                 |
| -------------- | ------------------------------------- | --------------------------------------- |
| `.memories/`   | Most agents                           | Project-specific patterns (JSON format) |
| Obsidian vault | obsidian-vault-manager, memory-keeper | Permanent documentation                 |

## Schemas

All agents use shared schemas in `claude/agents/schemas/`:

- `pattern.schema.json` - Code pattern structure
- `memory.schema.json` - Memory file structure

See [docs/SCHEMAS.md](../../docs/SCHEMAS.md) for details.

## Adding New Agents

When creating a new agent:

1. Include **Agent Integration Framework** section
2. Specify learning mode and confidence threshold
3. Define pattern storage location
4. List integrations with other agents
5. Add to this capability matrix
6. Update relevant schemas if needed

---

**Last Updated:** 2025-10-19

## Future Agent Ideas (Backlog)

### High Priority

- **bioinformatics-research-expert** - Deep research on biology topics, ingests papers, expert in bioinformatics tools

### Refactoring Needed

- Add hook for tts-status-notifier after notification events
