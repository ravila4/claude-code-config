#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///
"""
Extract thinking blocks and tool usage from JSONL session logs.

Shows Claude's reasoning process and what tools were invoked.

Usage:
    uv run extract_thinking.py <session.jsonl>
"""
import json
import sys

def extract_thinking_and_tools(filepath):
    """Extract thinking blocks and tool usage."""
    with open(filepath, 'r') as f:
        messages = [json.loads(line) for line in f if line.strip()]

    tool_uses = []
    thinking_moments = []

    for msg in messages:
        msg_content = msg.get('message', {}).get('content', [])
        if isinstance(msg_content, list):
            for block in msg_content:
                if isinstance(block, dict):
                    if block.get('type') == 'thinking':
                        think_text = block.get('thinking', '')[:300]
                        thinking_moments.append(think_text)
                    elif block.get('type') == 'tool_use':
                        tool_name = block.get('name', 'unknown')
                        tool_uses.append(tool_name)

    # Print summary
    print("THINKING BLOCKS AND TOOL USAGE")
    print("=" * 80 + "\n")

    print(f"Tools used: {set(tool_uses)}")
    print(f"Tool usage counts:")
    for tool in set(tool_uses):
        count = tool_uses.count(tool)
        print(f"  - {tool}: {count}x")

    print(f"\nTotal thinking moments: {len(thinking_moments)}\n")

    # Show first few thinking moments to understand reasoning
    print("=" * 80)
    print("KEY INSIGHTS / REALIZATIONS:")
    print("=" * 80)

    for i, think in enumerate(thinking_moments[:5], 1):
        print(f"\n[Insight {i}]")
        print(think)
        if len(think) >= 300:
            print("...")
        print()

    if len(thinking_moments) > 5:
        print(f"\n(... and {len(thinking_moments) - 5} more thinking moments)\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_thinking.py <session.jsonl>", file=sys.stderr)
        sys.exit(1)

    try:
        extract_thinking_and_tools(sys.argv[1])
    except FileNotFoundError:
        print(f"Error: File not found: {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in log file", file=sys.stderr)
        sys.exit(1)
