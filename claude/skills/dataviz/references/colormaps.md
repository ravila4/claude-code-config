# Colormap Selection Guide

## Core Principles

### Match Data Type to Colormap

| Data Type | Colormap Type | Examples |
|-----------|---------------|----------|
| Quantitative continuous | Sequential | viridis, plasma, cividis |
| Quantitative diverging | Diverging | RdBu_r, coolwarm, PiYG |
| Categorical (≤7 levels) | Qualitative | Okabe-Ito, tab10, Set2 |
| Categorical (>7 levels) | Faceting | Don't use color alone |
| Ordinal | Sequential lightness | YlOrRd, Purples, Blues |

### Visual Channel Effectiveness

For quantitative comparisons, effectiveness ranks:
1. Position (most accurate)
2. Length
3. Angle
4. Area
5. Color (least accurate)

Use color for categories; use position for quantities when possible.

## Perceptually Uniform Colormaps

These colormaps have equal perceptual steps, meaning equal data differences appear as equal visual differences.

### Recommended Sequential

```python
# Default choice
cmap = 'viridis'

# CVD-friendly alternative
cmap = 'cividis'

# High contrast
cmap = 'plasma'
cmap = 'inferno'
```

### Avoid

```python
# Perceptually non-uniform - avoid these
'jet'      # False peaks and valleys
'rainbow'  # Same issues
'hsv'      # Circular, misleading for linear data
```

## Diverging Colormaps

Use when data has meaningful center point (zero, mean, threshold).

```python
# Good diverging options
cmap = 'RdBu_r'    # Red-Blue (most common)
cmap = 'coolwarm'  # Less saturated
cmap = 'PiYG'      # Pink-Green (CVD-friendly alternative)

# Always center on meaningful value
sns.heatmap(data, cmap='RdBu_r', center=0)
```

## CVD-Safe Palettes

### Okabe-Ito Palette (Categorical)

Designed specifically for color vision deficiency accessibility.

```python
okabe_ito = [
    '#E69F00',  # Orange
    '#56B4E9',  # Sky blue
    '#009E73',  # Bluish green
    '#F0E442',  # Yellow
    '#0072B2',  # Blue
    '#D55E00',  # Vermillion
    '#CC79A7',  # Reddish purple
    '#000000',  # Black
]

plt.rcParams['axes.prop_cycle'] = plt.cycler(color=okabe_ito)
```

### Testing for CVD

```python
# Using colorspacious
from colorspacious import cspace_convert

# Simulate deuteranopia
deuteranopia_colors = cspace_convert(rgb_colors, "sRGB1", "sRGB1-deuteranomaly")
```

Online simulators: Coblis, Color Oracle

## Practical Selection Guide

### When to Use What

**Heatmap of expression values:**
- Absolute values → `viridis` (sequential)
- Compared to control → `RdBu_r` (diverging, center=0)

**Scatter plot groups:**
- 2-7 groups → Okabe-Ito or `tab10`
- >7 groups → Facet instead of color

**UMAP cell types:**
- Scanpy default palettes work well
- Or use `sc.pl.palettes.godsnot_102` for many types

**Continuous gradient on map:**
- `viridis` or `plasma` for most cases
- `cividis` if CVD is primary concern

### Colorbar Best Practices

```python
# Add colorbar with label
cbar = fig.colorbar(scatter)
cbar.set_label('Expression (log2 TPM)', rotation=270, labelpad=15)

# Truncate for outliers
vmin, vmax = np.percentile(data, [1, 99])
ax.imshow(data, vmin=vmin, vmax=vmax, cmap='viridis')
```

## WCAG Contrast Requirements

- **Text**: 4.5:1 minimum contrast ratio
- **Graphical elements**: 3:1 minimum

```python
# Check contrast with wcag-contrast-ratio package
from wcag_contrast_ratio import rgb, passes_AA

# Example: black text on white background
passes_AA(rgb(0, 0, 0), rgb(255, 255, 255), 'normal')  # True
```

## Quick Reference

| Use Case | Colormap |
|----------|----------|
| Default sequential | `viridis` |
| CVD-safe sequential | `cividis` |
| Diverging (centered) | `RdBu_r` |
| Categorical (≤7) | Okabe-Ito |
| Categorical (≤10) | `tab10` |
| High contrast | `plasma` |
