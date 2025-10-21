---
description: "Create a pull request description by analyzing git branch differences"
argumentHint: "[source-branch] [target-branch] (optional: additional context)"
---

# Draft Pull Request Description

I'll analyze the git changes and create a comprehensive PR description.

## Gathering Information

Comparing: $ARGUMENTS (or current branch to main if not specified)

Using the **pr-description-writer** agent to:
- Examine git diff between branches
- Incorporate conversation context about changes
- Categorize the type of change (feature, bugfix, refactor, etc.)
- Create a structured PR description with rationale, changes, and testing notes

{Launching pr-description-writer agent via Task tool}
