# Architecture Diagrams

This directory stores Graphviz (`.dot`) and Mermaid (`.mmd`) diagrams for architecture documentation and protocol contracts.

## Convention

Every diagram in this directory MUST have a corresponding `bd` issue for tracking:

- **Issue tracks**: Why the diagram was created, approval status, context
- **File contains**: The actual diagram code

## Naming

- `[feature]-architecture.dot` - System architecture diagrams
- `[feature]-protocol.dot` - Protocol contract decision trees
- `[feature]-sequence.mmd` - Sequence diagrams (Mermaid)
- `[feature]-state.mmd` - State machine diagrams (Mermaid)

## Creating a New Diagram

1. Create the diagram file in this directory
2. Create a `bd` issue to track it:

```bash
bd create \
  --title="Protocol: [Feature] Architecture" \
  --type=task \
  --description="## Protocol Contract

**Diagram**: \`docs/diagrams/[feature]-protocol.dot\`

## Approval Status
- [ ] Initial design
- [ ] Stakeholder review
- [ ] APPROVED

## Context
[Why this diagram was created, what decisions it captures]
"
```

## Orphan Prevention

If a diagram exists without a corresponding `bd` issue, it should be either:
1. Documented with a new issue
2. Deleted if no longer relevant
