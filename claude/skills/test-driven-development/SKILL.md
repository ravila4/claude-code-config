---
name: test-driven-development
description: Use when implementing any feature or bugfix, before writing implementation code - write the test first, watch it fail, write minimal code to pass
---

# Test-Driven Development (TDD)

## Overview

Write the test before the implementation, observe it fail, then write the simplest code to make it pass. If you haven't witnessed the test fail, you lack certainty that it validates the correct behavior.

## When to Use

Apply TDD consistently to:
- Feature development
- Bug resolution
- Code refactoring
- Behavioral modifications

**Exceptions** require explicit user approval:
- Throwaway prototypes
- Auto-generated code
- Configuration files

## The Iron Law

**Production code must never exist without a preceding failing test.**

If code is written before tests:
1. Delete it entirely
2. Restart with tests first
3. No exceptions - don't keep it as reference, don't look at it, just delete

## Red-Green-Refactor Cycle

### RED Phase: Write a Failing Test

Write a single minimal test demonstrating intended behavior:
- Clear, descriptive name
- Test actual functionality (not mocks unless necessary)
- Focus on one behavior
- If test name contains "and", split into separate tests

### Verify RED: Confirm Failure

Run tests and confirm:
- Test fails for the expected reason (missing feature)
- Not failing due to syntax errors
- This verification is non-negotiable

### GREEN Phase: Minimal Implementation

Write the simplest possible code satisfying the test:
- Avoid feature creep
- Don't refactor unrelated code
- Don't over-engineer

### Verify GREEN: Confirm Pass

Confirm:
- The new test passes
- No existing tests break

### REFACTOR Phase: Clean Up

Improve code quality while maintaining green status:
- Eliminate duplication
- Improve naming
- Simplify logic
- Run tests after each change

## Quality Test Attributes

**Minimal:** Single responsibility per test
**Clear:** Descriptive name revealing behavior
**Realistic:** Demonstrate intended API usage
**Focused:** One assertion per test (generally)

## Common Rationalizations to Reject

**"I'll test afterward"**
- Tests written post-implementation pass immediately
- Proves nothing about validation capability

**"Manual testing covered edge cases"**
- Lacks systematic documentation
- Not reproducible

**"Deleting hours of work wastes effort"**
- Sunk cost fallacy
- Unverified code is technical debt

**"Tests-after achieve identical goals"**
- Tests-first answer: "What should happen?"
- Tests-after answer: "What does this do?"
- Fundamentally different approaches

## Red Flags Requiring Restart

Delete code and restart with TDD if:
- Code written before tests
- Tests pass immediately on first run
- Can't explain why test failed
- Any rationalization about "just this once"

## Verification Checklist

Before considering work complete:
- [ ] Every new function has corresponding tests
- [ ] Each test failed before implementation
- [ ] Failures occurred for expected reasons
- [ ] Code written is minimal
- [ ] All tests pass without errors or warnings
- [ ] Real code tested (mocks only when necessary)
- [ ] Edge cases and error conditions covered

## Integration with Other Skills

**Works with:**
- Language-specific testing frameworks
- Legacy code refactoring techniques
- Continuous integration workflows

**Complements:**
- Test engineering (comprehensive suite design)
- Code review (verification of test coverage)
- Debugging (tests isolate failures)
