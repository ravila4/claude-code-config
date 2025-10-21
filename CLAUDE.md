# CLAUDE.md

**Purpose:** This document gives a high‑level overview of the `claude-code-agents` repository and points contributors to the relevant detailed documentation.

---

## What is claude‑code‑agents?

This repository defines the **agent ecosystem** for Claude‑based development workflows. It contains:

- Agent definitions (`claude/agents/*.md`)
- Shared JSON Schemas for validation
- Common conventions (learning mode, memory storage, integration framework)

Agents in this repo are **configuration and specification files**, not running code. They describe capabilities, learning workflows, and memory persistence behavior used by Claude or similar systems.

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
│   ├── scripts/                  # Tools such as validate‑memories
│   └── commands/ config/ plugins/  # Shared configuration and integrations
├── docs/
│   ├── CLAUDE_FLAT_FILE_MEMORY_SPEC.md   # Memory file spec
│   ├── AGENT_INTEGRATION_AUDIT.md        # Integration improvement plan
│   └── README.md                         # Top‑level repo overview
└── CLAUDE.md                            # ← this file
```

---

## Documentation Index

| Area                | File                                                                         | Description                                              |
| ------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------- |
| Memory Storage      | [docs/CLAUDE_FLAT_FILE_MEMORY_SPEC.md](docs/CLAUDE_FLAT_FILE_MEMORY_SPEC.md) | Defines the flat‑file `.memories/` format used by agents |
| Integration Audit   | [docs/AGENT_INTEGRATION_AUDIT.md](docs/AGENT_INTEGRATION_AUDIT.md)           | Actionable audit checklist for agent interoperability    |
| Repository Overview | [docs/README.md](docs/README.md)                                             | Explains purpose, layout, and CI setup                   |

---

## Contributing

- Add or update agent definitions under `claude/agents/`.
- Update documentation in `docs/` as needed.

  ```bash

  ```

## References

- [docs/README.md](docs/README.md) — repository overview
- [docs/CLAUDE_FLAT_FILE_MEMORY_SPEC.md](docs/CLAUDE_FLAT_FILE_MEMORY_SPEC.md) — memory schema details
- [docs/AGENT_INTEGRATION_AUDIT.md](docs/AGENT_INTEGRATION_AUDIT.md) — audit & roadmap
