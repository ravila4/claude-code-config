#!/usr/bin/env python3
"""
nbcell - Selective cell extraction from Jupyter notebooks.

Enables targeted access to notebook outputs (plots, tables, text) without
loading entire notebooks into context.
"""

import argparse
import base64
import json
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path


def load_notebook(path: str) -> dict:
    """Load notebook JSON."""
    with open(path) as f:
        return json.load(f)


class TableParser(HTMLParser):
    """Parse HTML tables to extract row data."""

    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.rows = []
        self.current_row = []
        self.current_cell = ""

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
        elif tag == "tr":
            self.in_row = True
            self.current_row = []
        elif tag in ("td", "th"):
            self.in_cell = True
            self.current_cell = ""

    def handle_endtag(self, tag):
        if tag == "table":
            self.in_table = False
        elif tag == "tr":
            self.in_row = False
            if self.current_row:
                self.rows.append(self.current_row)
        elif tag in ("td", "th"):
            self.in_cell = False
            self.current_row.append(self.current_cell.strip())

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell += data


def get_cell_info(cell: dict) -> dict:
    """Extract metadata about a cell's outputs."""
    info = {
        "cell_type": cell["cell_type"],
        "has_image": False,
        "has_table": False,
        "output_bytes": 0,
        "source_preview": "",
    }

    source = "".join(cell.get("source", []))
    info["source_preview"] = source[:60].replace("\n", " ")

    for output in cell.get("outputs", []):
        info["output_bytes"] += len(str(output))

        if "data" in output:
            data = output["data"]
            if "image/png" in data:
                info["has_image"] = True
            if "text/html" in data:
                html = "".join(data["text/html"])
                if "<table" in html.lower():
                    info["has_table"] = True

    return info


def cmd_index(args):
    """List all cells with output summary."""
    nb = load_notebook(args.notebook)
    cells = nb["cells"]

    print(f"Notebook: {args.notebook}")
    print(f"Total cells: {len(cells)}")
    print("=" * 80)
    print(f"{'Cell':>4} {'Type':<4} {'Size':>10} {'Img':>3} {'Tbl':>3}  Source")
    print("-" * 80)

    for i, cell in enumerate(cells):
        info = get_cell_info(cell)
        cell_type = info["cell_type"][:4]
        size = info["output_bytes"]
        img = "Y" if info["has_image"] else ""
        tbl = "Y" if info["has_table"] else ""
        preview = info["source_preview"][:50]

        print(f"{i:4d} {cell_type:<4} {size:>10} {img:>3} {tbl:>3}  {preview}...")


def cmd_find(args):
    """Search cells by code content."""
    nb = load_notebook(args.notebook)
    pattern = args.pattern.lower()

    print(f"Searching for: {args.pattern}")
    print("=" * 80)

    found = 0
    for i, cell in enumerate(nb["cells"]):
        source = "".join(cell.get("source", []))
        if pattern in source.lower():
            found += 1
            info = get_cell_info(cell)
            markers = []
            if info["has_image"]:
                markers.append("plot")
            if info["has_table"]:
                markers.append("table")
            marker_str = f" [{', '.join(markers)}]" if markers else ""

            print(f"\nCell {i}{marker_str}:")
            # Show matching context
            lines = source.split("\n")
            for line in lines[:10]:
                if pattern in line.lower():
                    print(f"  > {line[:70]}")
                else:
                    print(f"    {line[:70]}")
            if len(lines) > 10:
                print(f"    ... ({len(lines) - 10} more lines)")

    print(f"\n{found} cell(s) found.")


def cmd_show(args):
    """Display cell code and text outputs."""
    nb = load_notebook(args.notebook)
    cell_idx = args.cell

    if cell_idx >= len(nb["cells"]):
        print(f"Error: Cell {cell_idx} not found. Notebook has {len(nb['cells'])} cells.")
        sys.exit(1)

    cell = nb["cells"][cell_idx]
    info = get_cell_info(cell)

    print(f"Cell {cell_idx} ({info['cell_type']})")
    print("=" * 80)

    # Show source
    print("SOURCE:")
    print("-" * 40)
    source = "".join(cell.get("source", []))
    print(source)
    print()

    # Show outputs
    outputs = cell.get("outputs", [])
    if outputs:
        print("OUTPUTS:")
        print("-" * 40)

        for i, output in enumerate(outputs):
            output_type = output.get("output_type", "unknown")

            if "text" in output:
                print("".join(output["text"]))

            if "data" in output:
                data = output["data"]
                if "text/plain" in data:
                    print("".join(data["text/plain"]))
                if "image/png" in data:
                    print(f"[Image: {len(data['image/png'])} bytes - use 'plot' command to extract]")
                if "text/html" in data:
                    html = "".join(data["text/html"])
                    if "<table" in html.lower():
                        print(f"[Table: {len(html)} bytes - use 'table' command to extract]")
                    else:
                        print(f"[HTML: {len(html)} bytes]")


def cmd_plot(args):
    """Extract plot image to temp file."""
    nb = load_notebook(args.notebook)
    cell_idx = args.cell

    if cell_idx >= len(nb["cells"]):
        print(f"Error: Cell {cell_idx} not found. Notebook has {len(nb['cells'])} cells.")
        sys.exit(1)

    cell = nb["cells"][cell_idx]

    for output in cell.get("outputs", []):
        if "data" in output and "image/png" in output["data"]:
            img_data = base64.b64decode(output["data"]["image/png"])

            if args.output:
                output_path = args.output
            else:
                # Create temp file
                fd, output_path = tempfile.mkstemp(suffix=".png", prefix=f"nbcell_{cell_idx}_")
                import os
                os.close(fd)

            with open(output_path, "wb") as f:
                f.write(img_data)

            print(output_path)
            return

    print(f"Error: No image found in cell {cell_idx}.")
    sys.exit(1)


def cmd_table(args):
    """Extract table as markdown or CSV."""
    nb = load_notebook(args.notebook)
    cell_idx = args.cell

    if cell_idx >= len(nb["cells"]):
        print(f"Error: Cell {cell_idx} not found. Notebook has {len(nb['cells'])} cells.")
        sys.exit(1)

    cell = nb["cells"][cell_idx]

    for output in cell.get("outputs", []):
        if "data" in output and "text/html" in output["data"]:
            html = "".join(output["data"]["text/html"])
            if "<table" not in html.lower():
                continue

            parser = TableParser()
            parser.feed(html)
            rows = parser.rows

            if not rows:
                print("Error: Could not parse table.")
                sys.exit(1)

            # Apply row limit
            total_rows = len(rows)
            if not args.all and args.rows and total_rows > args.rows + 1:  # +1 for header
                display_rows = rows[: args.rows + 1]
                truncated = total_rows - args.rows - 1
            else:
                display_rows = rows
                truncated = 0

            if args.format == "csv":
                import csv
                import io

                output = io.StringIO()
                writer = csv.writer(output)
                for row in display_rows:
                    writer.writerow(row)
                print(output.getvalue())
            else:
                # Markdown format
                if display_rows:
                    header = display_rows[0]
                    print("| " + " | ".join(header) + " |")
                    print("| " + " | ".join(["---"] * len(header)) + " |")
                    for row in display_rows[1:]:
                        # Pad row if needed
                        padded = row + [""] * (len(header) - len(row))
                        print("| " + " | ".join(padded[: len(header)]) + " |")

            if truncated:
                print(f"\n[...{truncated} more rows]")

            return

    print(f"Error: No table found in cell {cell_idx}.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Selective cell extraction from Jupyter notebooks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nbcell index notebook.ipynb                    # List all cells
  nbcell find notebook.ipynb "scatter"           # Find cells containing "scatter"
  nbcell show notebook.ipynb 68                  # Show cell 68 code + outputs
  nbcell plot notebook.ipynb 68                  # Extract plot from cell 68
  nbcell table notebook.ipynb 7                  # Extract table as markdown
  nbcell table notebook.ipynb 7 --format csv     # Extract table as CSV
""",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # index command
    p_index = subparsers.add_parser("index", help="List all cells with output summary")
    p_index.add_argument("notebook", help="Path to notebook file")

    # find command
    p_find = subparsers.add_parser("find", help="Search cells by code content")
    p_find.add_argument("notebook", help="Path to notebook file")
    p_find.add_argument("pattern", help="Search pattern")

    # show command
    p_show = subparsers.add_parser("show", help="Display cell code and text outputs")
    p_show.add_argument("notebook", help="Path to notebook file")
    p_show.add_argument("cell", type=int, help="Cell index")

    # plot command
    p_plot = subparsers.add_parser("plot", help="Extract plot image to file")
    p_plot.add_argument("notebook", help="Path to notebook file")
    p_plot.add_argument("cell", type=int, help="Cell index")
    p_plot.add_argument("-o", "--output", help="Output file path (default: temp file)")

    # table command
    p_table = subparsers.add_parser("table", help="Extract table as markdown or CSV")
    p_table.add_argument("notebook", help="Path to notebook file")
    p_table.add_argument("cell", type=int, help="Cell index")
    p_table.add_argument("--format", choices=["markdown", "csv"], default="markdown", help="Output format")
    p_table.add_argument("--rows", type=int, default=20, help="Max rows to display (default: 20)")
    p_table.add_argument("--all", action="store_true", help="Show all rows")

    args = parser.parse_args()

    commands = {
        "index": cmd_index,
        "find": cmd_find,
        "show": cmd_show,
        "plot": cmd_plot,
        "table": cmd_table,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
