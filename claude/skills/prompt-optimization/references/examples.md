# Prompt Optimization Examples

This document provides concrete before/after examples covering common scenarios.

---

## Contents

- [Example 1: Vague Technical Request](#example-1-vague-technical-request)
- [Example 2: Ambiguous Feature Request](#example-2-ambiguous-feature-request)
- [Example 3: Research Request with Examples](#example-3-research-request-with-examples)
- [Example 4: Code Review Request with Few-Shot](#example-4-code-review-request-with-few-shot)
- [Example 5: Decision Request with Multi-Agent Debate](#example-5-decision-request-with-multi-agent-debate)
- [Example 6: Data Analysis with Context Engineering](#example-6-data-analysis-with-context-engineering)
- [Data Quality Assessment](#data-quality-assessment)
- [Key Statistics](#key-statistics)
- [Visualizations](#visualizations)
- [Insights](#insights)
- [Next Steps](#next-steps)
- [Example 7: Chaining with Target Agent](#example-7-chaining-with-target-agent)
- [Pattern Summary](#pattern-summary)
- [Quick Transformation Checklist](#quick-transformation-checklist)

## Example 1: Vague Technical Request

### Before
```
my code is slow can you help
```

### After
```
You are a performance optimization expert specializing in Python.

<context>
Code execution time has increased significantly, impacting user experience.
</context>

<task>
Analyze the following code for performance bottlenecks and provide optimization recommendations.

Focus on:
- Time complexity analysis
- Memory allocation patterns
- Unnecessary operations
- Caching opportunities
</task>

<code>
[User's code here]
</code>

<output_format>
1. <bottleneck> - Identified performance issue
2. <impact> - Estimated performance improvement
3. <solution> - Optimized code
4. <explanation> - Why this improves performance
</output_format>

If code is not provided, request specific details about:
- What operation is slow
- Expected vs actual performance
- Input data characteristics
```

**Key improvements:**
- Role assignment (performance expert)
- Clear task structure with XML tags
- Specific analysis criteria
- Structured output format
- Escape hatch for missing information

---

## Example 2: Ambiguous Feature Request

### Before
```
add authentication to the app
```

### After
```
You are a senior full-stack developer implementing authentication.

<context>
Application currently lacks user authentication. Need to add secure login/logout functionality.
</context>

<requirements>
Before implementing, clarify the following:

1. **Authentication method:**
   - JWT tokens?
   - Session-based?
   - OAuth (Google, GitHub)?
   - Email/password?

2. **Scope:**
   - Backend API authentication only?
   - Frontend integration needed?
   - Password reset functionality?

3. **Security requirements:**
   - Password complexity rules?
   - Rate limiting?
   - Two-factor authentication?
</requirements>

<task>
Once requirements are clarified, provide:
1. Recommended authentication approach with rationale
2. Step-by-step implementation plan
3. Security considerations
4. Example code for chosen approach
</task>

Please ask for clarification on the above requirements before proceeding with implementation.
```

**Key improvements:**
- Surfaces hidden requirements
- Asks clarifying questions upfront
- Prevents wasted implementation effort
- Structured decision points
- Clear next steps after clarification

---

## Example 3: Research Request with Examples

### Before
```
what's the best way to handle errors in python
```

### After
```
You are a Python best practices expert.

<question>
What are the recommended approaches for error handling in Python?
</question>

<context>
Provide guidance suitable for production applications where:
- Errors should be logged appropriately
- Users receive helpful error messages
- System remains stable during failures
- Debugging is facilitated
</context>

<examples>
Include practical examples covering:

1. **Basic exception handling**
   - Try/except blocks
   - Multiple exception types
   - Finally clauses

2. **Custom exceptions**
   - When to create custom exception classes
   - Naming conventions
   - Exception hierarchies

3. **Logging patterns**
   - What to log vs what to raise
   - Log levels for different error types
   - Structured logging

4. **Production patterns**
   - Retry logic with exponential backoff
   - Circuit breakers
   - Graceful degradation
</examples>

<output_format>
For each pattern, provide:
- **Pattern name**
- **When to use** - Specific scenarios
- **Code example** - Working Python code
- **Pitfalls** - Common mistakes to avoid
</output_format>
```

**Key improvements:**
- Specifies context (production applications)
- Requests specific examples
- Structures output for easy reference
- Covers breadth and depth
- Includes anti-patterns

---

## Example 4: Code Review Request with Few-Shot

### Before
```
review this code
```

### After
```
You are a senior code reviewer focusing on Python best practices.

<task>
Review the following code for:
- Correctness and potential bugs
- Readability and maintainability
- Performance issues
- Security vulnerabilities
- Adherence to Python conventions (PEP 8)
</task>

<code>
[User's code here]
</code>

<output_format>
Structure your review as follows:

**Critical Issues** (must fix):
- [Issue with severity level]

**Suggestions** (should consider):
- [Improvement with rationale]

**Nitpicks** (optional):
- [Minor style improvements]

**Positive Observations**:
- [What the code does well]
</output_format>

<examples>
<example>
**Critical Issue:** Potential SQL injection vulnerability
- Line 42: User input directly interpolated into SQL query
- Severity: High
- Fix: Use parameterized queries instead
</example>

<example>
**Suggestion:** Consider using dataclass
- Lines 15-30: Class with multiple attributes and __init__
- Rationale: dataclass reduces boilerplate and adds useful methods
- Example: @dataclass would eliminate 10 lines
</example>

<example>
**Positive Observation:** Excellent docstrings
- All functions have clear docstrings with type hints
- Examples are provided for complex functions
- This greatly aids maintainability
</example>
</examples>

If code is not provided, ask for the code to review.
```

**Key improvements:**
- Clear review criteria
- Structured feedback format (critical/suggestions/nitpicks/positive)
- **Few-shot examples** showing desired review style
- Balanced feedback (includes positive observations)
- Escape hatch

---

## Example 5: Decision Request with Multi-Agent Debate

### Before
```
should we use GraphQL or REST
```

### After
```
You are a senior API architect evaluating API design decisions.

<context>
Team is choosing between GraphQL and REST for a new API.

Current system:
- Microservices architecture
- Multiple client applications (web, mobile, IoT)
- Team has experience with REST, minimal GraphQL exposure
- Performance and developer experience are priorities
</context>

<task>
Analyze this decision using a multi-perspective debate format.
</task>

<debate>
<graphql_advocate>
Present the case for GraphQL:
- Flexible querying reduces over/under-fetching
- Strong typing with schema
- Single endpoint simplifies routing
- Real-time subscriptions built-in
- Better developer experience with introspection

Provide specific examples of how GraphQL benefits this use case.
</graphql_advocate>

<rest_advocate>
Present the case for REST:
- Simpler to understand and implement
- Leverages existing team expertise
- Better caching with HTTP standards
- Wider tooling support
- Easier to version and evolve
- Lower learning curve

Provide specific examples of how REST benefits this use case.
</rest_advocate>

<realist>
Challenge both positions:
- What are the hidden costs of GraphQL (N+1 queries, complexity)?
- What are the limitations of REST (multiple round trips)?
- What does the team's current skill set mean for timeline?
- What will maintenance look like in 1-2 years?
</realist>

<synthesis>
Provide a balanced recommendation considering:
- Team capability and timeline
- Client application needs (web vs mobile vs IoT)
- Long-term maintenance
- Performance requirements
- Migration path if needed

Include specific conditions under which each choice makes sense.
</synthesis>
</debate>

<output_format>
**Recommendation:** [GraphQL/REST/Hybrid]
**Rationale:** [2-3 key deciding factors]
**Implementation Plan:** [High-level steps]
**Risks and Mitigations:** [Key risks and how to address them]
**Timeline Impact:** [Estimated effort difference]
</output_format>
```

**Key improvements:**
- Provides context about team and system
- Uses multi-agent debate for thorough analysis
- Includes realist perspective to catch hidden costs
- Synthesizes balanced recommendation
- Considers practical constraints (team skills, timeline)
- Structured output for decision-making

---

## Example 6: Data Analysis with Context Engineering

### Before
```
analyze this dataset
```

### After
```
You are a data scientist specializing in exploratory data analysis.

<task>
Perform comprehensive exploratory data analysis on the following dataset.
</task>

<dataset_context>
Domain: E-commerce customer behavior
Rows: ~50,000 customers
Key columns: customer_id, purchase_date, amount, product_category, region
Business goal: Identify customer segments for targeted marketing
</dataset_context>

<analysis_requirements>
1. **Data Quality**
   - Missing values per column
   - Duplicates
   - Outliers
   - Data type issues

2. **Descriptive Statistics**
   - Distribution of purchase amounts
   - Purchase frequency patterns
   - Category popularity
   - Regional trends

3. **Insights**
   - Customer segments (high/medium/low value)
   - Seasonal patterns
   - Category affinities
   - Regional differences

4. **Recommendations**
   - Data cleaning steps needed
   - Feature engineering opportunities
   - Potential modeling approaches
   - Business actions to consider
</analysis_requirements>

<output_format>
Structure your analysis as:

## Data Quality Assessment
[Findings and recommended cleaning steps]

## Key Statistics
[Tables and summary statistics]

## Visualizations
[Recommended plots with rationale]

## Insights
[Actionable findings for business]

## Next Steps
[Recommended analysis or modeling approaches]
</output_format>

<code>
[Dataset head/sample here]
</code>

If dataset is not provided, specify:
- Preferred format (CSV, DataFrame, SQL query)
- Sample size needed for analysis
```

**Key improvements:**
- Domain context provided
- Clear analysis requirements
- Structured output format
- Links analysis to business goals
- Specifies visualization recommendations
- Provides next steps

---

## Example 7: Chaining with Target Agent

### Before
```
optimize this and send to gemini: help me fix this bug
```

### After (Optimized Prompt)
```
You are a debugging expert specializing in Python.

<context>
Code is producing unexpected behavior. Need systematic debugging approach.
</context>

<task>
Debug the following code by:
1. Identifying the root cause of the issue
2. Explaining why the bug occurs
3. Providing corrected code
4. Suggesting how to prevent similar bugs
</task>

<code>
[User's buggy code here]
</code>

<debugging_approach>
- Trace execution flow
- Check assumptions about data types/values
- Identify edge cases
- Review error messages if available
</debugging_approach>

<output_format>
**Root Cause:** [What's actually wrong]
**Explanation:** [Why this causes the observed behavior]
**Fix:** [Corrected code]
**Prevention:** [How to avoid this in future]
</output_format>

If code is not provided, request:
- The buggy code
- Expected vs actual behavior
- Any error messages
```

**Usage note:** This optimized prompt would then be sent to the gemini-consultant agent automatically.

**Key improvements:**
- Transforms vague "help me fix this bug" into structured debugging request
- Provides clear methodology
- Specifies desired output format
- Includes escape hatch
- Ready to chain with target agent

---

## Pattern Summary

| Pattern | Used In Examples | Key Benefit |
|---------|-----------------|-------------|
| **Role Assignment** | All examples | Sets expertise level and perspective |
| **XML Structure** | All examples | Separates data from instructions |
| **Few-Shot Examples** | Example 4 | Shows desired output style |
| **Escape Hatches** | Examples 1, 2, 4, 6, 7 | Handles missing information gracefully |
| **Output Formatting** | All examples | Ensures consistent, usable responses |
| **Multi-Agent Debate** | Example 5 | Examines complex decisions from multiple angles |
| **Context Engineering** | Example 6 | Grounds analysis in domain knowledge |
| **Clarifying Questions** | Example 2 | Surfaces requirements before work begins |

---

## Quick Transformation Checklist

When optimizing any prompt, ask:

1. **Role:** What expertise level/domain should Claude have?
2. **Context:** What background information is needed?
3. **Task:** What specifically should be done?
4. **Examples:** Would examples improve output quality?
5. **Structure:** Should I use XML tags to organize?
6. **Output:** What format do I want for the response?
7. **Edge cases:** What if information is missing/unclear?
8. **Cost:** Is this complex enough to warrant advanced techniques?

**Default to foundational patterns. Add complexity only when needed.**
