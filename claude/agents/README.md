# Claude Skills

Best practices for building skills can be found here: [Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
Use this when building new skills to ensure consistency across the ecosystem.

# Agent Capability Matrix

This document provides an overview of all agents in the ecosystem, their capabilities, and integration points.

## Core Python Development Agents

| Agent                    | Purpose                                                    | Key Integrations                     |
| ------------------------ | ---------------------------------------------------------- | ------------------------------------ |
| **python-debugger**      | Debug Python code, trace errors, performance profiling     | python-code-reviewer                 |
| **python-code-reviewer** | Review code for clarity, correctness, maintainability      | python-debugger                      |
| **python-test-engineer** | Create test suites, apply Feathers' legacy code techniques | python-code-reviewer, python-debugger |

## Architecture & Design Agents

| Agent                            | Purpose                                                            | Key Integrations                                                                |
| -------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| **software-architect**           | System design, architecture analysis, technical planning           | mermaid-expert, architecture-devils-advocate                                    |
| **architecture-devils-advocate** | Critical evaluation of architectural designs                       | software-architect                                                              |
| **architecture-contract-designer** | Create architecture proposals with visual diagrams as binding contracts | graphviz-architect, mermaid-expert, architecture-devils-advocate              |
| **mermaid-expert**               | Visual documentation specialist using mermaid-diagrams skill       | mermaid-diagrams skill, visual-design-critic, software-architect                |
| **graphviz-architect**           | Architecture diagrams and protocol contracts using graphviz-diagrams skill | graphviz-diagrams skill, visual-design-critic                              |
| **visual-design-critic**         | Critique diagrams and visualizations for clarity and effectiveness | mermaid-expert, graphviz-architect                                              |

**Note:** The mermaid-expert agent demonstrates the **agent-as-skill-wrapper pattern** - it uses the `mermaid-diagrams` skill for technical execution while focusing on collaboration, feedback loops, and strategic diagram design.

## Knowledge Agents

| Agent                      | Purpose                                                          | Key Integrations                            |
| -------------------------- | ---------------------------------------------------------------- | ------------------------------------------- |
| **obsidian-vault-manager** | Knowledge organization specialist using obsidian-vault skill     | obsidian-vault skill, mermaid-expert        |

**Note:** The obsidian-vault-manager agent demonstrates the **agent-as-skill-wrapper pattern** - it uses the `obsidian-vault` skill for technical vault operations (formatting, structure, linking) while focusing on strategic organization, preventing duplication, and building knowledge connections.

## External Consultants

| Agent                          | Purpose                                    | Voice Persona                             | Key Integrations          |
| ------------------------------ | ------------------------------------------ | ----------------------------------------- | ------------------------- |
| **gemini-consultant**          | Google Gemini integration                  | `af_sarah` (American female - friendly)   | multi-perspective-reviewer |
| **gpt5-consultant**            | GPT-5 via Cursor                           | `bm_fable` (British male - distinguished) | multi-perspective-reviewer |
| **codex-consultant**           | Codex CLI integration                      | `af_river` (American female - pragmatic)  | multi-perspective-reviewer |
| **multi-perspective-reviewer** | Synthesize multiple reviewer perspectives  | N/A                                       | All consultant agents, python-code-reviewer, architecture-devils-advocate |

**Audio Notifications:** All consultant agents provide audio summaries of their findings using the speaking skill with distinct voice personas, making it easy to differentiate between consultants when they report back.

## Code Analysis & Documentation Agents

| Agent              | Purpose                                                                            | Key Integrations                     |
| ------------------ | ---------------------------------------------------------------------------------- | ------------------------------------ |
| **code-explainer** | Comprehensive code explanation with visual diagrams and knowledge base integration | mermaid-expert, obsidian-vault-manager |

## Data & Visualization Agents

| Agent              | Purpose                                                                                                      | Key Integrations     |
| ------------------ | ------------------------------------------------------------------------------------------------------------ | -------------------- |
| **dataviz-master** | Publication-quality scientific and bioinformatics data visualization in Python (matplotlib, seaborn, plotly) | visual-design-critic |

## Utility Agents

| Agent                              | Purpose                                                                | Key Integrations                                                                         |
| ---------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **prompt-optimization-specialist** | LLM cognition expert using prompt-optimization skill to refine prompts | prompt-optimization skill, gemini-consultant, gpt5-consultant, codex-consultant |

**Note:** The prompt-optimization-specialist agent demonstrates the **agent-as-skill-wrapper pattern** - it uses the `prompt-optimization` skill for technical prompt engineering knowledge while providing cognitive expertise in LLM processing and human-AI communication.

## Integration Map

### Key Workflows

**Code Development:**

```
python-code-reviewer
         ↓
python-debugger
         ↓
python-test-engineer
```

**Architecture Design:**

```
software-architect → mermaid-expert → visual-design-critic
         ↓                   ↓                    ↓
architecture-devils-advocate  ←  (iterate)  →  refine
         ↓                   ↓
    feedback            obsidian-vault-manager
```

**Multi-Perspective Review:**

```
python-code-reviewer ──┐
architecture-devils-advocate ──┤
gemini-consultant ──┤
gpt5-consultant ──┤         multi-perspective-reviewer
codex-consultant ──┘
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

**prompt-optimization-specialist + prompt-optimization**
- **prompt-optimization skill:** Anthropic's prompt engineering patterns, foundational techniques, advanced patterns (CoT, persona-as-cognition, self-consistency, multi-agent debate), example transformations
- **prompt-optimization-specialist agent:** LLM cognition expert, human intent extraction, cognitive trade-off analysis (effectiveness vs token cost), chaining with external consultants

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

## Adding New Agents

When creating a new agent:

1. Include **Agent Integration Framework** section
2. List integrations with other agents
3. Add to this capability matrix
4. Consider if agent-as-skill-wrapper pattern applies

---

**Last Updated:** 2025-12-06

## Future Agent Ideas (Backlog)

### High Priority

- **bioinformatics-research-expert** - Deep research on biology topics, ingests papers, expert in bioinformatics tools

## Skills

Skills are reusable capabilities that can be invoked by agents or users. Unlike agents, skills don't have their own context but provide specialized workflows and bundled resources.

| Skill | Purpose | Key Resources |
|-------|---------|---------------|
| **test-driven-development** | Enforce strict TDD workflow: write test first, watch it fail, write minimal code to pass | None - Pure workflow discipline |
| **testing-anti-patterns** | Avoid common testing mistakes: never test mock behavior, never add test-only methods to production, never mock without understanding | None - Pure workflow discipline |
| **git-worktrees** | Create isolated git worktrees with smart directory selection and safety verification | None - Pure workflow discipline |
| **receiving-code-review** | Handle code review feedback with technical rigor, verification before implementation, and appropriate pushback | None - Pure workflow discipline |
| **docker-optimization** | Optimize Docker images for size, security, and performance with multi-stage builds and framework-specific patterns | None - Pure best practices knowledge |
| **speaking** | Audio notifications for completed tasks using TTS | `scripts/tts-notify` - Kokoro ONNX-based speech synthesis |
| **mermaid-diagrams** | Create, debug, and optimize Mermaid diagrams for visual documentation | `scripts/validate_diagram.py` - Syntax validation and rendering script<br/>`references/syntax_guide.md` - Comprehensive syntax rules<br/>`references/diagram_templates.md` - Reusable diagram templates |
| **graphviz-diagrams** | Create architecture diagrams, protocol contracts, and system visualizations using Graphviz DOT | `scripts/validate_diagram.py` - DOT validation and multi-engine rendering<br/>`references/syntax_guide.md` - Shape conventions and DOT syntax<br/>`references/layout_engines.md` - Layout engine selection guide<br/>`references/protocol_templates.md` - Protocol contract templates |
| **obsidian-vault** | Manage Obsidian vault operations for Ricardo's vault (formatting, structure, linking) | `references/vault_structure.md` - Folder hierarchy, naming conventions, attachment rules<br/>`references/markdown_formatting.md` - YAML frontmatter, markdown standards, tag system |
| **prompt-optimization** | Transform rough prompts into polished, effective prompts using Anthropic's best practices | `references/advanced_techniques.md` - CoT, persona-as-cognition, self-consistency, debate, context engineering<br/>`references/examples.md` - Example transformations for common scenarios |
| **dev-journaling** | Generate daily journal entries from Claude Code session logs | Scripts for log analysis and journal generation |
| **retrospecting** | Search past conversations and find design decisions | Scripts for JSONL log searching |

**Migration Notes:**
- `mermaid-expert` agent uses `mermaid-diagrams` skill for technical execution
- `graphviz-architect` agent uses `graphviz-diagrams` skill for technical execution
- `obsidian-vault-manager` agent uses `obsidian-vault` skill for technical execution
- `prompt-optimization-specialist` agent uses `prompt-optimization` skill for technical knowledge
