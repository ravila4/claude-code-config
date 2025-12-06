---
description: Draft, organize, or update development journal entries
---

# Journal Command

Help manage development journal entries with flexible workflows.

## What to Do

When the user invokes `/journal`, check what they need help with by asking:

**If no subcommand specified:**
Use AskUserQuestion to ask what they want to do:
- Draft new journal entry for today
- Organize existing raw/unstructured content
- Append content to specific section
- Review current journal and suggest improvements

**If context is unclear:**
Ask clarifying questions:
- Which date? (if not today)
- Which section to append to? (if appending)
- Full or minimal journal? (if drafting)
- What content should be included? (if appending)

## Subcommands

### `/journal draft`
Generate complete journal entry from today's activity.

**Actions:**
1. Invoke dev-journaling skill
2. Run `draft_journal_entry.py --mode auto`
3. Show the complete markdown draft
4. Ask if user wants to write it to Obsidian vault

**Best for:** End of day journal generation

### `/journal organize`
Organize raw/unstructured content in today's journal.

**Actions:**
1. Read today's journal from `~/Documents/Obsidian-Notes/Daily Log/YYYY-MM-DD.md`
2. Detect if it's unstructured (no headers, mostly code blocks)
3. Extract commands, outputs, and notes
4. Organize into structured sections
5. Show organized version for approval
6. Update the file if approved

**Best for:** When raw commands/notes need structure

### `/journal append [section]`
Add content to a specific section of today's journal.

**Actions:**
1. Extract relevant content from current conversation
2. Format it for the requested section
3. Show what will be appended
4. Update the journal file if approved

**Section options:** context, commands, reflection, questions, commits

**Best for:** Incremental journaling throughout the day

### `/journal review`
Show current state of today's journal with improvement suggestions.

**Actions:**
1. Read today's journal
2. Analyze completeness (missing sections, empty placeholders)
3. Suggest improvements based on today's conversations
4. Ask if user wants to fill gaps

**Best for:** Quick check before ending the day

## Integration

This command integrates with:
- **dev-journaling skill**: For draft generation and section logic
- **obsidian-vault-manager skill**: For reading/writing journal files
- **Current conversation**: For extracting relevant content to append
