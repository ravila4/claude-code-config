#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///
"""
Render Mermaid diagrams as ASCII art using mermaid-ascii.

This script wraps the mermaid-ascii CLI tool to render flowcharts and
sequence diagrams as ASCII art for terminal display or inline conversation output.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def check_mermaid_ascii_installed() -> bool:
    """Check if mermaid-ascii is installed and available."""
    try:
        result = subprocess.run(
            ['mermaid-ascii', '--help'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def render_ascii(
    diagram: str,
    ascii_only: bool = False,
    padding_x: int = 5,
    padding_y: int = 5
) -> tuple[bool, str]:
    """
    Render Mermaid diagram as ASCII art.

    Args:
        diagram: Mermaid diagram source code
        ascii_only: Use only ASCII characters (no Unicode box-drawing)
        padding_x: Horizontal padding between nodes
        padding_y: Vertical padding between nodes

    Returns:
        Tuple of (success, output_or_error)
    """
    cmd = ['mermaid-ascii', '-x', str(padding_x), '-y', str(padding_y)]

    if ascii_only:
        cmd.append('--ascii')

    try:
        result = subprocess.run(
            cmd,
            input=diagram,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Unknown error"
            return False, f"Rendering failed: {error_msg}"

        return True, result.stdout

    except subprocess.TimeoutExpired:
        return False, "Rendering timed out after 30 seconds"
    except FileNotFoundError:
        return False, (
            "mermaid-ascii not found. Install it:\n"
            "  - Download from: https://github.com/AlexanderGrooff/mermaid-ascii/releases\n"
            "  - Or build from source: go install github.com/AlexanderGrooff/mermaid-ascii@latest"
        )
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"


def main():
    parser = argparse.ArgumentParser(
        description='Render Mermaid diagrams as ASCII art',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Render from file
  %(prog)s diagram.mmd

  # Render from stdin
  echo 'graph LR; A-->B' | %(prog)s

  # ASCII-only mode (no Unicode)
  %(prog)s diagram.mmd --ascii

  # Compact layout
  %(prog)s diagram.mmd -x 3 -y 3

Supported diagram types:
  - Flowcharts (graph/flowchart TB, LR, etc.)
  - Sequence diagrams

Not supported:
  - Class diagrams
  - Gantt charts
  - State diagrams
  - Subgraphs
        """
    )

    parser.add_argument(
        'input',
        nargs='?',
        type=Path,
        help='Input Mermaid diagram file (.mmd). Reads from stdin if not provided.'
    )

    parser.add_argument(
        '--ascii',
        action='store_true',
        help='Use only ASCII characters (no Unicode box-drawing)'
    )

    parser.add_argument(
        '-x', '--padding-x',
        type=int,
        default=5,
        help='Horizontal padding between nodes (default: 5)'
    )

    parser.add_argument(
        '-y', '--padding-y',
        type=int,
        default=5,
        help='Vertical padding between nodes (default: 5)'
    )

    parser.add_argument(
        '--check',
        action='store_true',
        help='Check if mermaid-ascii is installed and exit'
    )

    args = parser.parse_args()

    # Check installation
    if args.check:
        if check_mermaid_ascii_installed():
            print("mermaid-ascii is installed and available")
            return 0
        else:
            print("mermaid-ascii is not installed", file=sys.stderr)
            print("Install from: https://github.com/AlexanderGrooff/mermaid-ascii/releases")
            return 1

    # Read input
    if args.input:
        if not args.input.exists():
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            return 1
        diagram = args.input.read_text()
    else:
        # Read from stdin
        if sys.stdin.isatty():
            print("Error: No input file provided and stdin is empty", file=sys.stderr)
            print("Usage: %(prog)s diagram.mmd")
            print("   or: echo 'graph LR; A-->B' | %(prog)s")
            return 1
        diagram = sys.stdin.read()

    # Render
    success, output = render_ascii(
        diagram,
        ascii_only=args.ascii,
        padding_x=args.padding_x,
        padding_y=args.padding_y
    )

    if success:
        print(output)
        return 0
    else:
        print(f"Error: {output}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
