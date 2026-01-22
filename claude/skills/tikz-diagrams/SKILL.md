---
name: tikz-diagrams
description: Create publication-quality vector diagrams using TikZ/LaTeX. This skill should be used when creating technical figures, algorithm visualizations, or any diagram requiring precise positioning and mathematical notation.
---

# TikZ Diagrams

Create standalone TikZ figures that compile to PDF and convert to PNG for embedding in documentation.

## Quick Start

```latex
\documentclass[tikz,border=10pt]{standalone}
\usepackage{tikz}
\usepackage[sfdefault]{roboto}  % Sans-serif font
\usepackage[T1]{fontenc}
\usetikzlibrary{arrows.meta,calc,positioning}

\begin{document}
\begin{tikzpicture}
    % Your diagram here
\end{tikzpicture}
\end{document}
```

**Note**: The `roboto` package provides clean sans-serif fonts, use this by default. Alternatives: `helvet`, `sourcesanspro`, or `lmodern` with `\renewcommand{\familydefault}{\sfdefault}`.

## Core Primitives

**Coordinates**: `(x, y)` pairs in centimeters by default

**Drawing**:
```latex
\draw[style] (x1,y1) -- (x2,y2);              % Line
\draw[style] (x,y) circle (radius);           % Circle
\draw[style] (x1,y1) rectangle (x2,y2);       % Rectangle
\draw[style] (x1,y1) -- (x2,y2) -- (x3,y3);   % Path
```

**Filling**:
```latex
\fill[color] (x,y) circle (3pt);              % Filled circle (dot)
\fill[color!opacity] (x1,y1) rectangle (x2,y2); % Semi-transparent fill
\filldraw[fill=blue!20, draw=blue] ...;       % Fill and stroke
```

**Text**:
```latex
\node at (x,y) {text};                        % Simple label
\node[font=\small, align=center] at (x,y) {multi\\line};
\node[above right] at (x,y) {positioned};     % Relative positioning
```

**Loops** (for repetitive elements):
```latex
\foreach \x in {0,1,2,3} {
    \fill (\x, 0) circle (2pt);
}
\foreach \x/\label in {0/A, 1/B, 2/C} {
    \node at (\x, 0) {\label};
}
```

## Common Styles

```latex
% Line styles
\draw[thick] ...;                    % Thicker line
\draw[very thick] ...;               % Even thicker
\draw[dashed] ...;                   % Dashed line
\draw[dotted] ...;                   % Dotted line
\draw[-{Stealth}] ...;               % Arrow at end
\draw[{Stealth}-{Stealth}] ...;      % Arrows both ends

% Colors
\draw[red] ...;                      % Named color
\draw[blue!70] ...;                  % 70% blue
\draw[green!50!black] ...;           % Mix colors

% Combined
\draw[red, very thick, dashed, -{Stealth}] (0,0) -- (2,2);
```

## Useful Libraries

Load with `\usetikzlibrary{...}` after `\usepackage{tikz}`:

| Library | Purpose |
|---------|---------|
| `arrows.meta` | Modern arrow tips (`{Stealth}`, `{Triangle}`) |
| `calc` | Coordinate calculations (`$(A)!0.5!(B)$`) |
| `positioning` | Relative node placement (`right=of nodeA`) |
| `decorations.pathreplacing` | Braces, waves (`decorate, decoration={brace}`) |
| `patterns` | Fill patterns (hatching, dots) |
| `shapes.geometric` | Ellipse, diamond, regular polygons |

## Compilation Workflow

Use the `compile_tikz.sh` script to compile `.tex` files to both PDF and PNG:

```bash
cd /path/to/assets
../scripts/compile_tikz.sh figure.tex [dpi]
```

- Requires: `pdflatex` (TeX Live), `magick` (ImageMagick)
- DPI defaults to 300 if not specified
- Outputs both `figure.pdf` (vector) and `figure.png` (raster)
- Automatically cleans up `.aux` and `.log` files

**After compiling**: Read the PNG output and review for improvements before finalizing:
- Does the diagram clearly present the main idea?
- Are labels readable and well-positioned?
- Is spacing balanced and not cramped?
- Do colors provide sufficient contrast?
- Are any elements clipped or overlapping?

Iterate on the `.tex` source until the diagram communicates clearly.

## Common Patterns

### Annotated Diagram with Brace

```latex
\draw[decorate, decoration={brace, amplitude=5pt, mirror}]
    (0, 0) -- (0, 2);
\node[left, font=\scriptsize] at (-0.3, 1) {label};
```

### Side-by-Side Comparison

```latex
\begin{scope}[shift={(0,0)}]
    % Left diagram
    \node[font=\bfseries] at (1.5, 3) {Case A};
\end{scope}
\begin{scope}[shift={(5,0)}]
    % Right diagram
    \node[font=\bfseries] at (1.5, 3) {Case B};
\end{scope}
```

### Legend

```latex
\begin{scope}[shift={(0, -1)}]
    \fill[red] (0, 0) circle (2pt);
    \node[right, font=\scriptsize] at (0.15, 0) {Label A};
    \fill[blue] (2, 0) circle (2pt);
    \node[right, font=\scriptsize] at (2.15, 0) {Label B};
\end{scope}
```

### Relative Positioning with `calc`

```latex
\coordinate (A) at (0, 0);
\coordinate (B) at (4, 2);
\fill ($(A)!0.5!(B)$) circle (2pt);        % Midpoint of A-B
\fill ($(A)!0.25!(B)$) circle (2pt);       % 25% from A toward B
\node at ($(A) + (1, 0.5)$) {offset};      % A shifted by (1, 0.5)
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `Undefined control sequence` | Missing library | Add `\usetikzlibrary{...}` |
| `Missing $ inserted` | Math mode needed | Wrap in `$...$` |
| `Package tikz Error` | Syntax error | Check semicolons, braces |
| Arrows not showing | Old arrow syntax | Use `arrows.meta` library |

## Best Practices

1. **Use `standalone` class** - auto-crops to content, no page margins
2. **Set `border=10pt`** - prevents clipping at edges
3. **Use `\scriptsize` or `\tiny`** for labels - prevents oversized text
4. **Keep coordinates simple** - prefer integers or simple fractions
5. **Use `scope` for groups** - shift entire sub-diagrams easily
6. **Layer elements** - draw fills first, then strokes, then labels
7. **Save `.tex` source** - allows future modifications

