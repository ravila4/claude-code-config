# claude-code-agents

**Agent definitions, conventions, and shared schemas for a multi‑agent development workflow.**

This repo contains _agent specs_ (markdown), _shared JSON Schemas_, and _operational conventions_ that make independent agents interoperate. Agents are optimized to persist short, structured memories as **flat JSON files** under each project’s `.memories/` folder. A separate project (e.g., **Engram**) may ingest those files into a database later—agents here do **not** depend on any specific backend.

---

## Why this exists

- **Interoperability:** standard formats for messages, patterns, and results.
- **Learning:** a consistent **learning mode** (confidence threshold = `0.7`) across agents.
- **Traceability:** human‑auditable memories stored as JSON in the repo.
- **Pluggability:** backends are optional; the flat‑file spec is the contract.

---

## Quick start

1. **Install / link configs**
   - This repo is designed to be symlinked into `~/.claude/` (dotfiles style), or used in‑repo.

2. **Use the flat‑file memory spec**
   - In your project, create:

     ```
     <project>/
       .memories/
         memories/  sources/  backlog/  events/  schemas/
         manifest.json  index.json
     ```

   - See **docs/CLAUDE_FLAT_FILE_MEMORY_SPEC.md** for required fields and examples.

3. **Validate**
   - Run the validator to ensure all `.memories/` files match the schemas:

     ```bash
     claude/commands/validate-memories
     ```

4. **Adopt the Agent Integration Framework**
   - Each agent’s markdown should include the standardized block (Provides/Requires, Learning Mode, etc.). See **docs/AGENT_INTEGRATION_AUDIT.md**.

---

## Repository layout

```
.
├── claude/
│   ├── agents/                    # agent definitions (markdown)
│   │   ├── schemas/               # shared JSON Schemas used by agents
│   │   └── README.md              # capabilities matrix (generated)
│   ├── config/                    # shared configuration defaults
│   ├── commands/                  # claude slash commands (see claude docs)
│   ├── scripts/                   # utility scripts
│   ├── plugins/                   # optional tool integrations (see claude docs)
│   ├── settings.json              " Claude global settings"
│   └── settings.local.json
├── docs/
│   ├── README.md                  # ← this file (top‑level overview)
│   ├── CLAUDE_FLAT_FILE_MEMORY_SPEC.md
│   └── AGENT_INTEGRATION_AUDIT.md
└── CLAUDE.md                      # Core principles and agent usage guide
```

> **Note:** Agents write/read _project‑local_ `.memories/` folders inside each target repo they operate on. This repository only defines the contract and validation.

---

## Key documents

- **docs/CLAUDE_FLAT_FILE_MEMORY_SPEC.md** — canonical spec for `.memories/` files (schemas, atomic writes, idempotency).
- **docs/AGENT_INTEGRATION_AUDIT.md** — action plan for standardizing schemas, validation, and integrations.
- **CLAUDE.md** — core principles and agent usage guide.

---

## Conventions

- **Learning mode:** if `confidence < 0.7`, agents enter clarify‑then‑store workflow.
- **Confidence defaults:** user‑instruction `0.95`, official‑docs `0.90`, inferred `0.65`.
- **Atomic writes:** write `*.tmp` → fsync → rename; set `client_uid` for idempotency.
- **Deterministic JSON:** lexicographic keys, 2‑space indent, UTC timestamps.
- **Provenance:** every memory includes `provenance.agent` and optional `source_url`/`source_type`.

---

## Validation & CI

- Schemas live in `claude/agents/schemas/` and are mirrored into each project’s `.memories/schemas/`.
- `claude/commands/validate-memories` validates all files; wire it into pre‑commit/CI.
- Coordination agents must validate inter‑agent payloads at runtime (router/orchestrator hooks).

---

## Roadmap

- Flat‑file memory spec (v0.1) and validator script
- Add Integration Framework block to all agents
- Capability matrix generator for `claude/agents/README.md`
- Runtime schema validation across coordination boundaries

## Contributing

- Follow the **Compliance Checklist** in the memory spec before sending PRs.
- Include the **Agent Integration Framework** section in any new/updated agent.
- Add/update sample payloads under `claude/agents/schemas/samples/` and ensure validation passes.

---

## License

MIT (unless stated otherwise in subfolders).
