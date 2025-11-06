# Color Schemes for Graphviz Diagrams

This guide provides evidence-based color selection principles for graph visualizations, drawing from Munzner (2014), Ware (2021), and Bertini & Di Battista (2008).

## Core Principles

### 1. Use Hue for Category, Luminance for Importance

**Hue** (color family) is most effective for encoding categorical distinctions:
- Node types (process, data store, decision)
- Organizational boundaries (teams, services, layers)
- Functional roles (input, processing, output)

**Luminance** (light/dark) encodes hierarchy or importance:
- Darker = higher priority, active, or critical
- Lighter = lower priority, passive, or background

**Example:**
```dot
// Good: Hue distinguishes categories, luminance shows importance
CriticalAPI [fillcolor="#1976d2"]; // Dark blue = critical API
StandardAPI [fillcolor="#64b5f6"]; // Light blue = standard API
Database [fillcolor="#388e3c"];    // Dark green = primary DB
Cache [fillcolor="#81c784"];       // Light green = secondary cache
```

### 2. Color Emphasizes Grouping, Not Connectivity

Use color to show **clusters, roles, or communities** - not to trace paths or connections. Let edge routing and layout convey connectivity.

**Rationale:** Shared hue promotes perceived grouping (Gestalt principles). Coloring edges to show paths creates visual clutter and confusion in dense graphs.

**Best practice:**
- Color nodes by functional group or domain
- Keep edges neutral (black, gray) or very subdued
- Use subgraph clustering with background colors for grouping

### 3. Keep Edge Colors Neutral and Subdued

Edges should **never compete with nodes** for attention. Exceptions: emphasizing specific flows (data vs control).

**Guidelines:**
- Default edges: black or `#606060` (dark gray)
- Secondary edges: `#b0b0b0` (light gray) or low opacity
- Control/configuration edges: `#90a4ae` (muted blue-gray), dashed, thin
- Data flow edges: solid, but still neutral or single accent color

**Ricardo's CLI edge pattern:**
```dot
// Control edges recede
CLI -> Component [color="#90a4ae", penwidth=0.8, style=dashed];

// Data flow prominent but neutral
Component -> Database [color="black", penwidth=1.4];
```

### 4. Encode Flow or Hierarchy with Gradients, Not Multiple Hues

For **sequential data** (throughput, latency, depth), use **monotonic gradients** within a single hue family.

**Avoid:** Rainbow scales or multiple unrelated hues for ordinal data.

**Use:** Light-to-dark progression in one hue:
- Blues: `#e3f2fd` → `#1976d2` → `#0d47a1`
- Greens: `#e8f5e9` → `#388e3c` → `#1b5e20`
- Oranges: `#fff3e0` → `#ef6c00` → `#e65100`

### 5. Maintain Consistent Color Semantics

**Never** let a single hue represent different categories in different parts of the diagram.

**Rule:** One color = one meaning across the entire diagram (and ideally across related diagrams).

**Example consistency:**
- Green always = data sources
- Orange always = processing steps
- Blue always = outputs
- Yellow always = warnings/pending

### 6. Limit Palette to 5-7 Hues

Human short-term memory struggles to differentiate more than 5-7 distinct categories. Beyond this, use:
- Luminance variation within hues
- Patterns or shapes as redundant encodings
- Hierarchical grouping (subgraphs) to reduce cognitive load

## Palette Selection

### Categorical (Qualitative)

Use when encoding **discrete categories** with no inherent order.

**Recommended palettes:**
- **Set2** - 8 soft, distinct colors (colorblind-safe)
- **Paired** - 12 colors in complementary pairs
- **Dark2** - 8 darker colors for contrast
- **tab10** - 10 colors from Tableau (widely recognized)

**Graphviz syntax:**
```dot
node [colorscheme=set28];
TypeA [fillcolor=1];
TypeB [fillcolor=2];
TypeC [fillcolor=3];
```

### Sequential

Use for **ordered data** (low to high): duration, depth, load.

**Recommended:**
- **blues3** through **blues9** (3-9 shades)
- **greens3** through **greens9**
- **oranges3** through **oranges9**

Light = low, dark = high.

**Graphviz syntax:**
```dot
node [colorscheme=blues5];
VeryLow [fillcolor=1];
Low [fillcolor=2];
Medium [fillcolor=3];
High [fillcolor=4];
VeryHigh [fillcolor=5];
```

### Diverging

Use for **deviations from a baseline**: above/below target, gain/loss.

**Recommended:**
- **rdbu** (Red-Blue) - temperature, pos/neg deviation
- **brbg** (Brown-Blue-Green) - opposing categories
- **prgn** (Purple-Green) - binary contrast

Neutral midpoint, diverging to two hues.

**Graphviz syntax:**
```dot
node [colorscheme=rdbu5];
BelowTarget [fillcolor=1];
Neutral [fillcolor=3];
AboveTarget [fillcolor=5];
```

## Case Study: Ricardo's Pastel Pipeline Pattern

Ricardo's PLINK merger diagrams use a consistent pastel palette for pipeline stages:

**Cluster backgrounds:**
- **Data Sources:** `#ede7f6` (light purple)
- **Loading:** `#fbe9e7` (light orange)
- **Planning:** `#e8f5e9` (light green)
- **Execution:** `#fff8e1` (light yellow)
- **Outputs:** `#e0f2f1` (light teal)

**Node fills** (one shade darker):
- Sources: `#d1c4e9`
- Loading: `#ffe0b2`, `#ffcc80`
- Planning: `#c8e6c9`, `#aed581`
- Execution: `#ffe082`, `#ffecb3`
- Outputs: `#b2dfdb`

**Edges:**
- Control (CLI): `#90a4ae`, thin, dashed
- Data flow: Bold, solid, stage-specific colors (`#1976d2`, `#ef6c00`, `#388e3c`)

**Pattern benefits:**
- Each pipeline stage has distinct hue
- Luminance shows sub-stages within clusters
- CLI edges recede into background
- Data flow prominent and clear

**When to use this pattern:**
- Multi-stage pipelines (ETL, processing workflows)
- Clear functional boundaries between stages
- Need for visual hierarchy (stage > step)

## Accessibility

### Colorblind-Safe Palettes

**Use:**
- ColorBrewer's colorblind-safe sets (mark on website)
- **viridis**, **plasma**, **cmocean** (perceptually uniform)
- **tab10** (Tableau palette, well-tested)

**Test with:**
- [Coblis](https://www.color-blindness.com/coblis-color-blindness-simulator/)
- Python: `colorspacious` library

### Contrast Requirements

Follow **WCAG 2.1 guidelines**:
- Text on background: ≥ 4.5:1 contrast ratio (AA)
- Large text: ≥ 3:1 contrast ratio

**Check contrast:** Use browser DevTools or [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

### Redundant Encodings

Never rely on color alone. Always provide:
- **Shape** variation (diamond, box, cylinder)
- **Labels** (descriptive text)
- **Patterns** or line styles (solid, dashed, dotted)

This ensures accessibility for colorblind users and maintains clarity in black-and-white prints.

## References

**Munzner, T. (2014).** *Visualization Analysis and Design.* CRC Press.
- Chapter 10: Network and Graph Visualization
- Principle: Use color sparingly to encode classes, not topology

**Ware, C. (2021).** *Information Visualization: Perception for Design* (4th ed.). Morgan Kaufmann.
- Chapters on Color Perception and Network Visualization
- Principle: Shared hue promotes grouping; luminance encodes hierarchy

**Bertini, E., & Di Battista, G. (2008).** "Color Coding in Graph Visualization: A Review." *Proceedings of BELIV '08: Beyond Time and Errors.*
- https://doi.org/10.1145/1377966.1377973
- Principle: Semantic color (data-driven) vs aesthetic (perceptual clarity)

**ColorBrewer 2.0:** https://colorbrewer2.org/
**Graphviz Color Documentation:** https://graphviz.org/doc/info/colors.html
