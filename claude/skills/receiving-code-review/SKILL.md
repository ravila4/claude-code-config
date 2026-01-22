---
name: receiving-code-review
description: Guidance for handling code review feedback with technical rigor before implementation, especially when suggestions lack clarity or seem technically questionable. Use when receiving feedback from the user or other agents like architecture-devils-advocate, python-code-reviewer, or external consultants.
---

# Receiving Code Review

## Overview

Handle code review feedback with technical rigor and verification before implementation. Emphasize understanding and evaluation over performative agreement.

**Core Principle:** Verification over performative agreement.

## When to Use

Apply this skill when:
- Receiving code review feedback from any source
- Suggestions lack clarity or technical detail
- Recommendations seem questionable for your specific context
- You're unsure about scope or implementation approach
- Feedback conflicts with architectural decisions

## Workflow

### 1. Read Completely

Read all feedback without immediate reaction:
- Don't interrupt with clarifying questions mid-review
- Don't start implementing before understanding the full scope
- Note all suggestions, concerns, and questions

### 2. Understand Requirements

Restate requirements in your own words:
- Paraphrase what you think is being requested
- Ask specific clarifying questions if unclear
- Confirm you understand the "why" not just the "what"

**If confused about scope:** STOP—do not implement anything yet.
- Partial understanding leads to incorrect implementation
- Request full clarification before proceeding

### 3. Verify Against Codebase

Check feedback against actual codebase conditions:
- Does the suggested problem actually exist?
- Is the recommended approach compatible with current architecture?
- Are there dependencies or constraints the reviewer may not see?

**YAGNI Check:**
Search the codebase for actual usage before implementing "professional" features:
```bash
# Example: Check if endpoint is actually used
grep -r "api/endpoint" .
rg "endpoint" --type js --type py
```

If unused: Remove rather than polish.

### 4. Evaluate Technical Soundness

Assess suggestions within your specific stack:
- Does this work with our framework/language version?
- Will this break existing functionality?
- Is the reviewer aware of our full context?
- Does this align with project conventions?

**Source-Specific Handling:**

**Internal feedback** (team members, internal tools):
- Understand the technical requirement
- Verify against codebase
- Proceed with implementation if sound

**External feedback** (external reviewers, automated tools):
- Apply heightened skepticism
- Verify technical correctness thoroughly
- Check for functionality breaks
- Confirm reviewer understands your full context

### 5. Respond with Technical Reasoning

**Forbidden performative responses:**
- "You're absolutely right!"
- "Great point!"
- "Thanks for catching that!"
- "I should have thought of that!"

**Instead use:**
- Restate technical requirements: "I'll refactor the error handling to use try-catch blocks around the database calls"
- Ask clarifying questions: "Should this validation apply to all endpoints or just the public API?"
- Proceed directly to implementation (no acknowledgment needed)

**When to push back:**

Challenge feedback that:
- Breaks existing functionality
- Lacks understanding of full context
- Violates YAGNI principles (adds unused features)
- Conflicts with documented architectural decisions
- Suggests premature optimization

**Push back with technical reasoning:**
- "This would break the existing OAuth flow because..."
- "Our architecture uses event sourcing, which means..."
- "I searched the codebase and this endpoint isn't called anywhere"
- "The ADR for this module specifies..."

**Not defensiveness:**
- Avoid "I thought...", "I was trying to...", "But I..."

### 6. Implement Incrementally

Apply changes with testing:
- Implement one suggestion at a time
- Run tests after each change
- Verify no regressions
- Commit incremental changes with clear messages

**Acknowledging correct feedback:**
Simply state what changed:
- "Refactored error handling per review"
- "Added validation to user input endpoints"
- "Removed unused /admin/legacy endpoint"

Let the code demonstrate you understood. No gratitude expressions needed.

## Decision Tree

```
Receive Feedback
    ↓
Understand it fully?
    ├─ No → Request clarification (STOP implementation)
    └─ Yes → Continue
         ↓
    Verify against codebase
         ↓
    Technically sound for your context?
         ├─ No → Push back with reasoning
         └─ Yes → Continue
              ↓
         Feature actually used? (YAGNI check)
              ├─ No → Propose removal instead
              └─ Yes → Implement incrementally
```

## Examples

### Example 1: Unclear Scope

**Feedback:** "The error handling needs improvement"

**Bad Response:** "You're absolutely right! I'll fix it."

**Good Response:** "Can you clarify which error scenarios you'd like handled? Should this apply to all database calls or specific endpoints?"

### Example 2: YAGNI Violation

**Feedback:** "Add comprehensive logging to all API endpoints"

**Action:** Search codebase for logging consumers
```bash
rg "logger\." --type py
```

**Finding:** No log aggregation system configured, logs not monitored

**Response:** "I searched the codebase and we don't have log monitoring configured. Should we set up log aggregation first, or is there a specific issue you're trying to debug?"

### Example 3: Context Missing

**Feedback:** "Use async/await instead of callbacks"

**Verification:** Check Node.js version in package.json → v12 (async/await supported)

**But also check:** Existing codebase patterns → all callbacks, no async/await anywhere

**Response:** "Our codebase uses callbacks throughout. Should we migrate everything to async/await, or maintain consistency with existing patterns? If migrating, should that be a separate refactoring task?"

### Example 4: Breaking Change

**Feedback:** "Change this API endpoint to return arrays instead of objects"

**Verification:** Search for endpoint usage
```bash
rg "api/users" --type js --type ts
```

**Finding:** 15 call sites expecting object response

**Response:** "This endpoint is called in 15 locations expecting object responses. Changing to arrays would break all of them. Can you clarify the requirement? If arrays are needed, should we version the API?"

### Example 5: Correct Feedback

**Feedback:** "Missing input validation on userId parameter"

**Verification:** Check code → indeed no validation

**Action:** Add validation, write test, commit

**Response:** "Added userId validation in commit abc123"

(No "thanks" needed—code speaks for itself)

## Red Flags Requiring Pushback

- Suggestions to add features with no callers in codebase
- Recommendations that break existing contracts without migration plan
- "Best practices" that don't apply to your specific stack
- Premature optimization without performance data
- Complexity added without concrete benefit
