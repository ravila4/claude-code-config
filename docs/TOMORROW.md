# Tomorrow's Agent Development Plan

## Session Context
Date: 2025-10-19 Evening
Status: Documentation updated, ready for new development

## Completed Today
- ✅ Deleted test-runner agent (unnecessary - basic operation)
- ✅ Deleted test-harness command (too broad, 2052 lines)
- ✅ Created python-test-engineer agent (730 lines, focused on Python + Feathers)
- ✅ Updated capability matrix
- ✅ Added advanced 2025 patterns to prompt-optimization-specialist

## Tomorrow's Priorities

### 1. New Agent: python-dataviz-expert

**Purpose:** Scientific data visualization expert
**Why:** Bioinformatics needs beautiful, informative plots

**Capabilities:**
- matplotlib, seaborn, polars, numpy, pandas, plotly expertise
- Translate scientific specs into visualizations
- Iterative design refinement (like mermaid-expert)
- Save plots to PNG/SVG files
- Store successful plot patterns in memory
- Integrate with visual-design-critic for feedback

**Learning Mode:** Yes (0.7)
**Storage:** `.memories/dataviz/`
**Integrations:** visual-design-critic, memory-knowledge-keeper

**Key Features:**
```python
# Example pattern to store:
DO: Use scientific color schemes (viridis, plasma)
DO: Label axes with units
DO: Use appropriate plot type for data distribution
DONT: Use rainbow colormap (not colorblind-friendly)
DONT: Clutter with excessive gridlines
```

### 2. New Agent: bioinformatics-research-expert

**Purpose:** Deep research on biology/bioinformatics topics
**Why:** Need specialized domain knowledge for bioinformatics work

**Capabilities:**
- Deep research on biological topics
- Paper search and ingestion
- Call external LLMs (gemini, gpt5) for specialized queries
- Expert in bioinformatics tools (BLAST, bedtools, samtools, etc.)
- Distill complex papers into actionable insights
- Store research findings in memory

**Learning Mode:** Yes (0.7)
**Storage:** `.memories/research/`, Obsidian vault
**Integrations:** memory-knowledge-keeper, obsidian-vault-manager, context-retrieval-specialist

**Integration with External LLMs:**
- Use prompt-optimization-specialist before calling Gemini/GPT5
- Store responses in memory-knowledge-keeper with source attribution

### 3. Refactor: docker-optimize Command → Agent

**Current State:** `claude/commands/docker-optimize.md`
**Problem:** Complex enough to warrant agent status
**Solution:** Convert to agent with learning mode

**Why Agent:**
- Complex enough to benefit from pattern storage
- Learns optimal configurations over time
- Integrates with other infrastructure agents

### 4. Enhancement: claude/CLAUDE.md Improvements

**Current Issues:**
- Not aware of available agents
- Doesn't mention deep-wiki MCP
- Could use prompt optimization

**Improvements:**
1. Add agent awareness section
   ```markdown
   ## Available Agents
   - python-test-engineer: Testing with Feathers techniques
   - python-dataviz-expert: Scientific visualization
   - bioinformatics-research-expert: Domain research
   - memory-knowledge-keeper: Central pattern storage
   - [full list in claude/agents/README.md]
   ```

2. Add MCP tools section
   ```markdown
   ## MCP Tools
   - deep-wiki: GitHub repository knowledge retrieval
   - [future MCPs...]
   ```

3. Run through prompt-optimization-specialist for clarity

### 5. Enhancement: deep-wiki MCP Integration

**Integration Points:**

**memory-knowledge-keeper:**
```markdown
## Source Types
- official_docs (confidence: 0.90)
- deep-wiki (confidence: 0.85)  # NEW
- user-verified (confidence: 0.95)
- llm-consultant (confidence: 0.70)
```

**context-retrieval-specialist:**
- Should use deep-wiki for GitHub repo context
- Alternative to WebFetch for open-source projects

**Hook Opportunity:**
- Similar to WebFetch hook
- Trigger memory storage after deep-wiki queries

### 6. Enhancement: tts-status-notifier Hook

**Current:** Agent exists but no automatic triggering
**Proposal:** Add postToolUse hook for long-running operations

```bash
# claude/hooks/notification-post.sh
# Trigger TTS notification after certain events
# - Test suite completion
# - Long-running analysis completion
# - Build/deployment completion
```

## Implementation Order

1. **python-dataviz-expert** (High value for bioinformatics)
2. **deep-wiki integration** (Leverage existing MCP)
3. **bioinformatics-research-expert** (Builds on deep-wiki)
4. **claude/CLAUDE.md improvements** (Quick win)
5. **docker-optimize refactor** (Lower priority)
6. **tts-status-notifier hook** (Polish)

## Notes

- Keep agents focused on Python/bioinformatics use cases
- All new agents should follow Agent Integration Framework
- Store patterns in `.memories/` with flat-file spec
- Use learning mode (0.7 threshold) for iterative improvement
- Integrate with memory-knowledge-keeper for cross-session learning

## Questions to Answer Tomorrow

1. Should python-dataviz-expert generate code or just the plot files?
   - Leaning toward: Both (code for reproducibility, files for immediate use)

2. How should bioinformatics-research-expert handle paper PDFs?
   - Option A: Use WebFetch for abstracts only
   - Option B: Add PDF ingestion capability
   - Option C: Store paper URLs and summaries only

3. Should deep-wiki hook store ALL queries or only successful ones?
   - Leaning toward: Only successful queries with useful results

4. Priority order if time is limited?
   - python-dataviz-expert (most immediate value)
   - deep-wiki integration (leverage existing tool)
   - CLAUDE.md improvements (low effort, high clarity)
