# Commands vs Agents: Decision Framework

## Key Differences (Verified from Anthropic Docs)

### Slash Commands
- **Context:** Execute within main conversation context (shares all history)
- **Invocation:** User-invoked (type `/command`)
- **Use for:** Quick, frequent tasks that benefit from existing context
- **Output:** Goes directly into main conversation
- **Format:** Markdown files with frontmatter in `.claude/commands/`

### Subagents (Task tool)
- **Context:** Context isolation - clean slate each invocation
- **Invocation:** Model-invoked or command-invoked
- **Use for:** Heavy, specialized tasks that shouldn't pollute main context
- **Output:** Returns summary to main, detailed work happens isolated
- **Format:** Markdown files with frontmatter in `.claude/agents/`

## Decision Framework

### Use Slash Commands When:
1. **Quick operations** (< 1 minute)
   - Format, lint, simple reviews
   - Generate boilerplate
   - Look up documentation

2. **Context-dependent**
   - Need current conversation history
   - Building on previous discussion
   - Quick follow-ups

3. **Simple templates**
   - Mostly prompt with `$ARGUMENTS`
   - Minimal file reading
   - No complex branching

### Use Subagents When:
1. **Heavy work** (> 1 minute)
   - Full test runs
   - Deep debugging
   - Large refactoring
   - Performance profiling

2. **Context isolation beneficial**
   - Avoid polluting main chat with logs
   - Need clean slate for focused work
   - Large file reads/analysis
   - Complex multi-step workflows

3. **Specialized expertise**
   - Domain knowledge (debugging, architecture)
   - Iterative workflows
   - Learning/pattern storage

### Use Commands that Wrap Agents:
- Simple user interface
- Agent does heavy lifting in isolation
- Command formats and presents summary
- **Example:** `/ask-gemini` → launches `gemini-consultant` agent

## Implementation Pattern: External LLM Integration

### The Pattern
```
/ask-{llm} $ARGUMENTS
  ↓
Command (lightweight wrapper)
  ↓
Launches {llm}-consultant agent
  ↓
Agent (isolated context):
  - Reads files
  - Calls external CLI
  - Caches response
  - Returns summary
  ↓
Command presents result
```

### Why This Works
1. **User gets simple interface** - just type `/ask-gemini question`
2. **Heavy work isolated** - no context pollution
3. **Cacheable** - responses stored in `.memories/external-llm-cache/`
4. **Reusable** - other agents can call consultants directly

## Current External LLM Setup

### Consultant Agents (in `.claude/agents/`)
- `gemini-consultant.md` - Google Gemini via CLI
- `gpt5-consultant.md` - GPT-5 via cursor-agent
- `codex-consultant.md` - Codex via codex CLI

### Wrapper Commands (in `.claude/commands/`)
- `/ask-gemini` - Launches gemini-consultant
- `/ask-gpt5` - Launches gpt5-consultant
- `/ask-codex` - Launches codex-consultant

### Multi-Perspective Review
- `multi-perspective-reviewer` agent - Coordinates all reviewers
- `/multi-agent-review` command - Simple wrapper to launch it

### Cache Structure
```
.memories/
├── external-llm-cache/
│   ├── gemini/
│   │   └── YYYY-MM-DD-{topic}-{hash}.json
│   ├── gpt5/
│   │   └── YYYY-MM-DD-{topic}-{hash}.json
│   └── codex/
│       └── YYYY-MM-DD-{topic}-{hash}.json
└── reviews/
    └── YYYY-MM-DD-multi-perspective-{topic}.json
```

### Cache Benefits
- Avoid redundant API calls (24h validity)
- Track questions over time
- Compare how LLM responses evolve
- Learn reviewer strengths/weaknesses

## Archived Meta-Agents

### Why Archived (to `examples/orchestration/`)
- **agent-router** - Main Claude interface already does routing
- **multi-agent-planner** - Creates plans nothing consumes
- **agent-orchestration-manager** - Runtime coordination doesn't exist

### Reality
- No message queues, agent registries, parallel execution
- Main Claude coordinates via sequential Task tool launches
- Meta-agents added complexity without value

## Key Learnings

**What Works:**
- Specialized agents with clear responsibilities
- Simple sequential workflows coordinated by main interface
- Commands as wrappers around agents
- External LLM integration with caching

**What Doesn't:**
- Meta-agents orchestrating other agents
- Complex runtime coordination assumptions
- Pseudocode suggesting non-existent infrastructure
- Over-engineered solutions for simple problems

---

**Last Updated:** 2025-10-18
