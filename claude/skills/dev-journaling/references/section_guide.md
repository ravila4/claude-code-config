# Section Population Guide

## Contents
- [Always Include](#always-include)
- [Conditionally Include](#conditionally-include)
- [Section Decision Logic](#section-decision-logic)

When generating journal drafts, use this guide to determine which sections to include:

## Always Include

**Date (H1):** `# YYYY-MM-DD`
**YAML frontmatter:** date and tags
**Goals/Todo:** From TodoWrite or early user messages - checkbox format

## Conditionally Include

**Project Wikilink:** Only if clear project focus detected (e.g., "plink", "manifest")

- Format: `Working on [[Project Name]]`

**Context:** Include if:

- Day had clear driving question or problem
- First user messages provide meaningful context (not just "help me debug X")
- Skip if day was purely operational or scattered

**Technical Work:** Include if:

- Git commits exist for the day
- Files were modified (Edit/Write tools used)
- At least one substantial action taken

**Commands Used:** Include if:

- 3+ significant bash commands run
- Exclude trivial commands (ls, cat, cd)
- Format as code block with optional descriptions

**Open Questions:** Include if:

- Unresolved issues mentioned
- Questions posed by user or Claude
- Uncertainties or "not sure" statements found
- Limit to 5 most significant

**Reflection:** Include for deep work days

- Skip for operational/debugging days
- Use placeholder text in full mode
- Omit in quick/auto mode unless substantial

**Next Steps:** Include if:

- Clear follow-up items identified
- Tomorrow's focus is obvious from context
- Use placeholder in full mode

## Section Decision Logic

**Auto mode (recommended):**

- Start with required sections
- Add conditional sections only if they have content
- Result: Clean, relevant journal without empty sections

**Full mode:**

- Include all sections
- Add placeholders for manual completion
- Best for deep work days needing reflection

**Quick mode:**

- Only: Date, YAML, Goals, Git Commits, Files
- Minimal structure for operational days
