#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# ///
"""
Apply common transcription replacements to SRT files.

Usage:
    apply_replacements.py <srt_file> [--output=<file>] [--in-place]

Applies replacements from transcription_replacements.json for high-frequency
transcription errors. Run this before or after Haiku correction to catch
systematic issues.
"""

import argparse
import json
import re
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "transcription"
REPLACEMENTS_FILE = CONFIG_DIR / "replacements.json"


def load_replacements() -> dict:
    """Load replacement dictionary."""
    if not REPLACEMENTS_FILE.exists():
        print(f"Warning: {REPLACEMENTS_FILE} not found", file=sys.stderr)
        return {"case_sensitive": {}, "case_insensitive": {}, "phrases": {}}
    return json.loads(REPLACEMENTS_FILE.read_text())


def apply_replacements(content: str, replacements: dict) -> tuple[str, list[dict]]:
    """Apply all replacements and return (new_content, list of changes)."""
    changes = []

    # Apply phrase replacements first (longer matches)
    for original, replacement in replacements.get("phrases", {}).items():
        if original in content:
            count = content.count(original)
            content = content.replace(original, replacement)
            changes.append({"original": original, "replacement": replacement, "count": count})

    # Apply case-sensitive replacements
    for original, replacement in replacements.get("case_sensitive", {}).items():
        pattern = r'\b' + re.escape(original) + r'\b'
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes.append({"original": original, "replacement": replacement, "count": len(matches)})

    # Apply case-insensitive replacements
    for original, replacement in replacements.get("case_insensitive", {}).items():
        pattern = r'\b' + re.escape(original) + r'\b'
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            changes.append({"original": original, "replacement": replacement, "count": len(matches)})

    return content, changes


def main():
    parser = argparse.ArgumentParser(description="Apply transcription replacements")
    parser.add_argument("srt_file", type=Path, help="Input SRT file")
    parser.add_argument("--output", "-o", type=Path, help="Output file (default: stdout)")
    parser.add_argument("--in-place", "-i", action="store_true", help="Modify file in place")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress change summary")
    args = parser.parse_args()

    if not args.srt_file.exists():
        print(f"Error: {args.srt_file} not found", file=sys.stderr)
        sys.exit(1)

    replacements = load_replacements()
    content = args.srt_file.read_text()
    new_content, changes = apply_replacements(content, replacements)

    # Output
    if args.in_place:
        args.srt_file.write_text(new_content)
        output_dest = str(args.srt_file)
    elif args.output:
        args.output.write_text(new_content)
        output_dest = str(args.output)
    else:
        print(new_content)
        output_dest = "stdout"

    # Summary
    if not args.quiet and changes:
        total = sum(c["count"] for c in changes)
        print(f"\n# Applied {total} replacements to {output_dest}:", file=sys.stderr)
        for c in changes:
            print(f"#   {c['original']} -> {c['replacement']} ({c['count']}x)", file=sys.stderr)


if __name__ == "__main__":
    main()
