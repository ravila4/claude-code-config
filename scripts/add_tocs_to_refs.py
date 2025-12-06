#!/usr/bin/env python3
"""Add table of contents to reference files >100 lines."""

import re
from pathlib import Path
from typing import List, Tuple


def extract_headers(content: str) -> List[Tuple[str, str]]:
    """Extract H2 headers and their anchor links."""
    headers = []
    for line in content.split('\n'):
        match = re.match(r'^## (.+)$', line)
        if match:
            title = match.group(1)
            # Create anchor link (lowercase, spaces to hyphens, remove special chars)
            anchor = title.lower()
            anchor = re.sub(r'[^\w\s-]', '', anchor)
            anchor = re.sub(r'\s+', '-', anchor)
            headers.append((title, anchor))
    return headers


def has_toc(content: str) -> bool:
    """Check if content already has a TOC."""
    lower = content.lower()
    return 'table of contents' in lower or '## contents' in lower


def create_toc(headers: List[Tuple[str, str]]) -> str:
    """Create TOC markdown from headers."""
    if not headers:
        return ""

    toc_lines = ["## Contents\n"]
    for title, anchor in headers:
        toc_lines.append(f"- [{title}](#{anchor})")

    return "\n".join(toc_lines) + "\n"


def insert_toc(content: str, toc: str) -> str:
    """Insert TOC at the beginning, after any intro paragraph."""
    lines = content.split('\n')

    # Find first H2 header
    first_h2_idx = None
    for i, line in enumerate(lines):
        if line.startswith('## '):
            first_h2_idx = i
            break

    if first_h2_idx is None:
        # No H2 headers, add at beginning
        return toc + "\n" + content

    # Insert TOC before first H2
    lines.insert(first_h2_idx, toc)
    return '\n'.join(lines)


def process_file(file_path: Path) -> bool:
    """Add TOC to a reference file if needed. Return True if modified."""
    with open(file_path, 'r') as f:
        content = f.read()

    # Check line count
    line_count = len(content.split('\n'))
    if line_count <= 100:
        return False

    # Check if already has TOC
    if has_toc(content):
        print(f"  ✓ Already has TOC: {file_path.name}")
        return False

    # Extract headers
    headers = extract_headers(content)
    if len(headers) < 2:
        print(f"  ⊘ Too few headers (<2): {file_path.name}")
        return False

    # Create and insert TOC
    toc = create_toc(headers)
    new_content = insert_toc(content, toc)

    # Write back
    with open(file_path, 'w') as f:
        f.write(new_content)

    print(f"  ✓ Added TOC ({len(headers)} sections): {file_path.name}")
    return True


def main():
    """Process all reference files in skills."""
    skills_dir = Path("claude/skills")
    ref_files = sorted(skills_dir.glob("*/references/*.md"))

    modified_count = 0
    for ref_file in ref_files:
        skill_name = ref_file.parent.parent.name
        line_count = len(ref_file.read_text().split('\n'))

        if line_count > 100:
            print(f"{skill_name}/{ref_file.parent.name}/{ref_file.name} ({line_count} lines)")
            if process_file(ref_file):
                modified_count += 1

    print(f"\n✅ Modified {modified_count} files")


if __name__ == "__main__":
    main()
