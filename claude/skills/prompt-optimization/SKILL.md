---
name: prompt-optimization
description: Transform rough prompts into polished, effective prompts using Anthropic's prompt engineering best practices. Use when refining prompts for clarity, adding structure with XML tags, implementing few-shot examples, or applying advanced techniques like chain-of-thought reasoning. Ideal for improving prompts before sending to other agents or LLMs.
---

# Prompt Optimization

## Overview

This skill provides comprehensive knowledge of Anthropic's prompt engineering best practices and research-backed advanced techniques. Use it to transform informal requests into well-structured, effective prompts that produce better results from LLMs.

## Core Mission

**Transform human ramblings into polished, effective prompts** using Anthropic's prompt engineering patterns. Take rough, informal requests and distill them into well-structured prompts that get better results.

## When to Use This Skill

- Refining user requests before sending to external LLMs (Gemini, GPT-5, Codex)
- Converting informal requirements into structured prompts
- Adding examples to improve task-specific behavior
- Structuring complex prompts with proper XML organization
- Applying advanced reasoning techniques for complex tasks
- Chaining prompts with target agents (e.g., "optimize then ask gemini")

## Workflow Decision Tree

```
User provides rough prompt
    ↓
Is this a simple factual query?
    → YES: Apply foundational patterns only (role, XML tags, output format)
    → NO: Continue to complexity assessment
        ↓
    Does it require multi-step reasoning?
        → YES: Consider chain-of-thought (cost-aware)
        → NO: Skip CoT
            ↓
    Would examples improve output?
        → YES: Add few-shot examples (most effective pattern)
        → NO: Continue
            ↓
    Are there edge cases or ambiguity?
        → YES: Add escape hatches, clarify constraints
        → NO: Continue
            ↓
    Is this a critical/high-stakes decision?
        → YES: Consider self-consistency or multi-agent debate
        → NO: Stick with foundational patterns
            ↓
    Apply final structure:
        1. Role assignment
        2. Task context (early)
        3. XML-tagged data/instructions
        4. Examples (middle)
        5. Input data
        6. Output format (near end)
```

## Foundational Patterns

These patterns should be considered for **every** prompt optimization.

### 1. Clear and Direct Communication

- State intentions explicitly
- Avoid relying on implicit understanding
- Be specific about requirements

### 2. Role Assignment

Assign Claude a specific role or persona when appropriate.

**Example:**
```
You are a senior Python developer with expertise in data processing...
```

### 3. XML Tag Structure

Use XML tags to separate data from instructions. This keeps structure clear and prevents confusion.

**Common tags:**
- `<example>` - For few-shot examples
- `<question>` - User queries
- `<context>` - Background information
- `<document>` - Source material
- `<task>` - Task description
- `<code>` - Code samples

**Example:**
```
<context>
A pandas DataFrame is producing unexpected NaN values.
</context>

<task>
Identify why NaN values appear and provide corrected code.
</task>

<code>
df = df[df['column'] > 0]
</code>
```

### 4. Few-Shot Prompting ⭐ Most Effective

Add examples enclosed in `<example></example>` tags. This is **"probably the single most effective tool"** for desired behavior.

**Best practices:**
- More examples = better results
- Include edge cases
- Show desired output format
- Cover common variations

**Example:**
```
<example>
Input: "uh so I need to filter this list"
Optimized: "Filter the following list to include only items matching the condition: [specific condition]"
</example>

<example>
Input: "make it faster"
Optimized: "Optimize the following code for performance. Focus on reducing time complexity and minimizing memory allocation."
</example>
```

### 5. Output Formatting

Specify exact response structure using XML tags or clear instructions.

**Example:**
```
Please provide:
1. Root cause analysis in <analysis> tags
2. Corrected code in <solution> tags
3. Brief explanation in <explanation> tags
```

### 6. Escape Hatches

Include instructions for when Claude is unsure or encounters edge cases.

**Example:**
```
If the question is unclear, ask for clarification rather than making assumptions.
If the context doesn't contain the answer, say so explicitly.
```

### 7. Complex Prompt Structure (Optimal Ordering)

For complex prompts, apply elements in this order:

1. **Task context** (early) - Background information
2. **Tone context** (if needed) - Desired style/formality
3. **Detailed task description and rules** - Core requirements
4. **Examples** (middle) - Few-shot examples
5. **Input data** - User's actual query/data with XML tags
6. **Immediate task description** (near end) - Restate the task
7. **Precognition instructions** (near end) - "Think step-by-step first"
8. **Output formatting** (near end) - Structure for response

**Critical principle:** Place the user's query close to the bottom of long prompts.

## Advanced Techniques

These patterns are **optional** and should only be applied when specifically beneficial. See `references/advanced_techniques.md` for detailed guidance.

### Quick Reference

| Technique | When to Use | Cost Impact | Key Benefit |
|-----------|-------------|-------------|-------------|
| **Chain-of-Thought** | Multi-step reasoning, logic puzzles | +20-80% tokens | Improves accuracy on complex reasoning |
| **Persona-as-Cognition** | Need specific thinking style | Minimal | Changes reasoning depth/approach |
| **Self-Consistency** | High-stakes decisions, math | 3-5x tokens | Higher confidence answers |
| **Multi-Agent Debate** | Complex decisions, catching bias | 2-3x tokens | Examines multiple perspectives |
| **Context Engineering** | Factual accuracy, recent events | Minimal | Reduces hallucinations |

**Rule of thumb:** Start with foundational patterns. Only add advanced techniques when the task genuinely requires them.

## Example Transformations

### Simple Query (Foundational Only)

**Before:**
```
uh so I have this DataFrame and it's got some weird NaN values
```

**After:**
```
You are a senior Python data engineer debugging pandas DataFrame issues.

<context>
A pandas DataFrame is producing unexpected NaN values after filtering operations.
</context>

<task>
Analyze the following DataFrame code and identify why NaN values are appearing. Consider common causes like:
- Chained indexing creating copies
- Type coercion issues
- Missing value propagation
- Index misalignment
</task>

<code>
[User's code would go here]
</code>

Please provide:
1. Root cause of the NaN values
2. Corrected code
3. Explanation of the fix

If the code is not provided, ask for specific details about the DataFrame operations.
```

### Complex Query (With Advanced Techniques)

**Before:**
```
help me decide if we should use microservices or monolith
```

**After:**
```
You are a senior software architect evaluating architecture decisions.

<context>
A team is deciding between microservices and monolith architecture for a new application.
</context>

<task>
Analyze this decision from multiple perspectives using a debate format.
</task>

<debate>
<microservices_advocate>
Present the strongest case for microservices, including scalability, independent deployment, and technology flexibility.
</microservices_advocate>

<monolith_advocate>
Present the strongest case for a monolith, including simplicity, consistency, and lower operational overhead.
</monolith_advocate>

<skeptic>
Challenge both positions. What are the hidden costs and risks of each approach?
</skeptic>

<synthesis>
Provide a balanced recommendation based on:
- Team size and experience
- Expected scale and growth
- Operational maturity
- Time to market constraints
</synthesis>
</debate>

Include specific trade-offs and conditions under which each choice makes sense.
```

## Resources

This skill includes:

### references/

- `advanced_techniques.md` - Detailed guidance on chain-of-thought, persona-as-cognition, self-consistency, multi-agent debate, and context engineering
- `examples.md` - Additional example transformations covering common scenarios

See the [references directory](references/) for comprehensive documentation.

---

**Note:** This skill focuses on **prompt structure and technique**. For LLM-specific integration and caching, see the consultant agents (gemini-consultant, gpt5-consultant, codex-consultant).
