# Pull Request Description Structure Guide

This guide provides detailed standards for crafting effective pull request descriptions.

## PR Description Sections

### Title
- **Length**: 50 characters or less when possible
- **Format**: Action-oriented, present tense
- **Examples**:
  - Good: "Add caching layer for API responses"
  - Good: "Fix memory leak in connection pool"
  - Avoid: "Added some caching stuff" (vague)
  - Avoid: "This PR adds a caching layer..." (too verbose)

### Type
State the primary category of the change:
- **Bug Fix**: Corrects existing functionality
- **Feature**: Adds new functionality
- **Optimization**: Improves performance or efficiency
- **Refactor**: Restructures code without changing behavior
- **Documentation**: Updates docs, comments, or READMEs
- **Tests**: Adds or modifies test coverage
- **Chore**: Maintenance tasks, dependency updates, etc.

Format: "Type: Feature" or "Type: Bug Fix"

### Rationale
Explain **WHY** these changes are necessary. This is the most important section.

Focus on:
- **The problem being solved** or opportunity being addressed
- **Business or technical justification** for the change
- **Impact on users or system behavior**

Examples:
- Good: "The current API client doesn't cache responses, causing excessive network calls and slow page loads. Users report 3-5 second delays when navigating between pages."
- Avoid: "This PR adds caching" (doesn't explain why)

### Changes
Provide a **bulleted list** of key changes at a high level.

Guidelines:
- Focus on **WHAT changed**, not HOW it was implemented
- Group related changes together
- **Highlight breaking changes** or migrations required with clear markers (e.g., "⚠️ BREAKING:")
- Mention any **new dependencies** or requirements
- Avoid implementation details unless critical for understanding

Example:
```
- Add Redis-backed caching layer for API responses
- Implement cache invalidation on data mutations
- Add cache hit/miss metrics to observability dashboard
- ⚠️ BREAKING: Requires Redis instance (see deployment notes)
```

### Testing
Briefly describe how changes were validated.

Examples of what to include (if apparent from diff or conversation):
- New unit tests added
- Integration tests updated
- Manual testing performed
- Performance benchmarks run

### Notes
Additional context reviewers should know:

- **Related issues or tickets** (if mentioned in conversation)
- **Follow-up work needed** (known limitations or future improvements)
- **Deployment considerations** (migration steps, feature flags, rollout strategy)
- **Areas needing careful review** (complex logic, security implications)
- **Dependencies on other PRs** (if applicable)

## Writing Quality Standards

### Clarity
- **Be concise but complete**: Reviewers should understand the PR without diving into code
- **Use present tense** for describing what the PR does
- **Avoid jargon** when possible, or define technical terms
- **Structure with clear headers** to improve scanability

### Focus
- Emphasize **"why"** and **"what"**, not **"how"**
- Implementation details should only be included if:
  - They involve critical architectural decisions
  - They have security implications
  - They require special reviewer attention

### Completeness
- **Ensure all significant changes are mentioned**
- **Verify the rationale clearly justifies the changes**
- **Check that the description makes sense** to someone unfamiliar with recent discussions
- **Confirm breaking changes are clearly marked** if present

### Risks and Review Focus
- Call out any **risky or complex areas**
- Highlight **security-sensitive changes**
- Note **performance-critical code** that needs benchmarking
- Identify **edge cases** that may need extra testing

## Example PR Description

```markdown
# Add Redis caching layer for API responses

Type: Feature

## Rationale

The current API client doesn't cache responses, causing excessive network calls during normal application usage. Users report 3-5 second page load times when navigating between product pages, and monitoring shows 80% of API calls are identical repeated requests within 5-minute windows. This caching layer will reduce API load and improve user experience.

## Changes

- Add Redis-backed caching layer for GET API responses
- Implement automatic cache invalidation on POST/PUT/DELETE operations
- Add cache hit/miss metrics to observability dashboard
- Configure TTL policies: 5 minutes for product data, 1 hour for static content
- ⚠️ BREAKING: Requires Redis instance (connection string via REDIS_URL env var)

## Testing

- Added unit tests for cache key generation and TTL policies
- Integration tests verify cache invalidation on mutations
- Load testing shows 65% reduction in API calls and 2.1s average page load

## Notes

- Deployment requires Redis instance provisioned before rollout
- Future work: Add cache warming for popular products (tracked in #1234)
- Review focus: Cache invalidation logic in `src/cache/invalidator.ts:45-78`
```

## Common Mistakes to Avoid

1. **Vague titles**: "Fix bug" instead of "Fix memory leak in connection pool"
2. **Missing rationale**: Jumping straight to changes without explaining why
3. **Implementation details**: Describing every function instead of high-level changes
4. **Buried breaking changes**: Not clearly marking changes that require action
5. **Assuming context**: Not explaining acronyms or domain-specific terms
6. **No testing info**: Leaving reviewers wondering if changes were validated
7. **Overly long**: More than 500 words without justified complexity

## Length Guidelines

- **Standard PR**: 200-300 words
- **Complex PR**: 300-500 words
- **Major refactor/architecture change**: 500+ words (justified by complexity)
- If exceeding 500 words, consider breaking into multiple PRs

## Tone and Voice

- **Professional but conversational**: "This PR adds..." not "This pull request shall implement..."
- **Active voice**: "Add caching layer" not "A caching layer was added"
- **Specific**: "Reduce API calls by 65%" not "Improve performance significantly"
- **Objective**: Focus on facts, not opinions or speculation
