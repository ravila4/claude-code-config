#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# ///
"""
Split SRT file into chunks for parallel processing.

Usage:
    split_srt.py <srt_file> [--chunk-size=N]

Options:
    --chunk-size=N  Number of subtitle blocks per chunk [default: 50]

Output:
    Creates <basename>.chunk0.srt, <basename>.chunk1.srt, etc.
    Prints JSON summary to stdout for easy parsing.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def count_blocks(content: str) -> int:
    """Count subtitle blocks in SRT content."""
    blocks = re.split(r'\n\n+', content.strip())
    return len([b for b in blocks if b.strip()])


def split_srt(srt_path: Path, chunk_size: int) -> dict:
    """Split SRT file into chunks and return summary."""
    content = srt_path.read_text()
    blocks = re.split(r'\n\n+', content.strip())
    blocks = [b for b in blocks if b.strip()]

    total_blocks = len(blocks)
    chunks = [blocks[i:i+chunk_size] for i in range(0, total_blocks, chunk_size)]

    base = srt_path.with_suffix('')
    chunk_files = []

    for i, chunk in enumerate(chunks):
        chunk_file = Path(f"{base}.chunk{i}.srt")
        chunk_file.write_text("\n\n".join(chunk))
        chunk_files.append({
            "file": str(chunk_file),
            "blocks": len(chunk),
            "start_block": i * chunk_size + 1,
            "end_block": min((i + 1) * chunk_size, total_blocks)
        })

    return {
        "source": str(srt_path),
        "total_blocks": total_blocks,
        "chunk_size": chunk_size,
        "num_chunks": len(chunks),
        "chunks": chunk_files
    }


def main():
    parser = argparse.ArgumentParser(description="Split SRT file into chunks")
    parser.add_argument("srt_file", type=Path, help="Input SRT file")
    parser.add_argument("--chunk-size", type=int, default=50,
                        help="Blocks per chunk (default: 50)")
    parser.add_argument("--count-only", action="store_true",
                        help="Only count blocks, don't split")
    args = parser.parse_args()

    if not args.srt_file.exists():
        print(f"Error: {args.srt_file} not found", file=sys.stderr)
        sys.exit(1)

    if args.count_only:
        content = args.srt_file.read_text()
        count = count_blocks(content)
        print(json.dumps({"file": str(args.srt_file), "blocks": count}))
    else:
        result = split_srt(args.srt_file, args.chunk_size)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
