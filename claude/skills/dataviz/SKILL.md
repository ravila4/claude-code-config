---
name: dataviz
description: Create publication-quality scientific figures in Python using matplotlib, seaborn, and plotly. Use when creating data visualizations, scientific plots, bioinformatics figures, or when user mentions charts, graphs, plotting, or figure generation.
---

# Data Visualization

## Contents

- [Overview](#overview)
- [When to Use](#when-to-use)
- [Core Libraries](#core-libraries)
- [Design Principles](#design-principles)
- [Quick Start Patterns](#quick-start-patterns)
- [Advanced Topics](#advanced-topics)
- [Error Handling](#error-handling)
- [References](#references)
- [Anti-Patterns](#anti-patterns)
- [Quality Checklist](#quality-checklist)
- [Export Guidelines](#export-guidelines)

## Overview

This skill provides guidance for creating publication-quality scientific and bioinformatics figures in Python. It combines visual perception theory, statistical graphics best practices, and domain-specific patterns from Rougier, Wilke, Tufte, Cleveland, and Wilkinson.

## When to Use

Use this skill when:
- Creating scientific or bioinformatics figures
- Generating publication-ready plots for manuscripts
- Working with matplotlib, seaborn, or plotly
- Needing guidance on colormaps, accessibility, or figure sizing

Skip this skill for:
- Simple exploratory plots where defaults suffice
- Non-scientific visualizations (dashboards, infographics)

## Core Libraries

**Primary stack:**
- Data: pandas, polars, numpy
- Plotting: matplotlib, seaborn, plotly
- Domain: scanpy, networkx (bioinformatics)
- R bridge: rpy2 for ggplot2, ComplexHeatmap when needed

## Design Principles

### 1. Minimize non-data ink (Tufte)

Remove chartjunk, redundant gridlines, excessive borders. Let data speak.

### 2. Emphasize comparisons

Align axes across panels. Use small multiples for stratification. Annotate differences.

### 3. Respect visual perception

- Position > Length > Angle > Area > Color for quantitative comparisons
- Use perceptually uniform colormaps (viridis, cividis, plasma)
- Categorical palettes: distinct hues, sufficient contrast (Okabe-Ito, Set2)
- Avoid rainbow colormaps, pie charts, 3D effects

### 4. Design for accessibility

- WCAG AA contrast ratios (4.5:1 text, 3:1 graphical)
- CVD-safe palettes (test with simulators)
- Font sizes: ≥8pt print, ≥10pt slides, ≥12pt posters

### 5. One story per figure

- Single clear message per figure
- Stratify by key covariates in faceted subplots
- Annotate aggregates: counts (n=), medians/means with CI
- Titles interpret, not just describe

### 6. Reproducibility first

- Inch-based sizing (not pixels): journals specify column widths
- DPI: 300+ for rasters, SVG preferred for line art
- Versioned dependencies, random seeds, documented colors

## Quick Start Patterns

### Basic figure setup

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Publication-ready defaults
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(3.5, 2.625))  # Single column width

# Clean up
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
fig.savefig('figure.svg', bbox_inches='tight')
```

### Scatter with overplotting control

```python
# For n > 1000 points
ax.scatter(x, y, alpha=0.3, s=10, rasterized=True)

# Or use hexbin for density
ax.hexbin(x, y, gridsize=30, cmap='viridis')
```

### Faceted comparison

```python
g = sns.FacetGrid(df, col='condition', height=2.5, aspect=1.2)
g.map_dataframe(sns.scatterplot, x='x', y='y', hue='group')
g.add_legend()
```

### Distribution comparison

```python
# Violin + strip for small n
sns.violinplot(data=df, x='group', y='value', inner='box')
sns.stripplot(data=df, x='group', y='value', color='black', alpha=0.5, size=3)
```

## Advanced Topics

### Label Placement with adjustText

Prevent overlapping labels on scatter plots and volcano plots:

```python
from adjustText import adjust_text

texts = []
for idx, row in top_genes.iterrows():
    texts.append(ax.text(row['x'], row['y'], row['label'], fontsize=8))

adjust_text(texts, arrowprops=dict(arrowstyle='-', color='gray', lw=0.5))
```

### Large Datasets (n > 100k)

```python
# Rasterize scatter points for performance
ax.scatter(x, y, alpha=0.3, s=5, rasterized=True)

# Or pre-aggregate with hexbin
ax.hexbin(x, y, gridsize=50, cmap='viridis', mincnt=1)

# Plotly with WebGL
import plotly.express as px
fig = px.scatter(df, x='x', y='y', render_mode='webgl')
```

### Multi-Panel Layouts

```python
import matplotlib.gridspec as gs

fig = plt.figure(figsize=(7.2, 5))
spec = gs.GridSpec(2, 3, figure=fig, wspace=0.3, hspace=0.3)

ax_main = fig.add_subplot(spec[0, :2])   # Spans 2 columns
ax_side = fig.add_subplot(spec[0, 2])    # Single column
ax_bottom = fig.add_subplot(spec[1, :])  # Full width
```

### Inset Axes for Outliers

```python
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# Main plot with truncated axis
ax.set_ylim(0, 100)

# Inset for outliers
axins = inset_axes(ax, width="30%", height="30%", loc='upper right')
axins.scatter(outlier_x, outlier_y)
axins.set_title('Outliers (y > 100)')
```

## Error Handling

### Missing Data

```python
# Check before plotting
print(f"Missing values: {df.isna().sum()}")

# Handle explicitly
df_clean = df.dropna(subset=['x', 'y'])
print(f"Dropped {len(df) - len(df_clean)} rows with missing data")
```

Document filtering in figure caption if >5% data excluded.

### Extreme Outliers

Options:
1. **Transform**: Use log scale, annotate transformation
2. **Truncate axis**: Add annotation "n=3 values >100 not shown"
3. **Inset panel**: Show outliers in separate zoomed region

```python
# Truncate with annotation
ax.set_ylim(0, np.percentile(y, 99))
ax.annotate(f'{(y > ax.get_ylim()[1]).sum()} outliers not shown',
            xy=(0.95, 0.95), xycoords='axes fraction', ha='right')
```

### Color Scale Saturation

```python
# Clip at percentiles to prevent outlier domination
vmin, vmax = np.percentile(data, [1, 99])
im = ax.imshow(data, vmin=vmin, vmax=vmax, cmap='viridis')
cbar = plt.colorbar(im)
cbar.set_label('Value (clipped at 1st/99th percentile)')
```

### Text Overlap

1. **adjustText** library (see Advanced Topics)
2. **Reduce labels**: Show only top N by significance
3. **Interactive**: Use Plotly hover tooltips instead of static labels

## References

Load these files for detailed guidance:

**Bioinformatics patterns**: See [references/bioinformatics.md](references/bioinformatics.md) for volcano plots, UMAP/t-SNE, heatmaps, QC patterns, UpSet plots.

**Colormap selection**: See [references/colormaps.md](references/colormaps.md) for perceptual principles, CVD-safe palettes, and selection guide.

**Publishing requirements**: See [references/publishing.md](references/publishing.md) for journal specs (Nature, Cell), export formats, sizing rules.

## Anti-Patterns

Avoid these common mistakes:

- **Pie charts** → Use bar charts
- **Venn diagrams (>3 sets)** → Use UpSet plots
- **Rainbow/jet colormaps** → Use viridis, plasma
- **3D plots for 2D data** → Unnecessary complexity
- **Dual y-axes with different units** → Use facets or normalization
- **Fonts <6pt final size** → Scale to ≥8pt minimum
- **Truncated y-axes without annotation** → Start at zero or mark break
- **Overplotting without mitigation** → Use alpha, jitter, binning
- **Categorical data on continuous colormap** → Use discrete palette
- **Missing error bars on aggregates** → Always show uncertainty
- **Unlabeled axes** → Always include labels with units
- **Inconsistent styles across panels** → Use shared stylesheet

## Quality Checklist

Before finalizing a figure:

- [ ] Correct data subset/filtering applied
- [ ] Axis labels include units
- [ ] Legend necessary and sufficient
- [ ] Colormap CVD-safe (tested)
- [ ] Font sizes readable at target size
- [ ] No chartjunk or redundant elements
- [ ] Statistical annotations accurate (p-values, n, CI)
- [ ] Code generates identical figure when re-run
- [ ] Random seeds set for stochastic methods (UMAP, t-SNE)

## Export Guidelines

```python
# SVG for vector graphics (preferred for line art)
fig.savefig('figure.svg', format='svg', bbox_inches='tight')

# PDF for manuscripts
fig.savefig('figure.pdf', format='pdf', dpi=300, bbox_inches='tight')

# PNG for slides/posters (or when many points)
fig.savefig('figure.png', format='png', dpi=300, bbox_inches='tight')
```
