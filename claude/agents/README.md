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

| Agent                            | Purpose                                                            | Learning Mode | Stores Patterns | Key Integrations                                                                        |
| -------------------------------- | ------------------------------------------------------------------ | ------------- | --------------- | --------------------------------------------------------------------------------------- |
| **software-architect**           | System design, architecture analysis, technical planning           | Yes (0.7)     | `.memories/`    | mermaid-expert, architecture-devils-advocate, memory-keeper                             |
| **architecture-devils-advocate** | Critical evaluation of architectural designs                       | No            | N/A             | software-architect                                                                      |
| **mermaid-expert**               | Visual documentation specialist using mermaid-diagrams skill       | Yes (0.7)     | `.memories/`    | mermaid-diagrams skill, visual-design-critic, software-architect, obsidian-vault-manager, memory-keeper |
| **visual-design-critic**         | Critique diagrams and visualizations for clarity and effectiveness | Yes (0.7)     | `.memories/`    | mermaid-expert, memory-keeper                                                           |

**Note:** The mermaid-expert agent demonstrates the **agent-as-skill-wrapper pattern** - it uses the `mermaid-diagrams` skill for technical execution while focusing on collaboration, feedback loops, and strategic diagram design. See `claude/agents/diagrams/mermaid-expert-interactions.svg` for visual documentation.

## Knowledge & Memory Agents

| Agent                      | Purpose                                              | Learning Mode | Stores Patterns              | Key Integrations                               |
| -------------------------- | ---------------------------------------------------- | ------------- | ---------------------------- | ---------------------------------------------- |
| **memory-keeper**          | Central pattern storage, learning across sessions    | Always active | `.memories/`, Obsidian vault | All agents (central hub)                       |
| **obsidian-vault-manager** | Knowledge organization specialist using obsidian-vault skill | Yes (0.7)     | Obsidian vault               | obsidian-vault skill, memory-keeper, mermaid-expert, python-debugger |

**Note:** The obsidian-vault-manager agent demonstrates the **agent-as-skill-wrapper pattern** - it uses the `obsidian-vault` skill for technical vault operations (formatting, structure, linking) while focusing on strategic organization, preventing duplication, and building knowledge connections.

## External Consultants

| Agent                          | Purpose                                    | Voice Persona | Learning Mode | Stores Patterns                        | Key Integrations                                                          |
| ------------------------------ | ------------------------------------------ | ------------- | ------------- | -------------------------------------- | ------------------------------------------------------------------------- |
| **gemini-consultant**          | Google Gemini integration with 24h caching | `af_sarah` (American female - friendly)    | No            | `.memories/external-llm-cache/gemini/` | multi-perspective-reviewer, memory-keeper                                 |
| **gpt5-consultant**            | GPT-5 via Cursor with 24h caching          | `bm_fable` (British male - distinguished)   | No            | `.memories/external-llm-cache/gpt5/`   | multi-perspective-reviewer, memory-keeper                                 |
| **codex-consultant**           | Codex CLI integration with 24h caching     | `af_river` (American female - pragmatic)    | No            | `.memories/external-llm-cache/codex/`  | multi-perspective-reviewer, memory-keeper                                 |
| **multi-perspective-reviewer** | Synthesize multiple reviewer perspectives  | N/A           | Yes (0.7)     | `.memories/reviews/`                   | All consultant agents, python-code-reviewer, architecture-devils-advocate |

**Audio Notifications:** All consultant agents provide audio summaries of their findings using the tts-notifier skill with distinct voice personas, making it easy to differentiate between consultants when they report back.

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

## Design Patterns

### Agent-as-Skill-Wrapper Pattern

Some agents act as wrappers around skills, combining technical capabilities with collaboration and strategic decision-making.

**Pattern Structure:**
- **Skill:** Provides technical execution, domain knowledge, and reusable resources
- **Agent:** Provides persona, collaboration with other agents, and strategic workflow

**Examples:**

**mermaid-expert + mermaid-diagrams**
- **mermaid-diagrams skill:** Syntax rules, validation, templates, rendering scripts
- **mermaid-expert agent:** Requirements analysis, agent collaboration, iterative feedback loops with visual-design-critic

**graphviz-architect + graphviz-diagrams**
- **graphviz-diagrams skill:** DOT syntax, layout engines, protocol templates, validation scripts
- **graphviz-architect agent:** Protocol contract design, approval workflow, binding specifications for implementations

**obsidian-vault-manager + obsidian-vault**
- **obsidian-vault skill:** Vault structure, markdown formatting, YAML frontmatter, folder hierarchy, attachment rules
- **obsidian-vault-manager agent:** Search & prevent duplication, strategic note placement, knowledge connections, consolidation decisions

**When to Use This Pattern:**

Use **skill only** when:
- Technical execution is self-contained
- No agent collaboration needed
- Users can invoke directly (e.g., document format conversion)

Use **agent only** when:
- Capability requires context and decision-making
- No reusable technical resources needed
- Collaboration is the primary value

Use **agent + skill** when:
- Technical complexity benefits from bundled resources (scripts, references)
- Agent collaboration adds strategic value
- Iterative feedback loops improve outcomes
- Same technical capability used across multiple contexts

**Benefits:**
- **Reduced context:** Technical details in skill, loaded only when needed
- **Reusability:** Skills can be used by multiple agents or directly by users
- **Separation of concerns:** Technical execution vs. strategic collaboration
- **Maintainability:** Update technical details in skill without changing agent workflows

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

- ~~Add hook for tts-status-notifier after notification events~~ - Converted to skill (tts-notifier)

### Skills

Skills are reusable capabilities that can be invoked by agents or users. Unlike agents, skills don't have their own context but provide specialized workflows and bundled resources.

| Skill | Purpose | Key Resources |
|-------|---------|---------------|
| **test-driven-development** | Enforce strict TDD workflow: write test first, watch it fail, write minimal code to pass | None - Pure workflow discipline |
| **git-worktrees** | Create isolated git worktrees with smart directory selection and safety verification | None - Pure workflow discipline |
| **receiving-code-review** | Handle code review feedback with technical rigor, verification before implementation, and appropriate pushback | None - Pure workflow discipline |
| **tts-notifier** | Audio notifications for completed tasks using TTS | `scripts/tts-notify` - Kokoro ONNX-based speech synthesis |
| **mermaid-diagrams** | Create, debug, and optimize Mermaid diagrams for visual documentation | `scripts/validate_diagram.py` - Syntax validation and rendering script<br/>`references/syntax_guide.md` - Comprehensive syntax rules<br/>`references/diagram_templates.md` - Reusable diagram templates |
| **graphviz-diagrams** | Create architecture diagrams, protocol contracts, and system visualizations using Graphviz DOT | `scripts/validate_diagram.py` - DOT validation and multi-engine rendering<br/>`references/syntax_guide.md` - Shape conventions and DOT syntax<br/>`references/layout_engines.md` - Layout engine selection guide<br/>`references/protocol_templates.md` - Protocol contract templates |
| **obsidian-vault** | Manage Obsidian vault operations for Ricardo's vault (formatting, structure, linking) | `references/vault_structure.md` - Folder hierarchy, naming conventions, attachment rules<br/>`references/markdown_formatting.md` - YAML frontmatter, markdown standards, tag system |

**Migration Notes:**
- `tts-status-notifier` agent → `tts-notifier` skill
- `mermaid-expert` agent → `mermaid-diagrams` skill (agent uses skill for technical execution)
- `graphviz-architect` agent → `graphviz-diagrams` skill (agent uses skill for technical execution)
- `obsidian-vault-manager` agent → `obsidian-vault` skill (archived - can invoke skill directly)
