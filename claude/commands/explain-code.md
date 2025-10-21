---
description: "Comprehensive code explanation with optional diagrams and vault storage"
argumentHint: "[file path or code snippet] (optional: --diagram, --save)"
---

# Code Explanation Request

Explaining code: $ARGUMENTS

I'll use the **code-explainer** agent to provide a comprehensive explanation.

## The agent will:

- Analyze code structure, control flow, and design patterns
- Provide multi-level explanations (high-level → detailed)
- Generate visual diagrams via **mermaid-expert** for complex flows (if requested or beneficial)
- Save explanations to your Obsidian vault via **obsidian-vault-manager** (if --save flag)
- Track patterns via **memory-knowledge-keeper** for future context

## Analysis includes:

- Summary and key components
- Control flow and data flow
- Design patterns and principles
- Edge cases and error handling
- Potential improvements

{Launching code-explainer agent via Task tool}
