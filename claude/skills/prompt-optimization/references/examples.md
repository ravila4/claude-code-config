# Prompt Optimization Examples

Before/after examples showing when to add structure and when to keep it simple.

---

## Simple → Simple (No Structure Needed)

These examples show restraint. Not every prompt needs XML tags or elaborate structure.

### Example: Factual Query

**Before:**
```
what's the difference between a list and tuple in python
```

**After:**
```
Explain the difference between a list and tuple in Python. Include when to use each.
```

**Why no structure?** Clear question, single topic. Adding tags would be noise.

---

### Example: Error Explanation

**Before:**
```
what does this error mean: TypeError: 'NoneType' object is not subscriptable
```

**After:**
```
Explain this Python error and how to fix it: TypeError: 'NoneType' object is not subscriptable

Include a code example showing both the problem and the solution.
```

**Why no structure?** The error message is self-contained. We just added clarity about what output we want.

---

### Example: Simple How-To

**Before:**
```
how do i read a csv in python
```

**After:**
```
Show how to read a CSV file in Python using pandas. Include handling for common issues like missing values and encoding.
```

**Why no structure?** Straightforward request. The additions are just specificity, not structure.

---

## Moderate Complexity (Light Structure)

These examples benefit from some organization but don't need heavy XML tagging.

### Example: Code Review Request

**Before:**
```
review this code
```

**After:**
```
You are a senior Python code reviewer.

Review the following code for:
- Correctness and potential bugs
- Readability and maintainability
- Performance issues
- Security vulnerabilities

Structure your review as:
- **Critical Issues** (must fix)
- **Suggestions** (should consider)
- **Positive Observations** (what the code does well)

[Code will be provided]
```

**Why this level of structure?**
- Role assignment helps set expertise level
- Bullet points organize review criteria
- Output format ensures consistent, useful feedback
- But no XML tags - markdown bullets suffice

---

### Example: Debugging Request

**Before:**
```
my code is broken help
```

**After:**
```
You are a Python debugging expert.

Debug the following code:
1. Identify what's going wrong
2. Explain why the bug occurs
3. Provide the corrected code
4. Suggest how to prevent similar bugs

If the code isn't provided, ask for:
- The code
- Expected vs actual behavior
- Any error messages
```

**Why this level of structure?**
- Role assignment appropriate for expertise task
- Numbered steps ensure complete debugging
- Escape hatch handles missing information
- No XML needed - natural language is clear

---

## Complex Tasks (Structure Justified)

These examples genuinely benefit from XML/JSON structure because they have distinct sections or need clear boundaries.

### Example: Architecture Decision

**Before:**
```
should we use GraphQL or REST
```

**After:**
```
You are a senior API architect evaluating API design decisions.

<context>
Team is choosing between GraphQL and REST for a new API.
- Microservices architecture
- Multiple clients (web, mobile, IoT)
- Team experienced with REST, minimal GraphQL exposure
</context>

<task>
Analyze using a multi-perspective approach:

1. **GraphQL case**: Flexible querying, strong typing, single endpoint
2. **REST case**: Simplicity, caching, wider tooling support
3. **Hidden costs**: What risks aren't immediately obvious?
4. **Recommendation**: Based on team constraints and use case
</task>

Include specific conditions under which each choice makes sense.
```

**Why structure here?**
- Context section separates background from the actual task
- Task section clearly delineates what analysis is needed
- Multiple perspectives require clear organization
- This is a high-stakes decision worth the extra structure

---

### Example: Data Analysis with Specific Output

**Before:**
```
analyze this dataset
```

**After:**
```
You are a data scientist specializing in exploratory data analysis.

<dataset_context>
Domain: E-commerce customer behavior
Goal: Identify customer segments for targeted marketing
</dataset_context>

<analysis_requirements>
1. **Data Quality**: Missing values, duplicates, outliers
2. **Key Statistics**: Distribution of purchase amounts, frequency patterns
3. **Insights**: Customer segments, seasonal patterns
4. **Recommendations**: Specific actions based on findings
</analysis_requirements>

Respond in this format:
```json
{
  "data_quality": {...},
  "key_findings": [...],
  "segments_identified": [...],
  "recommended_actions": [...]
}
```
```

**Why structure here?**
- Context section grounds the analysis in business purpose
- Requirements section ensures comprehensive coverage
- JSON output format makes results parseable and actionable
- Complex enough task to warrant the overhead

---

### Example: Multi-Step Workflow

**Before:**
```
help me set up authentication
```

**After:**
```
You are a senior full-stack developer implementing authentication.

<clarification_needed>
Before implementing, I need to understand:

1. **Auth method**: JWT tokens, session-based, OAuth, or email/password?
2. **Scope**: Backend only, or frontend integration too?
3. **Features**: Password reset? Two-factor? Rate limiting?
</clarification_needed>

<once_clarified>
Provide:
1. Recommended approach with rationale
2. Step-by-step implementation plan
3. Security considerations
4. Example code for the chosen approach
</once_clarified>

Please ask for clarification on the above before proceeding.
```

**Why structure here?**
- This is an ambiguous request that needs clarification
- XML sections separate "what I need to know" from "what I'll deliver"
- Prevents wasted effort implementing the wrong auth approach
- The structure surfaces hidden requirements

---

## When NOT to Add Structure

Common over-engineering patterns to avoid:

**Don't do this:**
```
<context>
The user wants to know what time it is.
</context>

<task>
Tell the user the current time.
</task>

<output_format>
Provide the time in HH:MM format.
</output_format>
```

**Do this instead:**
```
What time is it?
```

**The principle:** If the original prompt is already clear, don't add ceremony. Structure should solve a problem, not demonstrate thoroughness.

---

## Quick Decision Guide

| Request Type | Structure Needed? | Why |
|--------------|-------------------|-----|
| Factual query | No | Already clear |
| Simple how-to | No | Just add specificity |
| Code review | Light (bullets) | Organize criteria |
| Debugging | Light (steps) | Ensure completeness |
| Architecture decision | Yes (XML) | Separate context/task |
| Ambiguous request | Yes (XML) | Surface requirements |
| Parseable output needed | Yes (JSON) | Machine-readable |

---

**Remember:** The goal is effective prompts, not elaborate prompts.
