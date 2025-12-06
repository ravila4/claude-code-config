---
name: prompt-optimization
description: Use when crafting prompts for external LLMs (Gemini, Codex), sub-agents, MCP tools (like deepwiki), or when user requests help optimizing a prompt. Emphasizes matching complexity to task - simple requests stay simple.
---

# Prompt Optimization

## Overview

Transform rough prompts into effective prompts. The core principle: **match complexity to the task**. Simple requests should produce simple prompts. Only add structure when it genuinely improves output.

## Workflow

See `references/workflow.gv` for the visual decision flow.

**Quick summary:**
1. Is the intent clear? If not, extract the core intent first
2. Is this a simple request? If yes, minor cleanup only
3. Would structure help? Only add it if there's clear benefit
4. Does it need multi-step reasoning? Consider chain-of-thought
5. Is it high-stakes? Consider advanced techniques

## Core Principle: Simplicity First

**Not every prompt needs structure.** Before adding XML tags, JSON formatting, or advanced techniques, ask:

> "Does this complexity genuinely improve the output, or am I adding noise?"

### Keep It Simple When

- **Factual queries**: "What's the capital of France?" → Leave as-is
- **Single-purpose requests**: "Explain this error message" → Add context, not structure
- **Conversational prompts**: Natural language flows fine
- **Clear intent**: The request is already unambiguous

### Add Structure When

- **Separating user data from instructions**: Prevents prompt injection, clarifies boundaries
- **Multi-part output needed**: Analysis + code + explanation benefits from sections
- **Few-shot examples**: Multiple input/output pairs need clear delineation
- **Ambiguous boundaries**: Where does the user's content end and instructions begin?

## Foundational Patterns

### 1. Clear and Direct Communication

- State intentions explicitly
- Be specific about requirements
- Remove ambiguity

### 2. Role Assignment

Assign a specific role when expertise matters:

```
You are a senior Python developer with expertise in pandas...
```

### 3. Structuring Techniques (Use Sparingly)

Structure helps when you need clear boundaries. Choose the format that fits:

**XML tags** - Good for separating sections in prompts:
```
<context>
Background information here.
</context>

<task>
What to do with it.
</task>
```

**JSON** - Good for structured data or when output will be parsed:
```
Respond in JSON format:
{
  "analysis": "your analysis",
  "recommendation": "your recommendation",
  "confidence": "high/medium/low"
}
```

**Markdown** - Good for human-readable structure:
```
## Context
Background information here.

## Task
What to do with it.
```

**When to skip structure entirely:**
- The prompt is short and clear
- Natural language conveys the same information
- Adding tags would just be noise

### 4. Few-Shot Prompting

Examples are highly effective for showing desired behavior. Structure helps here because you're delineating multiple input/output pairs:

```
Example 1:
Input: "make it faster"
Output: "Optimize this code for performance, focusing on time complexity and memory usage."

Example 2:
Input: "it's broken"
Output: "Debug this code. Describe the error, identify the root cause, and provide a fix."
```

### 5. Output Formatting

Specify response structure when you need consistent output:

```
Provide:
1. Root cause analysis
2. Corrected code
3. Brief explanation
```

Or for structured data:
```
Respond as JSON with keys: "cause", "fix", "explanation"
```

### 6. Escape Hatches

Include fallback instructions for edge cases:

```
If the question is unclear, ask for clarification.
If you can't determine the answer, say so explicitly.
```

## Advanced Techniques

These are **optional** and cost tokens. Only apply when specifically beneficial. See `references/advanced_techniques.md` for detailed guidance.

| Technique | When to Use | Cost Impact |
|-----------|-------------|-------------|
| **Chain-of-Thought** | Multi-step reasoning, logic puzzles | +20-80% tokens |
| **Persona-as-Cognition** | Need specific thinking style | Minimal |
| **Self-Consistency** | High-stakes decisions, math | 3-5x tokens |
| **Multi-Agent Debate** | Complex decisions, catching bias | 2-3x tokens |

**Rule of thumb:** Start simple. Only add advanced techniques when simpler approaches fail or stakes justify the cost.

## Example Transformations

### Simple → Simple

**Before:**
```
what causes a KeyError in python
```

**After:**
```
Explain what causes a KeyError in Python and how to prevent it. Include a brief code example.
```

*Why no structure?* The request is clear and single-purpose. Adding XML would be noise.

---

### Moderate Complexity

**Before:**
```
my code is slow can you help
```

**After:**
```
You are a Python performance expert.

I have code that's running slowly. Analyze it for:
- Time complexity issues
- Unnecessary operations
- Memory allocation patterns
- Caching opportunities

Provide the optimized code with a brief explanation of what you changed and why.

[Code will be provided]
```

*Why this structure?* Role assignment helps, bullet points organize the analysis criteria, but no XML needed.

---

### Complex Task (Structure Justified)

**Before:**
```
help me decide if we should use microservices or monolith
```

**After:**
```
You are a senior software architect evaluating architecture decisions.

<context>
Team is deciding between microservices and monolith for a new application.
</context>

<task>
Analyze from multiple perspectives:

1. **Microservices case**: Scalability, independent deployment, technology flexibility
2. **Monolith case**: Simplicity, consistency, lower operational overhead
3. **Hidden costs**: Risks of each that aren't immediately obvious
4. **Recommendation**: Based on typical team constraints (size, experience, timeline)
</task>

Include specific conditions under which each choice makes sense.
```

*Why structure here?* The task has multiple distinct parts. XML separates context from task.

---

See `references/examples.md` for additional transformations.

## Resources

- `references/workflow.gv` - Visual decision flow (Graphviz)
- `references/advanced_techniques.md` - Chain-of-thought, persona-as-cognition, self-consistency, multi-agent debate
- `references/examples.md` - Additional example transformations

---

**Remember:** The goal is effective prompts, not elaborate prompts. Simple and clear beats complex and thorough when the task is straightforward.
