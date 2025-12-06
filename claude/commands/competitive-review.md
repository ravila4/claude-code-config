---
description: "Dispatch two competing subagents to review code for architecture and implementation issues"
argumentHint: "[file(s) or component to review]"
---

# Competitive Code Review: $ARGUMENTS

Launch TWO subagents IN PARALLEL to review the specified code. Use the Task tool with two simultaneous invocations.

## Agent Instructions

Both agents receive this briefing:

---

**COMPETITIVE REVIEW MISSION**

You are competing against another agent to find issues in this code. The agent who finds more legitimate issues gets promoted.

Your review must cover BOTH:
1. **Architecture** - Design patterns, separation of concerns, coupling, cohesion, extensibility, SOLID principles
2. **Implementation** - Bugs, edge cases, error handling, performance, security, readability, maintainability

Be thorough. Be critical. Your competitor is working right now trying to find more issues than you.

**Target:** $ARGUMENTS

Report your findings as a numbered list with severity (Critical/Major/Minor) and category (Architecture/Implementation).

---

## Dispatch

Use the Task tool to launch BOTH agents simultaneously:
- Agent 1: `subagent_type=python-code-reviewer` with the briefing above
- Agent 2: `subagent_type=architecture-devils-advocate` with the briefing above

After both complete, synthesize their findings and highlight:
- Issues found by both (high confidence)
- Unique finds from each agent
- Total issue count per agent (declare a winner)
