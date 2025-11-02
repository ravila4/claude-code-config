#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///
"""
Validate and render Graphviz DOT diagrams.

This script validates DOT diagram syntax and renders them to various formats
using different layout engines. It checks for common issues and provides
detailed error messages.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Tuple


LAYOUT_ENGINES = ["dot", "neato", "fdp", "circo", "twopi"]


def validate_syntax(diagram_content: str) -> Tuple[bool, list[str]]:
    """
    Validate Graphviz DOT diagram syntax for common issues.

    Returns:
        Tuple of (is_valid, list_of_warnings)
    """
    warnings = []

    # Check for common syntax issues
    lines = diagram_content.split("\n")

    # Check for proper graph declaration
    has_graph_declaration = False
    for line in lines:
        stripped = line.strip()
        if (
            stripped.startswith("digraph")
            or stripped.startswith("graph")
            or stripped.startswith("subgraph")
        ):
            has_graph_declaration = True
            break

    if not has_graph_declaration:
        warnings.append(
            "No graph declaration found. File should start with 'digraph' or 'graph'."
        )

    # Check for unclosed braces
    open_braces = diagram_content.count("{")
    close_braces = diagram_content.count("}")
    if open_braces != close_braces:
        warnings.append(
            f"Mismatched braces: {open_braces} opening braces but {close_braces} closing braces."
        )

    # Check for common shape typos
    common_shapes = [
        "box",
        "circle",
        "diamond",
        "ellipse",
        "octagon",
        "doublecircle",
        "plaintext",
        "cylinder",
        "component",
        "folder",
        "note",
    ]
    for i, line in enumerate(lines, 1):
        if "shape=" in line:
            # Extract shape value (simple heuristic)
            for shape in ["sqare", "elipse", "dimond", "octagn"]:  # Common typos
                if shape in line.lower():
                    warnings.append(
                        f"Line {i}: Possible shape typo '{shape}'. Check against valid shapes."
                    )

    # Check for nodes without proper termination
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if "-->" in stripped or "->" in stripped or "--" in stripped:
            if not stripped.endswith(";") and not stripped.endswith("{"):
                warnings.append(
                    f"Line {i}: Edge definition may be missing semicolon: {stripped}"
                )

    return len(warnings) == 0, warnings


def render_diagram(
    diagram_path: Path, output_path: Path, layout: str = "dot", format: str = "svg"
) -> Tuple[bool, str]:
    """
    Render Graphviz DOT diagram using specified layout engine.

    Args:
        diagram_path: Path to .dot file
        output_path: Path for output file
        layout: Layout engine (dot, neato, fdp, circo, twopi)
        format: Output format (svg, png, pdf)

    Returns:
        Tuple of (success, error_message)
    """
    if layout not in LAYOUT_ENGINES:
        return (
            False,
            f"Invalid layout engine: {layout}. Choose from: {', '.join(LAYOUT_ENGINES)}",
        )

    try:
        cmd = [layout, f"-T{format}", str(diagram_path), "-o", str(output_path)]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout
            return False, f"Rendering failed with {layout}:\n{error_msg}"

        return True, ""

    except subprocess.TimeoutExpired:
        return False, f"Rendering timed out after 30 seconds with {layout}"
    except FileNotFoundError:
        return (
            False,
            f"Layout engine '{layout}' not found. Install Graphviz: brew install graphviz (macOS) or apt-get install graphviz (Linux)",
        )
    except Exception as e:
        return False, f"Unexpected error with {layout}: {str(e)}"


def test_all_layouts(diagram_path: Path, output_dir: Path) -> dict[str, bool]:
    """
    Test diagram with all layout engines and report which ones work.

    Args:
        diagram_path: Path to .dot file
        output_dir: Directory for output files

    Returns:
        Dictionary mapping layout engine to success status
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    results = {}

    for layout in LAYOUT_ENGINES:
        output_file = output_dir / f"{diagram_path.stem}_{layout}.svg"
        success, error = render_diagram(diagram_path, output_file, layout=layout)
        results[layout] = success

        if success:
            print(f"✅ {layout:8} → {output_file}")
        else:
            print(f"❌ {layout:8} failed")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Validate and render Graphviz DOT diagrams",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate syntax only
  %(prog)s diagram.dot --validate-only

  # Render to SVG with dot layout (default)
  %(prog)s diagram.dot -o output.svg

  # Render with specific layout engine
  %(prog)s diagram.dot -o output.svg --layout neato

  # Test all layout engines
  %(prog)s diagram.dot --test-all-layouts

  # Render to PNG with high DPI
  %(prog)s diagram.dot -o output.png --format png --dpi 300
        """,
    )

    parser.add_argument("input", type=Path, help="Input Graphviz DOT file (.dot)")

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path (default: input name with format extension)",
    )

    parser.add_argument(
        "--layout",
        choices=LAYOUT_ENGINES,
        default="dot",
        help="Layout engine (default: dot)",
    )

    parser.add_argument(
        "--format",
        choices=["svg", "png", "pdf"],
        default="svg",
        help="Output format (default: svg)",
    )

    parser.add_argument(
        "--dpi", type=int, default=96, help="DPI for raster formats (default: 96)"
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate syntax, do not render",
    )

    parser.add_argument(
        "--test-all-layouts",
        action="store_true",
        help="Test rendering with all layout engines",
    )

    parser.add_argument(
        "--show-warnings",
        action="store_true",
        help="Show syntax warnings even if rendering succeeds",
    )

    args = parser.parse_args()

    # Check input file exists
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    # Read diagram content
    diagram_content = args.input.read_text()

    # Validate syntax
    is_valid, warnings = validate_syntax(diagram_content)

    if warnings and (args.show_warnings or not is_valid):
        print("⚠️  Syntax Warnings:", file=sys.stderr)
        for warning in warnings:
            print(f"  • {warning}", file=sys.stderr)
        print(file=sys.stderr)

    # If validate-only, exit here
    if args.validate_only:
        if is_valid:
            print(
                "✅ Validation passed (with warnings)"
                if warnings
                else "✅ Validation passed"
            )
            return 0
        else:
            print("❌ Validation found issues")
            return 1

    # Test all layouts mode
    if args.test_all_layouts:
        output_dir = args.input.parent / f"{args.input.stem}_layouts"
        print(f"Testing all layout engines for {args.input}...\n")
        results = test_all_layouts(args.input, output_dir)

        print(f"\nResults saved to: {output_dir}/")
        successful = sum(1 for v in results.values() if v)
        print(f"\n{successful}/{len(LAYOUT_ENGINES)} layout engines succeeded")
        return 0 if successful > 0 else 1

    # Determine output path
    output_path = args.output
    if not output_path:
        output_path = args.input.with_suffix(f".{args.format}")

    # Render diagram
    print(f"Rendering {args.input} → {output_path} (layout: {args.layout})...")
    success, error = render_diagram(args.input, output_path, args.layout, args.format)

    if success:
        print(f"✅ Successfully rendered to {output_path}")
        return 0
    else:
        print(f"❌ Rendering failed:", file=sys.stderr)
        print(f"  {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
