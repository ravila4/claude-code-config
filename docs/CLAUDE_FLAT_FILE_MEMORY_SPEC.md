# Claude Code Agents Memory Store

> **Purpose:** For the `claude-code-agents` repo: let agents persist and read memories using **plain JSON files** in the project’s repo under `.memories/`, with strong schemas and deterministic behavior. This enables immediate use (no DB needed) and a clean path to later ingest into an external memory service.

---

## 0) Scope & Principles

- **This spec lives in `claude-code-agents`.**
- **Local-first.** All agent memory data lives in a project repo under `.memories/`.
- **Schema-driven.** Every file must validate against a shared JSON Schema.
- **Append-only bias.** Prefer creating new versions over mutating in place.
- **Idempotent writes.** Every create has a `client_uid` to avoid duplicates.
- **Deterministic names.** File naming encodes type and ID.
- **Safe writes.** Write to temp file, fsync, then atomic rename.
- **Human-auditable.** Diff-friendly, stable field order, minimal noise.

---

## 1) Directory Layout

```
<project-root>/    # Project repo can be any codebase that a Claude agent works on
  .memories/
    manifest.json                 # repo-level metadata & versions
    index.json                    # lightweight registry for quick listing
    memories/
      mem_<uuid>.json             # pattern/memory records
    sources/
      src_<uuid>.json             # monitored knowledge sources (docs, APIs)
    backlog/
      bl_<uuid>.json              # backlog items
    events/
      ev_<uuid>.json              # learning/enforcement events (optional)
    schemas/                      # pinned JSON Schemas (copied here for agents)
      memory.schema.json
      source.schema.json
      backlog.schema.json
      event.schema.json
      index.schema.json
      manifest.schema.json
    locks/
      write.lock                  # optional advisory file to serialize heavy writes

# In the agents repo (shared definitions for validation at runtime)
claude/
  agents/
    schemas/                      # canonical copies (authoritative for CI)
      memory.schema.json
      source.schema.json
      backlog.schema.json
      event.schema.json
      index.schema.json
      manifest.schema.json
  scripts/
    validate-memories            # script that validates .memories/* against schemas
```

> **Note:** Agents should not rely on reading `locks/`. Locking is best-effort; atomic renames are the source of truth.

---

## 2) File Naming & IDs

- IDs are UUIDv4 strings.
- Filenames encode type prefix and ID: `mem_<uuid>.json`, `src_<uuid>.json`, etc.
- No nested subdirs per type (keeps globbing simple).

---

## 3) JSON Canonicalization Rules

- UTF‑8, LF newlines, no BOM.
- 2‑space indentation; keys in **lexicographic** order.
- Timestamps in **UTC ISO‑8601** with `Z` suffix, e.g., `2025-10-18T13:40:35Z`.
- Booleans/lists preferred over ad‑hoc strings.
- No trailing commas.

---

## 4) Schemas (high level)

### 4.1 `memory.schema.json` (Pattern/Memory)

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "memory.schema.json",
  "type": "object",
  "required": [
    "id",
    "project_slug",
    "title",
    "category",
    "severity",
    "do_text",
    "dont_text",
    "confidence",
    "provenance",
    "status",
    "learned_at",
  ],
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "client_uid": { "type": "string", "format": "uuid" },
    "project_slug": { "type": "string", "minLength": 1 },
    "title": { "type": "string", "maxLength": 140 },
    "category": { "type": "string" },
    "severity": { "type": "string", "enum": ["info", "warning", "error"] },
    "do_text": { "type": "string", "minLength": 1 },
    "dont_text": { "type": "string", "minLength": 1 },
    "example": { "type": "string" },
    "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
    "confidence_source": {
      "type": "string",
      "enum": [
        "user-instruction",
        "official-docs",
        "inferred",
        "verified-pattern",
      ],
    },
    "provenance": {
      "type": "object",
      "required": ["agent", "agent_version"],
      "properties": {
        "agent": { "type": "string" },
        "agent_version": { "type": "string" },
        "source_url": { "type": "string", "format": "uri" },
        "source_type": {
          "type": "string",
          "enum": [
            "official_docs",
            "api_ref",
            "maintainer_blog",
            "so_answer",
            "community",
            "inferred",
          ],
        },
      },
      "additionalProperties": false,
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "uniqueItems": true,
    },
    "status": { "type": "string", "enum": ["active", "stale", "archived"] },
    "learned_at": { "type": "string", "format": "date-time" },
    "stale_after": { "type": "string", "format": "date-time" },
  },
  "additionalProperties": false,
}
```

### 4.2 `source.schema.json`

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "source.schema.json",
  "type": "object",
  "required": [
    "id",
    "project_slug",
    "name",
    "url",
    "type",
    "priority",
    "schedule",
  ],
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "project_slug": { "type": "string" },
    "name": { "type": "string" },
    "url": { "type": "string", "format": "uri" },
    "type": {
      "type": "string",
      "enum": [
        "official_docs",
        "api_ref",
        "maintainer_blog",
        "so_answer",
        "community",
        "inferred",
      ],
    },
    "priority": { "type": "integer", "minimum": 1, "maximum": 5 },
    "schedule": { "type": "string" },
    "last_checked": { "type": "string", "format": "date-time" },
    "etag": { "type": "string" },
    "version": { "type": "string" },
    "last_error": { "type": "string" },
    "retry_after": { "type": "string", "format": "date-time" },
  },
  "additionalProperties": false,
}
```

### 4.3 `backlog.schema.json`

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "backlog.schema.json",
  "type": "object",
  "required": ["id", "project_slug", "title", "status"],
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "project_slug": { "type": "string" },
    "title": { "type": "string", "maxLength": 140 },
    "description": { "type": "string" },
    "priority": { "type": "string", "enum": ["low", "med", "high"] },
    "status": {
      "type": "string",
      "enum": ["todo", "doing", "done", "archived"],
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "uniqueItems": true,
    },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" },
  },
  "additionalProperties": false,
}
```

### 4.4 `event.schema.json` (optional)

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "event.schema.json",
  "type": "object",
  "required": ["id", "project_slug", "kind", "ts"],
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "project_slug": { "type": "string" },
    "kind": {
      "type": "string",
      "enum": [
        "added_memory",
        "modified_memory",
        "docs_update",
        "auto_fix",
        "enforcement_hit",
      ],
    },
    "ts": { "type": "string", "format": "date-time" },
    "pattern_id": { "type": "string", "format": "uuid" },
    "details": { "type": "object" },
  },
  "additionalProperties": false,
}
```

### 4.5 `index.schema.json`

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "index.schema.json",
  "type": "object",
  "required": ["version", "projects"],
  "properties": {
    "version": { "type": "string" },
    "projects": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["slug", "mem_count"],
        "properties": {
          "slug": { "type": "string" },
          "name": { "type": "string" },
          "mem_count": { "type": "integer" },
          "last_updated": { "type": "string", "format": "date-time" },
        },
        "additionalProperties": false,
      },
    },
  },
  "additionalProperties": false,
}
```

### 4.6 `manifest.schema.json`

```jsonc
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "manifest.schema.json",
  "type": "object",
  "required": ["schema_version", "created_at"],
  "properties": {
    "schema_version": { "type": "string" },
    "created_at": { "type": "string", "format": "date-time" },
    "generator": { "type": "string" },
    "notes": { "type": "string" },
  },
  "additionalProperties": false,
}
```

---

## 5) Allowed Operations (for agents)

All operations are **file-based** and must pass schema validation.

### 5.1 Create memory

1. Generate `id` (UUID) and optional `client_uid`.
2. Compute baseline `confidence` based on `confidence_source`:
   - `user-instruction`: 0.95
   - `official-docs`: 0.90
   - `verified-pattern`: 0.85
   - `inferred`: 0.65

3. Normalize fields (trim whitespace, collapse multiple spaces, cap sizes).
4. Write to `memories/mem_<id>.json.tmp` → fsync → rename to `memories/mem_<id>.json`.
5. Append/update `index.json` counts.

### 5.2 Update memory

- Create a **new version** (optional) or mutate in place with `updated_at`.
- If mutating, ensure atomic write; consider keeping `events/` record with diff.

### 5.3 Forget (archive)

- Set `status = "archived"`; do **not** delete files (keeps history).

### 5.4 Sources & due checks

- New sources go under `sources/`.
- An external job (or agent) can compute **due** by reading `schedule` + `last_checked` and act.

### 5.5 Backlog

- Backlog items are standalone JSON files under `backlog/`.

---

## 6) Validation & Idempotency

- Every create path should accept a `client_uid`. If a file with the same `client_uid` has already been written (tracked via a small `client_uids/<uid>` marker file or inside the memory file), skip creating a duplicate and return the existing `id`.
- All files must validate against schemas under `.memories/schemas/` at write-time.

---

## 7) Confidence & Staleness Rules (flat‑file)

- **On create:** set baseline as in §5.1.
- **On docs update:** agents scanning `sources/` may mark linked memories `status = "stale"` and add an event in `events/`.
- **Decay (optional):** agents may lower confidence by small monthly decay unless recently referenced.

---

## 8) Retrieval (flat‑file)

- Agents may:
  - Filter by `project_slug`, `category`, `severity`, `status`, `tags`.
  - Do simple substring search in `title`, `do_text`, `dont_text`.
  - Rank results by: recency boost (last 30d), confidence, and a crude lexical match score.

- Keep result sets **small** (top 20) and include compact snippets.

---

## 9) Examples

### 9.1 Memory file (`.memories/memories/mem_<uuid>.json`)

```json
{
  "id": "2b6ce1b8-2b2f-4a9e-9f47-3b5409185f0e",
  "client_uid": "8d9a7b5b-7b94-4d25-9e0a-2d9a6a34b7f1",
  "project_slug": "my-app",
  "title": "Convex query pattern for TanStack",
  "category": "data-fetching",
  "severity": "error",
  "do_text": "useQuery(convexQuery(api.tasks.get, { id }))",
  "dont_text": "await convexQuery(api.tasks.get, { id })",
  "example": "const { data } = useQuery(convexQuery(api.tasks.get, { id }))",
  "confidence": 0.9,
  "confidence_source": "official-docs",
  "provenance": {
    "agent": "memory-knowledge-keeper",
    "source_url": "https://docs.convex.dev",
    "source_type": "official_docs"
  },
  "tags": ["convex", "tanstack"],
  "status": "active",
  "learned_at": "2025-10-18T13:40:35Z"
}
```

### 9.2 Source file (`.memories/sources/src_<uuid>.json`)

```json
{
  "id": "3f2b9d23-7f6a-4a2f-8c9e-8f23c1d9a4e2",
  "project_slug": "my-app",
  "name": "Convex Docs",
  "url": "https://docs.convex.dev",
  "type": "official_docs",
  "priority": 1,
  "schedule": "weekly",
  "last_checked": "2025-10-10T09:30:00Z"
}
```

### 9.3 Backlog file (`.memories/backlog/bl_<uuid>.json`)

```json
{
  "id": "7f4c8a27-4bb2-41f1-8d4a-7d0b3f4d8c1e",
  "project_slug": "my-app",
  "title": "Refactor query pattern checks",
  "description": "Consolidate do/don't into shared helper",
  "priority": "med",
  "status": "todo",
  "tags": ["techdebt"],
  "created_at": "2025-10-18T13:41:07Z"
}
```

### 9.4 Manifest & Index

```json
// .memories/manifest.json
{
  "schema_version": "0.1",
  "created_at": "2025-10-18T13:39:00Z"
}
```

```json
// .memories/index.json
{
  "version": "0.1",
  "projects": [
    {
      "slug": "my-app",
      "name": "My App",
      "mem_count": 12,
      "last_updated": "2025-10-18T13:41:07Z"
    }
  ]
}
```

---

## 10) Agent Contract (refactor guidance for Claude agents)

### 10.1 Shared Schema Repository

- Add and maintain **canonical schemas** under `claude/agents/schemas/`.
- Copy (or symlink) the same files into each project’s `.memories/schemas/` for local validation.
- All agents **must** validate objects before writing files (see `claude/commands/validate-memories`).

### 10.2 Write API (file ops)

- **Create:**
  1. Build JSON object → validate against schema.
  2. Generate `id`/`client_uid` if absent.
  3. Write `*.tmp` → fsync → rename to final path.
  4. Update `index.json` counts (best-effort).

- **Update:**
  - Either mutate in place (atomic) or create a new file + add event under `events/`.

- **Forget:**
  - Set `status: "archived"` and rewrite atomically.

### 10.3 Learning Mode Behavior

- If confidence < 0.7, agents:
  1. search `.memories/memories` for similar items;
  2. consult `sources/` for docs;
  3. ask user for clarification;
  4. write memory with high confidence;
  5. add `events/ev_*.json` recording the change.

### 10.4 Retrieval Contract

- Agents read files and may build an in‑memory index (category/tags/title keywords).
- Limit result set sizes; include compact snippets when passing to other agents.

### 10.5 Integration Documentation Template (to add to each agent)

```
## Agent Integration Framework

**Can Integrate With:**
- [agent-name]: [how they work together]

**Provides to Other Agents:**
- [capability/data type]

**Requires from Other Agents:**
- [dependency]

**Learning Mode:** [yes/no]
**Stores Patterns In:** `.memories/` flat-files (this spec)
**Validates Against:** `claude/agents/schemas/*.json`
```

### 10.6 Runtime Validation Hook

- Coordination agents (`agent-router`, `agent-orchestration-manager`) should run schema validation on inter-agent payloads before dispatch.

---

## 11) Ingestion Path to Postgres/pgvector (later)

- A single **ingestor** scans `.memories/` and upserts into DB:
  - `memories/` → `pattern` table
  - `sources/` → `source` table
  - `backlog/` → `backlog` table
  - `events/` → `learning_event`/`enforcement_hit`

- Preserve `id`, `client_uid`, timestamps, and tags.
- Optionally compute `mem_emb` from `do_text+dont_text+title` and store in `pattern.mem_emb`.

---

## 12) Safety & Concurrency

- Single‑writer recommended per repo (router/orchestrator enforces it). If multiple writers:
  - Use `locks/write.lock` as an advisory lock (create file → write PID → perform operation → delete).
  - Still rely on atomic rename for correctness.

- Agents must tolerate partial writes (ignore `*.tmp`).

---

## 13) Compliance Checklist (for agent PRs)

- [ ] Writes validate against schema (`claude/commands/validate-memories` passes)
- [ ] Uses atomic write flow
- [ ] Populates `confidence_source` appropriately
- [ ] Sets `client_uid` on create
- [ ] Avoids unbounded file scans (filters first)
- [ ] Adds events for significant changes
- [ ] Updates `index.json` best‑effort
- [ ] Produces deterministic JSON formatting
- [ ] Adds **Agent Integration Framework** section in the agent’s markdown
- [ ] References shared schemas from `claude/agents/schemas/`

---

## 14) Future Extensions

- `relations/` folder to link memories ↔ sources ↔ code locations
- `snapshots/` for deterministic YAML exports used in code review
- local sqlite cache for faster reads (optional, generated, ignored by VCS)

---
