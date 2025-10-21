# Agent Integration Audit

> Source: external review on **2025-10-18**. This document distills third‑party feedback into **actionable work items**. Keep this file updated as items are addressed. Do not store proprietary reviewer output verbatim; capture the essence and decisions.

---

## 1) Executive Summary

- Strengths: core coordination agents; consistent learning mode (threshold = 0.7); solid router/orchestrator/planner triad; memory/pattern foundation.
- Gaps: no shared schemas; inconsistent integration docs; validation missing at runtime; some standalone agents not wired into learning system; potential circular refs.

---

## 2) Action Items (Backlog)

| ID   | Area       | Issue                                                                                                                         | Severity | Owner | Plan                                                    | Status |
| ---- | ---------- | ----------------------------------------------------------------------------------------------------------------------------- | -------- | ----- | ------------------------------------------------------- | ------ |
| A‑01 | Schemas    | Create **shared schema repository** at `claude/agents/schemas/` (messages, patterns, validation-results, orchestration-plans) | High     | @you  | Seed JSON Schemas; add CI validation                    | TODO   |
| A‑02 | Validation | Add **runtime validation hooks** in `agent-router` & `agent-orchestration-manager`                                            | High     | @you  | Integrate Ajv/Pydantic and fail fast on mismatch        | TODO   |
| A‑03 | Docs       | Add **Agent Integration Framework** section to every agent                                                                    | Med      | @you  | Use standard template; link capabilities & dependencies | TODO   |
| A‑04 | Learning   | Standardize **learning mode** across standalone agents (or document "no learning")                                            | Med      | @you  | Apply 0.7 threshold workflow                            | TODO   |
| A‑05 | Matrix     | Create `agents/README.md` with **capability matrix**                                                                          | Med      | @you  | Generate table via script                               | TODO   |
| A‑06 | Wiring     | Connect `obsidian-vault-manager` ↔ `memory-knowledge-keeper`                                                                 | Med      | @you  | Add store/read of patterns via `.memories/`             | TODO   |
| A‑07 | Wiring     | Complete `mermaid-expert` integration stubs                                                                                   | Med      | @you  | Document Provides/Requires; implement calls             | TODO   |
| A‑08 | Models     | Document **model selection rationale** per agent                                                                              | Low      | @you  | Inline comments + table                                 | TODO   |
| A‑09 | Arch       | Resolve **circular dependencies** (use registry pattern)                                                                      | Low      | @you  | Implement `AgentRegistry`                               | TODO   |

---

## 3) Acceptance Criteria (per item)

- **Schemas in repo**: CI job validates sample payloads; PRs fail on schema drift.
- **Runtime validation**: router rejects messages that fail schema; logs reason.
- **Integration docs**: every agent file contains the standard block and links.
- **Learning mode**: agents either implement the threshold flow or mark `learning: false` with rationale.
- **Matrix**: `agents/README.md` builds cleanly and stays in sync with files.

---

## 4) Standard Blocks & Paths

- Template: **Agent Integration Framework** (paste into each agent):

```
## Agent Integration Framework

**Can Integrate With:**
- [agent-name]: [how they work together]

**Provides to Other Agents:**
- [capability/data type]

**Requires from Other Agents:**
- [dependency]

**Learning Mode:** [yes/no]
**Stores Patterns In:** `.memories/`
**Validates Against:** `claude/agents/schemas/*.json`
```

- Shared schemas live at: `claude/agents/schemas/`
- Validation script: `claude/commands/validate-memories`

---

## 5) Scorecard (tracked locally)

Update periodically with evidence (commit/PR links).

| Agent                   | Integration Docs | Learning Mode | Pattern Storage | Schema Defined | Score |
| ----------------------- | ---------------- | ------------- | --------------- | -------------- | ----- |
| agent-router            | ✅               | ✅            | ✅              | ✅             | 100%  |
| memory-knowledge-keeper | ✅               | ✅            | ✅              | ✅             | 100%  |
| …                       | …                | …             | …               | …              | …     |

---

## 6) Decisions & ADRs

- ADR‑001: Adopt `.memories/` flat‑file spec (v0.1) for interim persistence.
- ADR‑002: Add runtime schema validation at integration boundaries.
- ADR‑003: Move model selection rationale into each agent header.

---

## 7) Open Questions

- Should Python agents receive a thin wrapper for JSON validation to simplify adoption?
- Which fields are required for cross‑agent search (minimum viable index)?

---

## 8) Changelog

- 2025‑10‑18: Initial audit distilled; action backlog created.
