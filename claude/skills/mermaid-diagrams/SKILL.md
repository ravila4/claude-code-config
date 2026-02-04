---
name: mermaid-diagrams
description: Create, debug, and optimize Mermaid diagrams for visual documentation. Use when visualizing system architecture, process flows, data relationships, API interactions, state machines, or any scenario requiring diagram-based documentation. Handles diagram type selection, syntax validation, styling, and renderability testing.
---

# Mermaid Diagrams

## Overview

This skill enables creation, debugging, and optimization of Mermaid diagrams for visual documentation. Mermaid is a text-based diagramming tool that generates diagrams from simple markdown-like syntax, commonly used for system architecture, process flows, sequence diagrams, and more.

## When to Use This Skill

Use this skill when:
- Creating system architecture or component diagrams
- Documenting process flows or decision trees
- Visualizing API interactions with sequence diagrams
- Showing state transitions or workflow states
- Debugging existing Mermaid diagrams with parse errors
- Optimizing diagrams for clarity and renderability
- Generating visual documentation for technical projects

## Core Capabilities

### 1. Diagram Type Selection

Choose the most appropriate Mermaid diagram type for the use case:

**Flowcharts (TB/LR)**
- Use for: Process flows, system architecture, decision trees, workflow documentation
- Best when: Showing sequential steps, branching logic, or component relationships
- Avoid when: Data has complex timing dependencies (use sequence diagrams instead)

**Sequence Diagrams**
- Use for: API interactions, user journeys, system communication flows
- Best when: Showing time-based interactions between actors/systems
- Avoid when: Static relationships or hierarchical structures

**Class Diagrams**
- Use for: Object-oriented design, data models, API schemas
- Best when: Documenting software architecture or data relationships
- Avoid when: Process flows or user interactions

**State Diagrams**
- Use for: System states, user journey states, workflow states
- Best when: Showing how systems or objects change state over time
- Avoid when: Static relationships or simple processes

**Gantt Charts**
- Use for: Project timelines, scheduling, milestone tracking
- Best when: Showing project phases, dependencies, and deadlines
- Avoid when: System architecture or process flows

### 2. Syntax Debugging and Validation

Follow critical syntax patterns to ensure diagrams render correctly. See `references/syntax_guide.md` for comprehensive rules.

**Key patterns:**
- Always quote labels containing HTML tags or special characters
- Convert Unicode symbols to ASCII equivalents
- Use explicit class statements (avoid inline `:::class` syntax)
- Quote subgraph titles and set direction inside subgraphs
- Test diagrams before delivery

### 3. Visual Design and Styling

Create clean, readable diagrams with consistent styling:

**Readability:**
- Limit nodes to 20-25 per diagram for clarity
- Use meaningful, descriptive labels
- Group related elements with subgraphs
- Maintain consistent spacing

**Styling Consistency:**
- Color code by element type (inputs: light blue, processes: light gray, calculations: light green, outputs: light purple, warnings: light orange)
- Use consistent typography and stroke widths
- Maintain visual hierarchy

**Layout Optimization:**
- Choose appropriate direction (TB for hierarchical, LR for sequential)
- Minimize crossing lines
- Align related elements
- Use subgraphs for visual organization

### 4. ASCII Rendering for Terminal Display

Use `mermaid-ascii` to render diagrams as ASCII art directly in the terminal or conversation. This is useful when:
- Working in terminal-only environments
- Displaying diagrams inline in conversations
- Quick visualization without opening image files
- Sharing diagrams in text-only contexts (chat, logs, documentation)

**Supported diagram types for ASCII:**
- Flowcharts (graph/flowchart with TB, LR, etc.)
- Sequence diagrams

**Not yet supported in ASCII:**
- Class diagrams
- Gantt charts
- State diagrams
- Subgraphs

**Usage:**
```bash
# From file
mermaid-ascii -f diagram.mmd

# From stdin (useful for quick rendering)
echo 'graph LR; A-->B-->C' | mermaid-ascii

# ASCII-only mode (no Unicode box-drawing characters)
mermaid-ascii -f diagram.mmd --ascii

# Adjust padding for denser/sparser layouts
mermaid-ascii -f diagram.mmd -x 3 -y 3
```

**When to use ASCII vs SVG:**
- **ASCII**: Quick visualization, terminal output, inline in conversation, text-only sharing
- **SVG/PNG**: Documentation, high-fidelity output, complex diagrams with styling, diagrams needing subgraphs

### 5. Validation and Testing

Before delivering diagrams:
1. Verify all labels with HTML/symbols are quoted
2. Check for ASCII-only symbols
3. Confirm no inline class annotations
4. Validate subgraph formatting
5. Test renderability with Mermaid CLI or mermaid-ascii

**CLI Validation (SVG):**
```bash
npx --yes @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.svg -c mermaid.config.json
```

**CLI Validation (ASCII):**
```bash
mermaid-ascii -f diagram.mmd
```

**Configuration for HTML labels (SVG only):**
```json
{
  "securityLevel": "loose",
  "flowchart": {
    "htmlLabels": true,
    "wrap": true,
    "useMaxWidth": true
  }
}
```

## Workflow

When creating or debugging Mermaid diagrams:

1. **Analyze requirements** - Determine the optimal diagram type
2. **Draft diagram** - Create initial structure with proper syntax
3. **Apply styling** - Add consistent colors and formatting (SVG only)
4. **Validate syntax** - Check against rules in `references/syntax_guide.md`
5. **Choose output format**:
   - For inline display/terminal: Use `mermaid-ascii` to render ASCII
   - For documentation/files: Use `mermaid-cli` to render SVG/PNG
6. **Test rendering** - Verify diagram renders without errors
7. **Refine design** - Optimize for clarity and readability

## Resources

### scripts/

**validate_diagram.py** - Validate Mermaid syntax and render to SVG/PNG using mermaid-cli. Checks for common issues and provides detailed error messages.

**render_ascii.py** - Render Mermaid diagrams as ASCII art using mermaid-ascii. Useful for terminal display and inline conversation output.

### references/

**syntax_guide.md** - Comprehensive Mermaid syntax rules, debugging patterns, and common pitfalls. Load this when encountering parse errors or when creating complex diagrams to ensure proper syntax.

**diagram_templates.md** - Reusable templates for common diagram patterns (architecture, API flows, state machines). Reference when creating standard diagram types.

### External Tools

**mermaid-ascii** - https://github.com/AlexanderGrooff/mermaid-ascii
- Renders Mermaid diagrams as ASCII art
- Install: Download binary from releases or `go install github.com/AlexanderGrooff/mermaid-ascii@latest`
- Supports: Flowcharts, sequence diagrams
- Limitations: No subgraphs, class diagrams, Gantt, or state diagrams yet

## Output Format

When delivering diagrams, provide:

1. **Diagram code** - Complete, validated Mermaid syntax
2. **Analysis** - Explanation of diagram type choice and structure
3. **Rendered output** - For flowcharts/sequence diagrams, render ASCII inline:
   ```bash
   echo '<mermaid code>' | mermaid-ascii
   ```
4. **Rendering notes** - Any special configuration requirements
5. **Usage guidance** - How to embed or render the diagram

**Inline ASCII Example:**
When asked to visualize a simple flow, render it inline:
```
┌───────┐     ┌───────┐     ┌───────┐
│ Start │────▶│Process│────▶│  End  │
└───────┘     └───────┘     └───────┘
```
This provides immediate visual feedback without requiring the user to open external files.

## Quality Standards

All diagrams must:
- Follow syntax rules from `references/syntax_guide.md`
- Use appropriate diagram type for the use case
- Maintain visual clarity (under 25 nodes)
- Include meaningful labels
- Render without parse errors
- Apply consistent styling
