#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///
"""
Extract conversation flow with automatic keyword tagging.

Identifies key moments like INSIGHT, ACTION, TESTING, PROBLEM, COMPLETION.

Usage:
    uv run conversation_flow.py <session.jsonl>
"""
import json
import re
import sys

def analyze_conversation_flow(filepath):
    """Extract conversation with keyword highlighting."""
    conversation_flow = []

    with open(filepath, 'r') as f:
        for line in f:
            try:
                data = json.loads(line)
                if 'message' in data:
                    msg = data['message']
                    role = msg.get('role', '')

                    content = msg.get('content', [])
                    text = ''

                    # Extract text content
                    if isinstance(content, str):
                        text = content
                    elif isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict) and block.get('type') == 'text':
                                text = block.get('text', '')
                                break

                    conversation_flow.append({
                        'role': role,
                        'text': text,
                        'timestamp': data.get('timestamp', '')
                    })
            except:
                pass

    # Print the story with keyword highlighting
    print("CONVERSATION FLOW WITH KEY MOMENTS")
    print("=" * 80 + "\n")

    for i, turn in enumerate(conversation_flow):
        if turn['role'] == 'user':
            print(f"\n[USER #{i//2 + 1}]: {turn['text'][:300]}")
            if len(turn['text']) > 300:
                print("    ...")

        elif turn['role'] == 'assistant':
            text = turn['text']

            # Look for key phrases and tag them
            tags = []

            if 'memory' in text.lower() or 'scale' in text.lower():
                tags.append("→ INSIGHT: Memory/scaling concern")
            if 'refactor' in text.lower():
                tags.append("→ ACTION: Refactoring code")
            if 'test' in text.lower() and ('passing' in text.lower() or 'failed' in text.lower() or 'error' in text.lower()):
                tags.append("→ TESTING: Running tests")
            if 'commit' in text.lower():
                tags.append("→ COMPLETION: Committing changes")

            # Extract error messages
            errors = re.findall(r'(Error|Failed|Exception|FAILED).*', text, re.IGNORECASE)
            if errors:
                tags.append(f"→ PROBLEM: {errors[0][:100]}")

            # Print tags
            for tag in tags:
                print(f"  {tag}")

            # Print preview
            if text:
                preview = text[:400].replace('\n', ' ')
                print(f"  Assistant: {preview}...")
                if len(text) > 400:
                    print("    ...")

    print("\n" + "=" * 80)
    print(f"Total turns: {len(conversation_flow)}")
    print("=" * 80)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 conversation_flow.py <session.jsonl>", file=sys.stderr)
        sys.exit(1)

    analyze_conversation_flow(sys.argv[1])
