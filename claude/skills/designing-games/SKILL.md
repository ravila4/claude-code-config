---
name: designing-games
description: Game design principles for text-based games, interactive fiction, and RPGs. Provides MDA framework, balance principles, narrative consistency checklists, and worldbuilding rules. Use when creating or reviewing game mechanics, story structure, or player experience.
---

# Designing Games

Foundational principles for designing text-based games that are fun, not just functional.

## Core Framework: MDA

**Mechanics → Dynamics → Aesthetics**

The MDA framework decomposes games into three layers:

| Layer | Definition | Designer's View | Player's View |
|-------|------------|-----------------|---------------|
| **Mechanics** | Rules, systems, code | What you build | Discovered last |
| **Dynamics** | Emergent behavior | What happens at runtime | Experienced through play |
| **Aesthetics** | Emotional response | What you want players to feel | Felt first |

Designers work Mechanics → Dynamics → Aesthetics.
Players experience Aesthetics → Dynamics → Mechanics.

**The Eight Aesthetics** (types of "fun"):
1. **Sensation** — Sense-pleasure
2. **Fantasy** — Make-believe, escapism
3. **Narrative** — Drama, story
4. **Challenge** — Obstacle course, mastery
5. **Fellowship** — Social connection
6. **Discovery** — Exploration, surprise
7. **Expression** — Self-discovery, creativity
8. **Submission** — Relaxation, idle pleasure

For detailed MDA application: See [references/mda_framework.md](references/mda_framework.md)

## Quick Reference Checklists

### Narrative Consistency

- [ ] Objects remain in the state the player left them
- [ ] NPCs remember previous interactions
- [ ] Navigation is predictable across the experience
- [ ] World rules stay consistent (no "because plot")
- [ ] Character motivations track logically
- [ ] No dead ends without explicit endings

For complete checklist: See [references/narrative_consistency.md](references/narrative_consistency.md)

### Game Balance

- [ ] Power curves appropriate (linear/quadratic/logarithmic)
- [ ] Resource sources balanced against sinks
- [ ] No dominant strategies that trivialize choices
- [ ] Difficulty scales with progression
- [ ] Stats that are set are also checked (and vice versa)
- [ ] Risk/reward proportional across paths

For balance frameworks and formulas: See [references/balance_principles.md](references/balance_principles.md)

### Worldbuilding (Sanderson's Laws Generalized)

1. **Limit #1**: Systems solve problems in proportion to reader understanding
2. **Limit #2**: Limitations > powers (constraints create drama)
3. **Limit #3**: Expand what you have before adding new elements

For worldbuilding rules: See [references/worldbuilding_rules.md](references/worldbuilding_rules.md)

## When to Use This Skill

**Learning/Reference**: Consult frameworks while designing game systems
**Review Preparation**: Understand what the gameplay-reviewer agent will check
**Design Decisions**: Apply MDA lens to mechanic choices
**Troubleshooting**: When a game feels "flat," identify which aesthetic is missing

## Visualization

For diagramming game structure, use the **graphviz-diagrams** skill:

| Game Concept | Graphviz Pattern |
|--------------|------------------|
| Story branches | Decision tree (diamond nodes for choices) |
| State transitions | State machine pattern |
| Economy flows | Dependency graph with labeled edges |
| Quest structure | Directed graph with clustering by act/chapter |

**Highlighting structural issues:**
- Dead ends: terminal nodes with `fillcolor=red`
- False choices: edges that converge immediately (visually obvious)
- Orphaned content: disconnected subgraphs
- Bottlenecks: nodes with high in-degree

## Integration with Agents

**gameplay-reviewer**: Uses these frameworks to evaluate games. The reviewer applies MDA analysis, checks narrative consistency, and assesses balance.

To run a gameplay review:
```
Launch gameplay-reviewer agent with:
- Source code (for structural review), OR
- Playthrough logs (for experiential review), OR
- Both for comprehensive review
```

## Key Principles

1. **Fun is the metric** — Technical correctness is necessary but not sufficient
2. **Player experience is truth** — If it feels wrong, it is wrong
3. **Constraints enable creativity** — Limitations produce better designs
4. **Playtest > theory** — Frameworks are lenses, not laws
