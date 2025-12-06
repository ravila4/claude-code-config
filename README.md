# claude-code-agents

**Agent definitions, skills, and conventions for a multi-agent Claude Code workflow.**

This repo contains agent specs (markdown), reusable skills, and operational conventions that extend Claude Code's capabilities. Agents are specialized sub-agents that can be spawned via the Task tool, while skills provide reusable workflows and resources that can be invoked directly.

---

## Why this exists

- **Specialization:** Agents with focused expertise (debugging, architecture review, external LLM consultation)
- **Reusability:** Skills bundle domain knowledge, scripts, and templates for common tasks
- **Interoperability:** Standard patterns for agent collaboration and skill composition
- **Extensibility:** Easy to add new agents and skills following established patterns

---

## Quick start

1. **Install / link configs**
   - This repo is designed to be symlinked into `~/.claude/` (dotfiles style), or used in-repo.

2. **Use agents via Task tool**
   - Agents are spawned automatically when Claude Code determines they're needed
   - Or explicitly request: "Use the python-debugger agent to investigate this error"

3. **Use skills via Skill tool**
   - Invoke skills directly: `skill: "mermaid-diagrams"`
   - Skills load their instructions and resources into context

---

## Repository layout

```
.
├── claude/
│   ├── agents/                    # agent definitions (markdown)
│   │   └── README.md              # capabilities matrix
│   ├── skills/                    # reusable skills with resources
│   │   ├── mermaid-diagrams/      # diagram creation skill
│   │   ├── graphviz-diagrams/     # architecture diagram skill
│   │   ├── obsidian-vault/        # knowledge management skill
│   │   └── ...
│   ├── commands/                  # slash commands
│   ├── hooks/                     # Claude Code hooks
│   └── settings.json              # Claude global settings
├── docs/                          # additional documentation
└── CLAUDE.md                      # core principles and usage guide
```

---

## Key documents

- **claude/agents/README.md** - Agent capability matrix and design patterns
- **CLAUDE.md** - Core principles and agent usage guide

---

## Agent Categories

**Core Python Development:**
- python-debugger, python-code-reviewer, python-test-engineer

**Architecture & Design:**
- software-architect, architecture-devils-advocate, mermaid-expert, graphviz-architect, visual-design-critic

**External Consultants:**
- gemini-consultant, gpt5-consultant, codex-consultant, multi-perspective-reviewer

**Knowledge & Documentation:**
- obsidian-vault-manager, code-explainer

See `claude/agents/README.md` for the full capability matrix.

---

## Skills

Skills are reusable capabilities with bundled resources (scripts, references, templates).

| Skill | Purpose |
|-------|---------|
| **mermaid-diagrams** | Create and validate Mermaid diagrams |
| **graphviz-diagrams** | Architecture diagrams and protocol contracts |
| **obsidian-vault** | Obsidian vault management |
| **speaking** | Audio notifications via TTS |
| **prompt-optimization** | Optimize prompts using Anthropic best practices |
| **dev-journaling** | Generate journal entries from session logs |

---

## Design Patterns

### Agent-as-Skill-Wrapper

Some agents wrap skills, combining technical capabilities with collaboration:
- **mermaid-expert** agent uses **mermaid-diagrams** skill
- **graphviz-architect** agent uses **graphviz-diagrams** skill
- **obsidian-vault-manager** agent uses **obsidian-vault** skill

Use skill alone for direct technical execution. Use agent when collaboration or strategic decisions are needed.

---

## Contributing

- Follow the capability matrix format when adding agents
- Include the Agent Integration Framework section in agent definitions
- Add skills with proper structure (SKILL.md, references/, scripts/)

---

## License

MIT (unless stated otherwise in subfolders).
