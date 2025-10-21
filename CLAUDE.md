# CLAUDE.md

**Purpose:** This document gives a high‑level overview of the `claude-code-agents` repository and points contributors to the relevant detailed documentation.

---

## What is claude‑code‑agents?

This repository defines the **agent and skill ecosystem** for Claude‑based development workflows. It contains:

- Agent definitions (`claude/agents/*.md`)
- Skill definitions (`claude/skills/*/SKILL.md`)
- Shared JSON Schemas for validation
- Common conventions (learning mode, memory storage, integration framework)

Agents in this repo are **configuration and specification files**, not running code. They describe capabilities, learning workflows, and memory persistence behavior used by Claude or similar systems.

Skills are **reusable capabilities** that provide specialized knowledge, workflows, and bundled resources (scripts, references, assets) that can be invoked by agents or users.

---

## Key Concepts

- **Learning Mode:** All agents can enter a learning state when confidence < `0.7`.
- **Memory Storage:** Uses the [Flat‑File Memory Spec](docs/CLAUDE_FLAT_FILE_MEMORY_SPEC.md) — agents store structured `.json` memories in a `.memories/` folder within each project.
- **Schemas:** Common JSON Schemas ensure consistent data validation.
- **Integration Framework:** Defines how agents communicate, share knowledge, and validate interactions.

---

## Repository Structure

```
claude-code-agents/
├── claude/
│   ├── agents/                    # Agent definitions (markdown)
│   │   ├── schemas/               # Shared schemas used across agents
│   │   └── README.md              # Capabilities matrix (generated)
│   ├── skills/                    # Skill definitions
│   │   ├── skill-creator/         # Skill for creating skills
│   │   ├── tts-notifier/          # TTS audio notifications
│   │   ├── mcp-builder/           # MCP server builder
│   │   └── document-skills/       # PDF, DOCX, PPTX, XLSX
│   ├── scripts/                   # Tools such as validate‑memories
│   └── commands/ config/ plugins/  # Shared configuration and integrations
├── docs/
│   ├── CLAUDE_FLAT_FILE_MEMORY_SPEC.md   # Memory file spec
│   ├── AGENT_INTEGRATION_AUDIT.md        # Integration improvement plan
│   └── README.md                         # Top‑level repo overview
└── CLAUDE.md                            # ← this file
```

---

## Documentation Index

| Area                | File                                                                         | Description                                                  |
| ------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Memory Storage      | [docs/CLAUDE_FLAT_FILE_MEMORY_SPEC.md](docs/CLAUDE_FLAT_FILE_MEMORY_SPEC.md) | Defines the flat‑file `.memories/` format used by agents     |
| Integration Audit   | [docs/AGENT_INTEGRATION_AUDIT.md](docs/AGENT_INTEGRATION_AUDIT.md)           | Actionable audit checklist for agent interoperability        |
| Repository Overview | [docs/README.md](docs/README.md)                                             | Explains purpose, layout, and CI setup                       |
| Skills              | [claude/agents/CLAUDE.md](claude/agents/CLAUDE.md)                           | Skills registry and capability matrix for agents and skills  |

---

## Contributing

**Adding Agents:**
- Add or update agent definitions under `claude/agents/`.
- Update `claude/agents/CLAUDE.md` capability matrix
- Update documentation in `docs/` as needed.

**Adding Skills:**
- Use `claude/skills/skill-creator/scripts/init_skill.py` to initialize a new skill
- Follow best practices from [Claude Skills Documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- Validate and package with `claude/skills/skill-creator/scripts/package_skill.py`
- Update `claude/agents/CLAUDE.md` skills registry

## References

- [docs/README.md](docs/README.md) — repository overview
- [docs/CLAUDE_FLAT_FILE_MEMORY_SPEC.md](docs/CLAUDE_FLAT_FILE_MEMORY_SPEC.md) — memory schema details
- [docs/AGENT_INTEGRATION_AUDIT.md](docs/AGENT_INTEGRATION_AUDIT.md) — audit & roadmap
