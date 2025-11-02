#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///
"""
Validate and render Mermaid diagrams.

This script validates Mermaid diagram syntax and renders them to various formats.
It checks for common issues and provides detailed error messages.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple


def create_mermaid_config(html_labels: bool = True) -> dict:
    """Create Mermaid configuration for rendering."""
    return {
        "securityLevel": "loose" if html_labels else "strict",
        "flowchart": {
            "htmlLabels": html_labels,
            "wrap": True,
            "useMaxWidth": True
        },
        "theme": "default"
    }


def validate_syntax(diagram_content: str) -> Tuple[bool, list[str]]:
    """
    Validate Mermaid diagram syntax for common issues.

    Returns:
        Tuple of (is_valid, list_of_warnings)
    """
    warnings = []

    # Check for Unicode symbols that should be ASCII
    unicode_replacements = {
        '↔': '<->',
        '×': 'x',
        '≥': '>=',
        '≤': '<=',
        '·': '-',
        '•': '-',
        '–': '-',
        '—': '-',
        '→': '->',
        '←': '<-',
        ''': "'",
        ''': "'",
        '"': '"',
        '"': '"'
    }

    for unicode_char, ascii_char in unicode_replacements.items():
        if unicode_char in diagram_content:
            warnings.append(
                f"Unicode character '{unicode_char}' found. Consider using '{ascii_char}' instead."
            )

    # Check for inline class annotations (:::)
    if ':::' in diagram_content:
        warnings.append(
            "Inline class annotation ':::' found. Use explicit class statements instead:\n"
            "  classDef myClass fill:#f00;\n"
            "  class A myClass"
        )

    # Check for potentially reserved class names
    reserved_names = ['in', 'out']
    for name in reserved_names:
        if f'classDef {name} ' in diagram_content or f'classDef {name}\n' in diagram_content:
            warnings.append(
                f"Reserved class name '{name}' found. Use 'input' or 'output' instead."
            )

    # Check for unquoted labels with HTML tags
    lines = diagram_content.split('\n')
    for i, line in enumerate(lines, 1):
        if '<' in line and '>' in line and '[' in line and ']' in line:
            # Simple heuristic: if we see HTML-like tags and brackets, check for quotes
            bracket_content = line[line.find('['):line.find(']')+1] if ']' in line else ''
            if bracket_content and not ('"' in bracket_content or "'" in bracket_content):
                warnings.append(
                    f"Line {i}: Possible unquoted HTML in label. Quote labels with HTML tags:\n"
                    f"  {line.strip()}"
                )

    # Check for subgraphs without direction
    in_subgraph = False
    subgraph_has_direction = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('subgraph'):
            in_subgraph = True
            subgraph_has_direction = False
        elif stripped.startswith('end') and in_subgraph:
            if not subgraph_has_direction:
                warnings.append(
                    f"Line {i}: Subgraph ending without explicit direction. "
                    "Add 'direction TB' or 'direction LR' inside subgraph."
                )
            in_subgraph = False
        elif in_subgraph and 'direction' in stripped:
            subgraph_has_direction = True

    return len(warnings) == 0, warnings


def render_diagram(
    diagram_path: Path,
    output_path: Path,
    config: Optional[dict] = None,
    format: str = 'svg'
) -> Tuple[bool, str]:
    """
    Render Mermaid diagram using mermaid-cli.

    Args:
        diagram_path: Path to .mmd file
        output_path: Path for output file
        config: Optional Mermaid configuration dict
        format: Output format (svg, png, pdf)

    Returns:
        Tuple of (success, error_message)
    """
    # Create config file if provided
    config_file = None
    if config:
        config_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        )
        json.dump(config, config_file)
        config_file.close()

    try:
        cmd = [
            'npx',
            '--yes',
            '@mermaid-js/mermaid-cli',
            '-i', str(diagram_path),
            '-o', str(output_path)
        ]

        if config_file:
            cmd.extend(['-c', config_file.name])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout
            return False, f"Rendering failed:\n{error_msg}"

        return True, ""

    except subprocess.TimeoutExpired:
        return False, "Rendering timed out after 30 seconds"
    except FileNotFoundError:
        return False, "mermaid-cli not found. Install with: npm install -g @mermaid-js/mermaid-cli"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
    finally:
        if config_file:
            Path(config_file.name).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(
        description='Validate and render Mermaid diagrams',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate syntax only
  %(prog)s diagram.mmd --validate-only

  # Render to SVG
  %(prog)s diagram.mmd -o output.svg

  # Render to PNG with strict security
  %(prog)s diagram.mmd -o output.png --no-html-labels

  # Validate and render with warnings
  %(prog)s diagram.mmd -o output.svg --show-warnings
        """
    )

    parser.add_argument(
        'input',
        type=Path,
        help='Input Mermaid diagram file (.mmd)'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output file path (default: input name with .svg extension)'
    )

    parser.add_argument(
        '--format',
        choices=['svg', 'png', 'pdf'],
        default='svg',
        help='Output format (default: svg)'
    )

    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate syntax, do not render'
    )

    parser.add_argument(
        '--no-html-labels',
        action='store_true',
        help='Disable HTML label support (strict security)'
    )

    parser.add_argument(
        '--show-warnings',
        action='store_true',
        help='Show syntax warnings even if rendering succeeds'
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
            print("✅ Validation passed (with warnings)")
            return 0
        else:
            print("❌ Validation found issues")
            return 1

    # Determine output path
    output_path = args.output
    if not output_path:
        output_path = args.input.with_suffix(f'.{args.format}')

    # Create config
    config = create_mermaid_config(html_labels=not args.no_html_labels)

    # Render diagram
    print(f"Rendering {args.input} -> {output_path}...")
    success, error = render_diagram(args.input, output_path, config, args.format)

    if success:
        print(f"✅ Successfully rendered to {output_path}")
        return 0
    else:
        print(f"❌ Rendering failed:", file=sys.stderr)
        print(f"  {error}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
