#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///
"""
Generate detailed summary of a single Claude Code conversation.

Usage:
    uv run summarize_conversation.py <path/to/conversation.jsonl>
    uv run summarize_conversation.py <path/to/conversation.jsonl> --format obsidian
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def extract_text_content(content):
    """Extract text from various content structures."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    texts.append(item.get('text', ''))
                elif item.get('type') == 'thinking':
                    texts.append(item.get('thinking', ''))
            elif isinstance(item, str):
                texts.append(item)
        return ' '.join(texts)
    return str(content)


def extract_tool_uses(content):
    """Extract tool use blocks from message content."""
    tools = []
    if not isinstance(content, list):
        return tools

    for item in content:
        if isinstance(item, dict) and item.get('type') == 'tool_use':
            tools.append({
                'name': item.get('name', 'unknown'),
                'id': item.get('id', ''),
                'input': item.get('input', {})
            })
    return tools


def extract_file_paths(tool_use):
    """Extract file paths from tool use."""
    tool_name = tool_use.get('name', '')
    input_data = tool_use.get('input', {})

    paths = []
    if tool_name in ['Read', 'Edit', 'Write', 'NotebookEdit']:
        if 'file_path' in input_data:
            paths.append(input_data['file_path'])
        if 'notebook_path' in input_data:
            paths.append(input_data['notebook_path'])
    elif tool_name == 'Glob':
        if 'path' in input_data and input_data['path']:
            paths.append(input_data['path'])

    return paths


def extract_thinking(content):
    """Extract thinking blocks from message content."""
    if not isinstance(content, list):
        return []

    thinking_blocks = []
    for item in content:
        if isinstance(item, dict) and item.get('type') == 'thinking':
            thinking_blocks.append(item.get('thinking', ''))
    return thinking_blocks


def analyze_conversation(jsonl_path):
    """Analyze a conversation file and extract key information."""
    summary = {
        'path': str(jsonl_path),
        'file_name': Path(jsonl_path).stem,
        'user_messages': [],
        'assistant_messages': [],
        'thinking_count': 0,
        'tool_uses': [],
        'files_touched': set(),
        'errors': [],
        'timestamp': None
    }

    try:
        with open(jsonl_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)

                    # Extract timestamp from first message
                    if not summary['timestamp'] and 'timestamp' in data:
                        summary['timestamp'] = data['timestamp']

                    msg_type = data.get('type')
                    message = data.get('message', {})
                    content = message.get('content', '')

                    if msg_type == 'user':
                        text = extract_text_content(content)
                        if text:
                            summary['user_messages'].append({
                                'line': line_num,
                                'text': text
                            })

                    elif msg_type == 'assistant':
                        text = extract_text_content(content)
                        thinking = extract_thinking(content)
                        tools = extract_tool_uses(content)

                        summary['thinking_count'] += len(thinking)
                        summary['tool_uses'].extend(tools)

                        # Extract file paths from tools
                        for tool in tools:
                            paths = extract_file_paths(tool)
                            summary['files_touched'].update(paths)

                        if text:
                            summary['assistant_messages'].append({
                                'line': line_num,
                                'text': text,
                                'thinking_blocks': len(thinking),
                                'tools': [t['name'] for t in tools]
                            })

                except json.JSONDecodeError as e:
                    summary['errors'].append(f"Line {line_num}: Malformed JSON - {e}")
                    continue
                except Exception as e:
                    summary['errors'].append(f"Line {line_num}: Processing error - {e}")
                    continue

    except FileNotFoundError:
        print(f"Error: File not found: {jsonl_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: Could not read {jsonl_path}: {e}", file=sys.stderr)
        return None

    # Convert set to list
    summary['files_touched'] = sorted(list(summary['files_touched']))

    return summary


def format_summary(summary, format_type='standard'):
    """Format conversation summary as markdown."""
    if not summary:
        return "Error: Could not analyze conversation"

    output = []

    # Header
    if format_type == 'obsidian':
        output.append(f"# Conversation: {summary['file_name']}\n")
        output.append("---")
        output.append(f"date: {summary['timestamp'][:10] if summary['timestamp'] else 'unknown'}")
        output.append(f"type: claude-conversation")
        output.append(f"tags: [conversation, claude-code]")
        output.append("---\n")
    else:
        output.append(f"# Conversation Summary: {summary['file_name']}\n")

    if summary['timestamp']:
        dt = datetime.fromisoformat(summary['timestamp'].replace('Z', '+00:00'))
        output.append(f"**Date:** {dt.strftime('%Y-%m-%d %H:%M:%S')}")

    output.append(f"**File:** `{summary['path']}`")
    output.append("")

    # Overview
    output.append("## Overview\n")
    output.append(f"- User messages: {len(summary['user_messages'])}")
    output.append(f"- Assistant responses: {len(summary['assistant_messages'])}")
    output.append(f"- Thinking blocks: {summary['thinking_count']}")
    output.append(f"- Tools used: {len(summary['tool_uses'])}")
    output.append(f"- Files touched: {len(summary['files_touched'])}")
    output.append("")

    # User Journey
    if summary['user_messages']:
        output.append("## User Journey\n")
        output.append("What was requested:\n")
        for i, msg in enumerate(summary['user_messages'], 1):
            preview = msg['text'][:200]
            if len(msg['text']) > 200:
                preview += "..."
            output.append(f"{i}. {preview}")
        output.append("")

    # Files Touched
    if summary['files_touched']:
        output.append("## Files Touched\n")
        for file_path in summary['files_touched']:
            if format_type == 'obsidian':
                output.append(f"- `[[{file_path}]]`")
            else:
                output.append(f"- `{file_path}`")
        output.append("")

    # Tool Usage
    if summary['tool_uses']:
        output.append("## Tool Usage\n")
        tool_counts = {}
        for tool in summary['tool_uses']:
            tool_name = tool['name']
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1

        for tool_name, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True):
            output.append(f"- **{tool_name}**: {count} times")
        output.append("")

    # Key Exchanges
    if summary['assistant_messages']:
        output.append("## Key Exchanges\n")
        # Show first few assistant responses with context
        for i, msg in enumerate(summary['assistant_messages'][:5], 1):
            output.append(f"### Exchange {i}\n")
            preview = msg['text'][:300]
            if len(msg['text']) > 300:
                preview += "..."
            output.append(preview)
            if msg['tools']:
                output.append(f"\n*Tools: {', '.join(msg['tools'])}*")
            if msg['thinking_blocks'] > 0:
                output.append(f"*Thinking blocks: {msg['thinking_blocks']}*")
            output.append("")

        if len(summary['assistant_messages']) > 5:
            output.append(f"*... and {len(summary['assistant_messages']) - 5} more exchanges*\n")

    # Errors
    if summary['errors']:
        output.append("## Errors Encountered\n")
        for error in summary['errors'][:10]:
            output.append(f"- {error}")
        if len(summary['errors']) > 10:
            output.append(f"- *... and {len(summary['errors']) - 10} more errors*")
        output.append("")

    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='Summarize a Claude Code conversation')
    parser.add_argument('conversation', help='Path to conversation JSONL file')
    parser.add_argument('--format', choices=['standard', 'obsidian'], default='standard',
                        help='Output format (default: standard)')

    args = parser.parse_args()

    # Analyze conversation
    print(f"Analyzing conversation: {args.conversation}", file=sys.stderr)
    summary = analyze_conversation(args.conversation)

    if not summary:
        sys.exit(1)

    # Format and print summary
    print(format_summary(summary, args.format))


if __name__ == "__main__":
    main()
