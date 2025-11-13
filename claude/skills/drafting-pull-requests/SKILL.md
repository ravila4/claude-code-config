---
name: drafting-pull-requests
description: Create comprehensive pull request descriptions by analyzing git diffs between branches. Use when the user has finished implementing changes and wants to document them in a PR. This skill analyzes code changes, incorporates conversation context about why changes were made, and produces well-structured PR descriptions focusing on rationale and high-level impact.
---

# Drafting Pull Requests

## Overview

This skill guides the creation of effective pull request descriptions by analyzing git branch differences and structuring them into clear, reviewer-friendly documentation. The goal is to communicate the purpose, impact, and key changes to reviewers without requiring them to understand every implementation detail.

## When to Use This Skill

Use this skill when:
- User has finished implementing code changes and committed them to a branch
- User requests a PR description (e.g., "Write a PR comparing feature/caching to main")
- User is ready to open a pull request and needs documentation
- Code changes are complete and the focus shifts to communication

Do NOT use this skill when:
- Changes are not yet committed
- User is still implementing the feature
- User only wants to review their own changes (use git diff directly instead)

## Workflow

### Step 1: Gather Git Information

Start by collecting the necessary git information:

```bash
# Get current branch name
git branch --show-current

# Get the diff between branches (user will specify target branch, often 'main' or 'develop')
git diff <target-branch>...HEAD

# Get commit history for the branch
git log <target-branch>..HEAD --oneline

# Get more detailed commit messages if needed
git log <target-branch>..HEAD --format="%h %s%n%b"
```

**Important**: Pay attention to the conversation context. The user may have discussed:
- Why they made these changes
- What problem they were solving
- Business or technical justification
- Known limitations or future work

This context is critical for the Rationale section.

### Step 2: Analyze the Changes

Review the git diff and identify:
1. **Primary category**: Is this a bug fix, feature, refactor, optimization, etc?
2. **Scope**: What areas of the codebase changed (frontend, backend, database, tests)?
3. **Key changes**: What are the 3-7 most significant changes at a high level?
4. **Breaking changes**: Are there any changes that require action from other developers?
5. **New dependencies**: Were any new libraries or services added?
6. **Testing**: Are there new or updated tests visible in the diff?

### Step 3: Structure the PR Description

Draft a PR description using the standard structure defined in `references/pr-structure-guide.md`. The structure consists of:

1. **Title**: Short, action-oriented (50 chars or less when possible)
2. **Type**: Category of change (Bug Fix, Feature, Optimization, etc.)
3. **Rationale**: WHY these changes are necessary (most important section)
4. **Changes**: Bulleted list of WHAT changed at a high level
5. **Testing**: How changes were validated
6. **Notes**: Additional context (related issues, follow-up work, deployment notes)

Load the detailed guide when needed:
```
Read references/pr-structure-guide.md for comprehensive formatting standards, examples, and quality guidelines.
```

### Step 4: Write the Description

Key principles:
- **Emphasize WHY over HOW**: Focus on rationale and impact, not implementation details
- **Be specific**: Use concrete metrics and examples
- **Mark breaking changes clearly**: Use ⚠️ BREAKING: prefix
- **Keep it concise**: 200-300 words for standard PRs, 300-500 for complex changes
- **Use present tense**: "Add caching layer" not "Added caching layer"
- **Group related changes**: Don't list every file, group by logical area

### Step 5: Output the PR Description

**CRITICAL**: Output the complete PR description to the user as formatted markdown. Do NOT keep the description internal.

Present it in a code block for easy copying:

````
Here's the PR description for your changes:

```markdown
# [Title]

Type: [Type]

## Rationale

[Rationale content]

## Changes

- [Change 1]
- [Change 2]
- [Change 3]

## Testing

[Testing information]

## Notes

[Additional notes]
```
````

After outputting, offer to:
1. Refine the description based on feedback
2. Create the PR directly using `gh pr create` if the user wants
3. Add more detail to any section

## Tips for Quality PR Descriptions

1. **Start with conversation context**: Before looking at the diff, review what the user said about why they made these changes
2. **Ask clarifying questions**: If the rationale isn't clear from context or diff, ask the user
3. **Read commit messages**: They often contain valuable context about the changes
4. **Identify the story**: Every PR tells a story (problem → solution → impact)
5. **Highlight risks**: Call out areas that need careful review
6. **Be honest about limitations**: Mention known issues or follow-up work

## Common Patterns

### Bug Fix PR
- Rationale focuses on symptoms users experienced and root cause
- Changes describe the fix at a high level
- Testing emphasizes regression prevention

### Feature PR
- Rationale explains the user need or business opportunity
- Changes list new capabilities added
- Testing covers happy path and edge cases
- Notes often include feature flag info or rollout strategy

### Refactor PR
- Rationale justifies why refactoring was needed (maintainability, performance, etc.)
- Changes describe structural improvements
- Testing emphasizes no behavior changes
- Notes may warn about merge conflicts or suggest coordination

### Optimization PR
- Rationale includes current performance metrics and targets
- Changes describe optimizations at a high level
- Testing includes benchmarks and performance measurements
- Notes may cover trade-offs (e.g., memory vs. speed)

## Example Invocations

**User:** "Write a PR description comparing feature/caching to main"

**Response:**
1. Run `git diff main...HEAD` to see changes
2. Run `git log main..HEAD --oneline` to see commits
3. Review conversation context about why caching was added
4. Draft PR description following structure
5. **Output the complete description to the user**

**User:** "The memory leak fix is ready on bugfix/memory-leak. Draft a PR comparing it to develop"

**Response:**
1. Run `git diff develop...HEAD` to see the fix
2. Review conversation about the memory leak symptoms and diagnosis
3. Focus rationale on user impact (crashes, slowdowns) and root cause
4. List key changes (e.g., "Add connection cleanup in error paths")
5. **Output the complete description to the user**

## References

- `references/pr-structure-guide.md` - Comprehensive guide to PR description structure, formatting, examples, and quality standards
