# Frame Evaluation Guide

Detailed criteria for evaluating extracted frames from screen recordings.

## Classification Types

| Content Type | Description | Examples |
|--------------|-------------|----------|
| `code` | Code snippets, terminal output | IDE, Jupyter notebook, terminal |
| `diagram` | Architecture, flowcharts, relationships | Whiteboard drawings, hand annotations |
| `visualization` | Charts, plots, data displays | Matplotlib plots, dashboards |
| `documentation` | External docs, websites | GitHub, official docs, wikis |
| `cluttered` | Multiple overlapping windows | Screen shares with noise |

## Critical Value Assessment

For EACH frame, answer these questions:

1. **Is this information already captured in the transcript/notes?**
   - If yes → likely DELETE (the text version is better)

2. **Is the visual presentation essential, or would text suffice?**
   - Code → Extract as code block, DELETE image
   - Config/parameters → Extract as table, DELETE image
   - Concepts explained in text → DELETE image

3. **Does this show a publicly available resource?**
   - Official documentation → DELETE (link to docs instead)
   - GitHub pages → DELETE (reference the repo)

4. **Is there distracting noise (other windows, chat, unrelated tabs)?**
   - If yes and valuable content exists → Consider CROP
   - If mostly noise → DELETE

5. **Would a clean diagram better convey this concept?**
   - Hand-drawn flowcharts → RE-CREATE in Graphviz
   - Annotated relationships → RE-CREATE in Graphviz/TikZ
   - Data flow explanations → RE-CREATE as diagram

## Decision Matrix

| Verdict | When to Use | Action |
|---------|-------------|--------|
| **DELETE** | Redundant, noisy, or better as text | Remove from notes, delete file |
| **EXTRACT** | Contains code/text not in transcript | Extract content to code block or table, then DELETE image |
| **CROP** | Partial value buried in clutter | Crop to essential portion, keep cropped version |
| **RE-CREATE** | Concept benefits from clean diagram | Create Graphviz/TikZ diagram, DELETE original |
| **KEEP** | Unique visual essential to understanding | Embed in notes as-is |

## Extracting Text/Code from Images

When a frame contains valuable code or configuration:

```markdown
**From screenshot at MM:SS:**
\`\`\`python
# Extracted code here
def example():
    pass
\`\`\`
```

Then DELETE the original image - the extracted code is more useful.

## Creating Clean Diagrams

When concepts would benefit from proper visualization, launch parallel sub-agents to create diagrams. Read the `graphviz-diagrams` skill for detailed guidelines.

**Rendering workflow:**
1. Create `.dot` source file (keep for future edits)
2. Render BOTH formats:
   - `dot -Tpng -Gdpi=150 diagram.dot -o diagram.png` (for critic review)
   - `dot -Tsvg diagram.dot -o diagram.svg` (for embedding in notes)
3. Launch `visual-design-critic` agent to review the PNG
4. **ALWAYS ask user before accepting revisions** from the critic
5. Embed the SVG in the final notes: `![[diagram.svg]]`

**Common diagram types:**
- Pipeline/workflow flows → Graphviz with clusters
- Comparison diagrams → Graphviz with side-by-side subgraphs
- Data relationships → Graphviz entity-relationship style
- Mathematical concepts → TikZ (read `tikz-diagrams` skill)
- Simple 2x2 tables/matrices → Markdown tables (no diagram needed)

## Deduplication

If multiple frames show nearly identical content (e.g., same code at different scroll positions):
- Keep only the most complete version
- Note the timestamp range in the notes if relevant
