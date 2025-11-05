#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///
"""
Extract user messages from JSONL session logs.

Shows what the user actually asked Claude to do throughout the session.

Usage:
    uv run extract_user_journey.py <session.jsonl>

Or inline:
    sed -n '9,100p' session.jsonl | uv run extract_user_journey.py
"""
import json
import sys

def extract_user_journey(file_handle):
    """Extract and print user messages from JSONL log."""
    user_message_count = 0

    for line in file_handle:
        if not line.strip():
            continue

        try:
            msg = json.loads(line)
            role = msg.get('message', {}).get('role')

            if role == 'user':
                user_message_count += 1
                content = msg.get('message', {}).get('content', '')

                # Handle both string and list content formats
                if isinstance(content, str):
                    print(f"\n[USER #{user_message_count}]: {content[:600]}\n")
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get('type') == 'text':
                            text = block.get('text', '')
                            print(f"\n[USER #{user_message_count}]: {text[:600]}\n")
                            break
        except json.JSONDecodeError:
            continue
        except Exception as e:
            print(f"Warning: Error processing line: {e}", file=sys.stderr)
            continue

    if user_message_count == 0:
        print("No user messages found in log.", file=sys.stderr)
    else:
        print(f"\n{'='*80}")
        print(f"Total user messages: {user_message_count}")
        print(f"{'='*80}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # File provided as argument
        with open(sys.argv[1], 'r') as f:
            extract_user_journey(f)
    else:
        # Read from stdin (for piping)
        extract_user_journey(sys.stdin)
