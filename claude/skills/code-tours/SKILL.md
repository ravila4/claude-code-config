---
name: code-tours
description: Generate CodeTour (.tour) files that provide guided, step-by-step walkthroughs of code changes or existing codebases. This skill should be used when the user asks for a tour or walkthrough of code, after significant multi-file changes by an agent, or when onboarding to an unfamiliar module. Produces structured JSON tours compatible with VS Code CodeTour extension and Neovim codetour.nvim.
---

# Code Tours

## Overview

Generate CodeTour `.tour` files -- structured JSON walkthroughs that link explanations to specific file:line locations in a codebase. Tours follow a deliberate narrative flow: start at the entry point, follow the logical progression, and build understanding step by step. Tours are ephemeral by default -- meant to be consumed shortly after creation, not maintained long-term. Use `ref` pinning to make a tour survive edits when persistence is needed.

## When to Use

**On-demand triggers:**
- User asks for a "tour", "walkthrough", or "explain what changed"
- User asks to understand a module, feature, or codebase area
- User wants to review changes made by an agent

**Proactive suggestions (offer once at task completion, don't auto-generate):**
- After completing multi-file changes (3+ files), offer: "Want me to generate a code tour of these changes?"
- After implementing a new feature with non-obvious control flow
- After a significant refactor that restructured existing code

**When NOT to create a tour:**
- Trivial single-file changes that are self-explanatory
- Formatting-only or dependency-update changes
- Changes already fully described by commit messages

## Tour Design Principles

The value of a tour over a flat explanation is the **narrative flow** -- it forces structured reasoning about how code connects. Apply these principles when designing tour step order:

### 1. Find the entry point

Every tour starts with the question: "Where does a reader need to begin to understand this?"

- **For changes**: Start at the most architecturally significant change, not the first file alphabetically. Often this is where the new behavior is initiated (a new endpoint, CLI command, function call, or config entry).
- **For existing code**: Start at the public API surface or the entry point a user/caller would encounter first.

### 2. Follow the execution flow

Order steps by how data or control flows through the code, not by file hierarchy. A reader should be able to follow the tour and mentally "execute" the code.

- Trace function calls from caller to callee
- Follow data transformations from input to output
- Track state changes from trigger to effect

### 3. Explain the why, not the what

Step descriptions should focus on *why* code exists and *what decisions it embodies*, not restate what the code literally does. The reader can see the code -- tell them what they can't see.

**Good:** "This validates input before it reaches the pipeline. We check schema compatibility here rather than downstream because failures at this point produce clearer error messages."

**Bad:** "This function takes a dict and checks if it has the required keys."

### 4. Group by concept, not by file

If a single concept spans multiple files, keep those steps adjacent in the tour even if it means jumping between files. Conceptual coherence matters more than minimizing file switches.

### 5. Write for the comment widget

CodeTour renders descriptions in VS Code's comment widget, which has limited markdown styling. For readability:

- **Fenced code blocks with a language** (` ```python `) get full syntax highlighting -- use these when referencing code snippets, not inline backticks.
- **Inline backticks** render with a subtle border but no color contrast -- fine for short names but don't rely on them for visual emphasis.
- **Bold** and **headings** render well -- use them to structure longer descriptions.

### 6. Keep tours focused

Aim for 5-20 steps depending on complexity. If a tour exceeds 25 steps or the narrative branches into separate concerns, split into multiple tours linked via `nextTour`.

## Workflow

### Preflight (both modes)

Before generating a tour, establish context:

```bash
# Locate repo root for correct file paths
git rev-parse --show-toplevel

# Check working tree state
git status --short
```

If the working tree is dirty (uncommitted changes), omit the `ref` field and note in the tour description that it reflects working tree state.

### Mode A: Tour of Recent Changes

1. **Gather the diff** -- adapt the range to what was changed:
   ```bash
   # Single commit
   git diff HEAD~1 --name-status

   # Branch comparison
   git diff main...HEAD --name-status

   # Full diff for context
   git diff <range>
   ```
   Use `--name-status` to detect renames (`R`) and deletions (`D`). Do not create tour steps pointing to deleted files.

2. **Identify the narrative:** What is the conceptual story of these changes? What problem do they solve?

3. **Determine entry point:** Which changed file/location would a reviewer look at first to understand the change?

4. **Trace the flow:** Order remaining changes by how they connect -- caller to callee, config to implementation, interface to concrete. Skip generated files, lockfiles, and formatting-only changes unless they affect behavior.

5. **Write the tour:** Generate the `.tour` file following the schema in `references/tour_schema.md`.

6. **Pin to commit** (if changes are committed):
   ```bash
   git rev-parse HEAD
   ```
   Set this as the `ref` field so the tour remains accurate even after further edits.

7. **Validate:** Read each referenced file at its specified line to confirm the content matches the step description.

### Mode B: Tour of Existing Code

1. **Scope the tour:** Clarify what area the user wants to understand (a module, a feature, a subsystem).

2. **Map the structure:** Read the relevant files, identify entry points, key abstractions, and data flow.

3. **Find the entry point:** Where would a new developer start reading?

4. **Build the narrative:** Order steps to progressively build understanding -- introduce concepts before they're used.

5. **Write the tour:** Generate the `.tour` file.

6. **Validate:** Confirm each step's file and line exist and point to the intended code.

### Output

1. Create the `.tours/` directory if it doesn't exist:
   ```bash
   mkdir -p .tours
   ```

2. Write the tour as UTF-8 JSON with 2-space indentation. Name the file in kebab-case:
   - Change tours: `add-caching-layer.tour`, `fix-auth-race-condition.tour`
   - Module tours: `pipeline-architecture.tour`, `api-endpoints.tour`

3. Present a brief summary to the user: what the tour covers, how many steps, and how to open it (VS Code: install CodeTour extension, then open the tour from the CodeTour panel).

## Complementary Diagrams

Tours pair well with architecture diagrams. CodeTour step descriptions support inline images via standard markdown syntax (`![alt](./path.png)`), file links, shell commands (`>> command`), and cross-references to other steps/tours. Mermaid code blocks are **not** rendered (the comment API doesn't support them).

To include a diagram in a tour step:

1. Render the diagram to PNG or SVG (e.g., via `dot -Tpng` or `mermaid-cli`)
2. Place the rendered file in `.tours/` or a project directory
3. Embed in the step description: `![Architecture overview](.tours/caching-architecture.png)`

This works well for an overview diagram in the first step, giving the reader a visual map before stepping through the code.

For the source diagram files (`.mmd`, `.dot`), keep them alongside the rendered image so they can be regenerated if needed.

## Example

A tour for a new caching feature:

```json
{
  "$schema": "https://aka.ms/codetour-schema",
  "title": "Add Redis caching to API responses",
  "description": "Walkthrough of the caching layer added to reduce database load on frequently-accessed endpoints.",
  "ref": "a1b2c3d",
  "steps": [
    {
      "title": "Cache configuration",
      "description": "New Redis connection settings. The TTL defaults are tuned for our read-heavy access pattern -- most data changes at most once per hour, so a 30-minute TTL balances freshness with hit rate.",
      "file": "config/settings.py",
      "line": 45
    },
    {
      "title": "Cache client initialization",
      "description": "The cache client is created as a singleton at app startup. Connection pooling is handled by redis-py internally. The `decode_responses=True` flag means we get strings back instead of bytes.",
      "file": "src/cache.py",
      "line": 12
    },
    {
      "title": "Decorator for cached endpoints",
      "description": "This decorator handles the cache-aside pattern: check cache first, fall through to handler on miss, store result on the way back. The key is derived from the request path + query params.\n\nNote: POST/PUT/DELETE requests bypass the cache entirely (line 38).",
      "file": "src/cache.py",
      "line": 25
    },
    {
      "title": "Applied to the products endpoint",
      "description": "This is the highest-traffic endpoint (~60% of reads). The `@cached(ttl=1800)` decorator wraps the existing handler with no changes to its logic.",
      "file": "src/api/products.py",
      "pattern": "def list_products"
    },
    {
      "title": "Cache invalidation on writes",
      "description": "When a product is updated, we explicitly invalidate its cache entry. This prevents serving stale data after writes while keeping the TTL-based expiry for the general case.",
      "file": "src/api/products.py",
      "pattern": "def update_product"
    }
  ]
}
```

Note: the last two steps use `pattern` instead of `line` to locate the code by function signature, making them resilient to line shifts from edits elsewhere in the file. Use `line` or `pattern`, not both -- see `references/tour_schema.md` for guidance on choosing between them.

## Resources

**references/tour_schema.md** - Complete CodeTour JSON schema with all fields, types, and guidance on anchoring strategies (`line` vs `pattern`). Load when generating a tour to ensure valid output.
