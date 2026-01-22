# Publishing Requirements

## Figure Sizing

### Standard Column Widths

| Journal | Single Column | Double Column |
|---------|---------------|---------------|
| Nature | 89mm (3.5") | 183mm (7.2") |
| Cell | 85mm (3.35") | 174mm (6.85") |
| Science | 90mm (3.5") | 183mm (7.2") |
| PLOS | 83mm (3.27") | 173mm (6.81") |

### Setting Figure Size

```python
# Single column (most common)
fig, ax = plt.subplots(figsize=(3.5, 2.625))  # 4:3 aspect

# Double column
fig, ax = plt.subplots(figsize=(7.2, 4.5))

# Golden ratio
width = 3.5
height = width / 1.618
fig, ax = plt.subplots(figsize=(width, height))
```

### Multi-Panel Layouts

```python
import matplotlib.gridspec as gs

fig = plt.figure(figsize=(7.2, 6))
spec = gs.GridSpec(2, 3, figure=fig, wspace=0.3, hspace=0.3)

ax1 = fig.add_subplot(spec[0, :2])  # Top left, spans 2 columns
ax2 = fig.add_subplot(spec[0, 2])   # Top right
ax3 = fig.add_subplot(spec[1, :])   # Bottom, full width
```

## Typography

### Font Requirements

Most journals require sans-serif fonts:
- Arial (most universal)
- Helvetica
- DejaVu Sans (open source alternative)

```python
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
```

### Font Sizes

Scale based on figure width:

| Element | 3.5" figure | 7" figure |
|---------|-------------|-----------|
| Axis labels | 10pt | 12pt |
| Tick labels | 8pt | 10pt |
| Legend | 8pt | 10pt |
| Annotations | 8pt | 10pt |

```python
# For single-column figure
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['legend.fontsize'] = 8
```

**Minimum**: Never go below 6pt at final print size.

## Export Formats

### Vector (Preferred for Line Art)

```python
# SVG - editable, web-friendly
fig.savefig('figure.svg', format='svg', bbox_inches='tight')

# PDF - print-ready, embeds fonts
fig.savefig('figure.pdf', format='pdf', bbox_inches='tight')

# EPS - legacy format, some journals require
fig.savefig('figure.eps', format='eps', bbox_inches='tight')
```

### Raster (For Dense Data)

```python
# PNG - when >10k points or complex patterns
fig.savefig('figure.png', format='png', dpi=300, bbox_inches='tight')

# TIFF - some journals prefer
fig.savefig('figure.tiff', format='tiff', dpi=300, bbox_inches='tight')
```

### DPI Requirements

| Use Case | DPI |
|----------|-----|
| Screen/web | 72-150 |
| Print (line art) | 300 |
| Print (photographs) | 300-600 |
| Poster | 150-300 |

## Color Mode

### RGB vs CMYK

Most journals accept RGB. Some print journals require CMYK.

```python
# Check journal requirements
# RGB is default in matplotlib

# For CMYK conversion, use external tools:
# - ImageMagick: convert input.png -colorspace CMYK output.tiff
# - Adobe Illustrator/Photoshop
```

### Grayscale Compatibility

Ensure figures remain interpretable in grayscale (many readers print in B&W).

```python
# Test grayscale conversion
from PIL import Image
img = Image.open('figure.png').convert('L')
img.save('figure_grayscale.png')
```

## Journal-Specific Notes

### Nature/Nature Methods

- Arial or Helvetica font
- Minimum 5pt font size
- 300 dpi minimum
- RGB color
- No text in figures should be smaller than 5pt at final size

### Cell/Cell Press

- Arial or Helvetica
- 8-12pt font range
- 300-500 dpi
- Single column: 85mm, Double: 174mm

### PLOS

- Open access, less restrictive
- EPS, PDF, or TIFF preferred
- 300 dpi minimum
- No specific font requirements

## Matplotlib Stylesheet

Save as `publication.mplstyle`:

```python
# Font
font.family: sans-serif
font.sans-serif: Arial, Helvetica, DejaVu Sans
font.size: 10
axes.labelsize: 10
xtick.labelsize: 8
ytick.labelsize: 8
legend.fontsize: 8

# Figure
figure.figsize: 3.5, 2.625
figure.dpi: 300
savefig.dpi: 300
savefig.bbox: tight

# Style
axes.spines.top: False
axes.spines.right: False
axes.grid: False
axes.linewidth: 0.8
xtick.major.width: 0.8
ytick.major.width: 0.8

# Colors (Okabe-Ito)
axes.prop_cycle: cycler('color', ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7'])
```

Usage:

```python
plt.style.use('publication.mplstyle')
```

## Checklist Before Submission

- [ ] Figure width matches journal requirements
- [ ] Font is Arial/Helvetica, ≥6pt at final size
- [ ] DPI ≥300 for raster images
- [ ] Grayscale version is interpretable
- [ ] Colors are CVD-safe
- [ ] File format matches journal requirements
- [ ] Panel labels (A, B, C) are consistent
- [ ] All text is legible at printed size
