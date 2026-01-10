---
name: analyzing-notebooks
description: Extract and analyze specific cells from Jupyter notebooks without loading entire files. This skill should be used when working with .ipynb files, viewing notebook plots or tables, or when the user references specific cell outputs. Enables selective extraction of plots, tables, and code outputs from large notebooks.
---

# Analyzing Notebooks

Selectively extract cell outputs (plots, tables, text) from Jupyter notebooks without loading entire notebooks into context. Large notebooks (20-40MB+) contain embedded outputs that would consume excessive context - this skill provides targeted access.

## Quick Reference

The `nbcell` CLI utility provides selective cell access:

```bash
# Location: ~/.claude/skills/analyzing-notebooks/scripts/nbcell.py

# List all cells with output summary
python3 ~/.claude/skills/analyzing-notebooks/scripts/nbcell.py index notebook.ipynb

# Find cells containing specific code
python3 ~/.claude/skills/analyzing-notebooks/scripts/nbcell.py find notebook.ipynb "pattern"

# Show cell code + text outputs
python3 ~/.claude/skills/analyzing-notebooks/scripts/nbcell.py show notebook.ipynb <cell_number>

# Extract plot to temp file
python3 ~/.claude/skills/analyzing-notebooks/scripts/nbcell.py plot notebook.ipynb <cell_number>

# Extract table as markdown
python3 ~/.claude/skills/analyzing-notebooks/scripts/nbcell.py table notebook.ipynb <cell_number>
```

## Workflow

### Step 1: Index the notebook

Run `index` to see all cells with their output types and sizes:

```bash
python3 ~/.claude/skills/analyzing-notebooks/scripts/nbcell.py index notebook.ipynb
```

Output columns:
- **Cell**: Cell index number
- **Type**: code or mark (markdown)
- **Size**: Output size in bytes
- **Img**: Y if cell contains a plot
- **Tbl**: Y if cell contains a table
- **Source**: Code preview

### Step 2: Locate cells of interest

Use `find` to search cells by code content:

```bash
python3 ~/.claude/skills/analyzing-notebooks/scripts/nbcell.py find notebook.ipynb "scatter"
```

Shows matching cells with context and markers for plots/tables.

### Step 3: Extract specific outputs

**To view a plot:**
```bash
# Extract to temp file
path=$(python3 ~/.claude/skills/analyzing-notebooks/scripts/nbcell.py plot notebook.ipynb 68)
# Then use Read tool on $path to display the image
```

**To view a table:**
```bash
python3 ~/.claude/skills/analyzing-notebooks/scripts/nbcell.py table notebook.ipynb 7
# Outputs markdown table directly
```

**To see cell code and text outputs:**
```bash
python3 ~/.claude/skills/analyzing-notebooks/scripts/nbcell.py show notebook.ipynb 68
```

## Table Options

```bash
# Limit rows (default: 20)
python3 ~/.claude/skills/analyzing-notebooks/scripts/nbcell.py table notebook.ipynb 7 --rows 50

# Show all rows
python3 ~/.claude/skills/analyzing-notebooks/scripts/nbcell.py table notebook.ipynb 7 --all

# Output as CSV
python3 ~/.claude/skills/analyzing-notebooks/scripts/nbcell.py table notebook.ipynb 7 --format csv
```

## Using Paired .py Files

Databricks notebooks export paired `.py` files with `# COMMAND ----------` cell delimiters. These can serve as a lightweight structural map:

1. Read the `.py` file to understand code structure
2. Cell indices in the `.py` correspond to notebook cells
3. Use `nbcell` to extract specific outputs from the `.ipynb`
