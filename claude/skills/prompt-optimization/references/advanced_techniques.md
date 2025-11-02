# Advanced Prompt Engineering Techniques

This document provides detailed guidance on research-backed advanced techniques that go beyond Anthropic's foundational patterns. These techniques should be applied **selectively** based on task requirements.

---

## Selective Chain-of-Thought (Cost-Aware Reasoning)

### When to Use

**Good candidates:**
- Complex multi-step problems requiring stepwise logic
- Math word problems and logical puzzles
- Tasks with non-obvious intermediate steps
- Problems where reasoning path affects accuracy

**Poor candidates:**
- Simple factual queries
- Already clear, straightforward tasks
- Situations where brevity matters
- Tasks where the model already reasons effectively by default

### Rationale

Recent 2025 research shows CoT can waste 20-80% more tokens and sometimes **decreases accuracy** on simple tasks. Modern LLMs often perform reasoning by default; explicit CoT may be redundant for straightforward queries.

### Implementation

**Good - Complex reasoning benefits from CoT:**
```
<thinking>
Step 1: Parse the constraint (sister was half my age when I was 6 = she was 3)
Step 2: Calculate age difference (6 - 3 = 3 years)
Step 3: Apply to current age (70 - 3 = 67)
</thinking>
Answer: Sister is 67
```

**Bad - Simple query doesn't need CoT (wastes tokens):**
```
Question: What is the capital of France?
<thinking>
Let me think through this... France is a country... capitals are important cities...
I recall Paris is the capital...
</thinking>
Answer: Paris
```

### Cost Impact

- **+20-80% tokens** depending on problem complexity
- Only worth it when reasoning improves accuracy significantly

---

## Persona-as-Cognition

### Purpose

Assign roles that change **thinking style**, not just tone. Different personas affect reasoning depth, creativity, and analytical approach.

### Cognition-Changing Personas

**Skeptical Methodologist**
- Questions assumptions
- Demands evidence
- Catches logical flaws
- **Use for:** Critical analysis, research evaluation, design review

**Careful Proofreader**
- Detail-oriented
- Slow and thorough
- Catches typos and inconsistencies
- **Use for:** Document review, code auditing, quality control

**Creative Brainstormer**
- Fast, divergent thinking
- Generates many ideas
- Explores unusual connections
- **Use for:** Ideation, problem-solving, alternative approaches

**Devil's Advocate**
- Actively seeks counter-arguments
- Identifies edge cases
- Challenges assumptions
- **Use for:** Risk analysis, decision evaluation, testing ideas

**Empathetic Counselor**
- Considers emotional and human factors
- Collaborative approach
- Values relationships and context
- **Use for:** User experience, team dynamics, stakeholder communication

### Rationale

2025 personality research shows different personas affect reasoning depth and style:
- "Introverted" personas produce longer, more reflective outputs
- "Analytical" personas are more utilitarian and focused
- "Creative" personas explore more alternatives

Use personas strategically to match the cognitive style needed.

### Implementation

```
You are a Skeptical Methodologist reviewing this experimental design.
Question every assumption. Demand evidence. Point out potential confounds.

[This produces more critical, rigorous analysis than a neutral persona]
```

### Cost Impact

- **Minimal** - mainly affects output style and depth
- May increase output length for reflective personas

---

## Self-Consistency (Ensemble Reasoning)

### When to Use

**Appropriate scenarios:**
- High-stakes decisions with significant consequences
- Math problems where single reasoning path might fail
- Complex logical puzzles with multiple solution approaches
- Situations where you need confidence in the answer

**Not worth it:**
- Simple queries with obvious answers
- Time-sensitive tasks
- Low-stakes decisions
- When one reasoning approach is clearly sufficient

### How It Works

Generate 3-5 independent reasoning paths, then vote on the most consistent answer. This catches errors that a single reasoning path might miss.

### Implementation Structure

```
Generate 3 independent solutions to this problem with different reasoning approaches:

<solution_1>
[Approach: Work backwards from the goal]
Answer: X
</solution_1>

<solution_2>
[Approach: Use algebraic substitution]
Answer: X
</solution_2>

<solution_3>
[Approach: Guess and verify]
Answer: Y
</solution_3>

<final_answer>
Votes: X appears in 2/3 solutions
Most consistent answer: X
Confidence: High (majority agreement)
</final_answer>
```

### Cost Impact

- **3-5x token usage** - one of the most expensive techniques
- Only use when accuracy is absolutely critical

---

## Multi-Agent Debate

### When to Use

**Good scenarios:**
- Complex decisions with trade-offs
- Argument mining and reasoning
- Catching blind spots and biases
- Need to examine problem from multiple angles
- Evaluating controversial or nuanced topics

**Avoid when:**
- Simple yes/no questions
- Clear-cut technical issues
- Time-constrained situations
- Cost is a major concern

### How It Works

Model plays multiple personas debating/critiquing each other. This "society of minds" approach reduces confirmation bias and catches reasoning errors that a single perspective would miss.

### Implementation Structure

```
<debate>
<optimist>
Approach X is superior because:
- [Benefit 1]: Improved scalability
- [Benefit 2]: Better developer experience
- [Benefit 3]: Lower maintenance cost
</optimist>

<skeptic>
I disagree. Approach X has critical flaws:
- [Flaw 1]: Hidden operational complexity
- [Flaw 2]: Vendor lock-in risk
- [Flaw 3]: Steep learning curve
Consider alternative Y which addresses these concerns.
</skeptic>

<optimist_rebuttal>
Those concerns are valid but can be addressed:
- [Response 1]: Use abstraction layer to avoid lock-in
- [Response 2]: Training program reduces learning curve
- [Response 3]: Operational complexity pays off at scale
</optimist_rebuttal>

<synthesis>
Balanced conclusion:
- Approach X makes sense when: [specific conditions]
- Approach Y is better when: [alternative conditions]
- Key trade-offs to consider: [list]
- Recommended path: [final recommendation with caveats]
</synthesis>
</debate>
```

### Rationale

Debate format forces the model to:
- Consider opposing viewpoints
- Identify weaknesses in each position
- Synthesize a more balanced conclusion
- Surface hidden assumptions

### Cost Impact

- **2-3x token usage** - moderate expense
- Worth it for decisions with significant consequences

---

## Context Engineering (RAG Integration)

### When to Use

**Appropriate scenarios:**
- Need factual accuracy about recent events or specific documents
- Working with long documents or external knowledge
- Reducing hallucinations on specialized topics
- Grounding responses in verified sources

**Not needed:**
- General knowledge questions within training cutoff
- Creative tasks not requiring factual accuracy
- Simple queries not needing external context

### How It Works

Structure prompts to explicitly ground the model with retrieved facts from external sources. This separates what the model knows from what it should use.

### Implementation

```
Using ONLY the following background information, answer the question:

<retrieved_context>
[Relevant passages from external sources]
Source: [Citation]
Date: [When information was published]
</retrieved_context>

<question>
[User's query]
</question>

Instructions:
- Cite which part of the context you used
- If the context doesn't contain the answer, say so explicitly
- Do not use information outside the provided context
```

### Best Practices

1. **Explicit boundaries** - Make it clear to use ONLY provided context
2. **Source tracking** - Include citations so model can reference them
3. **Fallback handling** - Instruct what to do when context is insufficient
4. **Recency markers** - Include dates to help model assess relevance

### Cost Impact

- **Minimal direct cost** - mainly just the context length
- May save tokens by preventing unnecessary reasoning

---

## When NOT to Use Advanced Techniques

### Important Limitations

| Technique | Primary Limitation | When to Avoid |
|-----------|-------------------|---------------|
| **Self-Consistency** | 3-5x token cost | Simple queries, low-stakes decisions |
| **Multi-Agent Debate** | Slow and verbose | Time-sensitive tasks, clear-cut issues |
| **Chain-of-Thought** | 20-80% token overhead | Simple factual queries, already-clear tasks |
| **Persona Shifts** | Introduces variance | When consistency is critical |
| **Context Engineering** | Only helps with external facts | General knowledge questions |

### Rule of Thumb

**Start with foundational patterns:**
1. Role assignment
2. XML tags for structure
3. Few-shot examples
4. Output format specification

**Only add advanced techniques** when:
- Task genuinely requires them
- Benefits outweigh token costs
- Simpler approaches have failed
- Accuracy is more important than speed/cost

---

## Combining Techniques

Advanced techniques can be combined when appropriate:

```
You are a Skeptical Methodologist [Persona-as-Cognition]
reviewing this system architecture design.

<retrieved_context>
[Recent documentation, research papers]
</retrieved_context>

<debate>
[Multi-agent debate between perspectives]
</debate>

For each position in the debate, provide step-by-step reasoning:
<thinking>
[Chain-of-thought for complex analysis]
</thinking>
```

**Warning:** Combining techniques multiplies token costs. Only do this for truly critical decisions.

---

## Summary Decision Matrix

| Task Type | Recommended Techniques | Estimated Cost |
|-----------|----------------------|----------------|
| Simple factual query | Foundational only | 1x |
| Complex reasoning | Foundational + CoT | 1.5-2x |
| High-stakes decision | Foundational + Self-Consistency | 3-5x |
| Multi-faceted problem | Foundational + Multi-Agent Debate | 2-3x |
| Specialized domain | Foundational + Context Engineering | 1.2-1.5x |
| Critical architecture | All techniques combined | 5-10x |

**Always start simple and add complexity only when needed.**
