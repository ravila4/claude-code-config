#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///
"""
List Claude Code conversations with metadata for quick browsing.

Usage:
    uv run list_conversations.py
    uv run list_conversations.py --since 2025-11-01
    uv run list_conversations.py --project plink_processing
    uv run list_conversations.py --limit 20
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
            elif isinstance(item, str):
                texts.append(item)
        return ' '.join(texts)
    return str(content)


def quick_scan_conversation(jsonl_path):
    """Quickly scan a conversation for basic metadata."""
    metadata = {
        'path': str(jsonl_path),
        'file_name': Path(jsonl_path).stem,
        'message_count': 0,
        'user_messages': 0,
        'assistant_messages': 0,
        'tool_uses': 0,
        'first_user_message': None,
        'timestamp': None,
        'file_size': 0,
        'error': None
    }

    try:
        # Get file size
        metadata['file_size'] = jsonl_path.stat().st_size
        metadata['mtime'] = datetime.fromtimestamp(jsonl_path.stat().st_mtime)

        # Quick scan (don't read entire file for large conversations)
        line_count = 0
        max_lines = 100  # Only scan first 100 lines for efficiency

        with open(jsonl_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if line_num > max_lines:
                    break

                try:
                    data = json.loads(line)
                    line_count += 1

                    if not metadata['timestamp'] and 'timestamp' in data:
                        metadata['timestamp'] = data['timestamp']

                    msg_type = data.get('type')

                    if msg_type == 'user':
                        metadata['user_messages'] += 1
                        if not metadata['first_user_message']:
                            message = data.get('message', {})
                            content = message.get('content', '')
                            text = extract_text_content(content)
                            # Skip system messages
                            if text and not text.startswith('<') and not text.startswith('[Request interrupted'):
                                metadata['first_user_message'] = text[:150]

                    elif msg_type == 'assistant':
                        metadata['assistant_messages'] += 1
                        # Count tool uses
                        message = data.get('message', {})
                        content = message.get('content', [])
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and item.get('type') == 'tool_use':
                                    metadata['tool_uses'] += 1

                except json.JSONDecodeError:
                    continue
                except Exception:
                    continue

        metadata['message_count'] = line_count

    except Exception as e:
        metadata['error'] = str(e)

    return metadata


def find_conversations(log_dir, since=None, until=None, project=None):
    """Find all JSONL conversation files with optional filters."""
    log_dir = Path(log_dir).expanduser()

    if not log_dir.exists():
        print(f"Error: Log directory not found: {log_dir}", file=sys.stderr)
        return []

    conversations = []

    # If project specified, narrow search
    if project:
        search_pattern = f"*{project}*/*.jsonl"
    else:
        search_pattern = "*/*.jsonl"

    for jsonl_file in log_dir.glob(search_pattern):
        try:
            stat = jsonl_file.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)

            # Date filtering
            if since and mtime.date() < since:
                continue
            if until and mtime.date() > until:
                continue

            conversations.append(jsonl_file)
        except Exception as e:
            print(f"Warning: Could not stat {jsonl_file}: {e}", file=sys.stderr)
            continue

    return conversations


def format_size(bytes_size):
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f}GB"


def format_list(conversations_metadata, show_paths=False):
    """Format conversation list as markdown table."""
    if not conversations_metadata:
        return "No conversations found."

    # Sort by modification time (newest first)
    conversations_metadata.sort(key=lambda x: x['mtime'], reverse=True)

    output = []
    output.append(f"# Conversations ({len(conversations_metadata)} total)\n")

    for i, meta in enumerate(conversations_metadata, 1):
        # Format timestamp
        if meta['mtime']:
            dt_str = meta['mtime'].strftime('%Y-%m-%d %H:%M')
        else:
            dt_str = 'unknown'

        output.append(f"## {i}. {meta['file_name']}")
        output.append(f"**Date:** {dt_str}")
        output.append(f"**Size:** {format_size(meta['file_size'])}")
        output.append(f"**Messages:** {meta['message_count']} ({meta['user_messages']} user, {meta['assistant_messages']} assistant)")
        output.append(f"**Tools:** {meta['tool_uses']} uses")

        if meta['first_user_message']:
            output.append(f"\n**First request:** {meta['first_user_message']}...")

        if show_paths:
            output.append(f"\n**Path:** `{meta['path']}`")

        if meta['error']:
            output.append(f"\n**Error:** {meta['error']}")

        output.append("")

    return '\n'.join(output)


def format_compact(conversations_metadata):
    """Format as compact list (one line per conversation)."""
    if not conversations_metadata:
        return "No conversations found."

    conversations_metadata.sort(key=lambda x: x['mtime'], reverse=True)

    output = []
    output.append(f"# Conversations ({len(conversations_metadata)} total)\n")
    output.append("| Date | File Name | Msgs | Tools | First Request |")
    output.append("|------|-----------|------|-------|---------------|")

    for meta in conversations_metadata:
        dt_str = meta['mtime'].strftime('%Y-%m-%d %H:%M') if meta['mtime'] else 'unknown'
        first_msg = meta['first_user_message'][:50] + "..." if meta['first_user_message'] else "N/A"
        first_msg = first_msg.replace('|', '\\|')  # Escape pipes for markdown table

        output.append(f"| {dt_str} | {meta['file_name'][:30]} | {meta['message_count']} | {meta['tool_uses']} | {first_msg} |")

    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='List Claude Code conversations')
    parser.add_argument('--since', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--until', help='End date (YYYY-MM-DD)')
    parser.add_argument('--project', help='Filter by project name substring')
    parser.add_argument('--limit', type=int, help='Limit number of results')
    parser.add_argument('--compact', action='store_true', help='Show compact table format')
    parser.add_argument('--show-paths', action='store_true', help='Show full file paths')
    parser.add_argument('--log-dir', default='~/.claude/projects',
                        help='Log directory (default: ~/.claude/projects)')

    args = parser.parse_args()

    # Parse dates
    since = datetime.strptime(args.since, '%Y-%m-%d').date() if args.since else None
    until = datetime.strptime(args.until, '%Y-%m-%d').date() if args.until else None

    # Find conversations
    print(f"Searching conversations in {args.log_dir}...", file=sys.stderr)
    if args.project:
        print(f"Filtering by project: {args.project}", file=sys.stderr)

    conversations = find_conversations(args.log_dir, since, until, args.project)
    print(f"Found {len(conversations)} conversation files", file=sys.stderr)

    # Apply limit
    if args.limit:
        conversations = conversations[:args.limit]

    # Scan each conversation
    print(f"Scanning conversations...", file=sys.stderr)
    metadata_list = []
    for conv_path in conversations:
        meta = quick_scan_conversation(conv_path)
        metadata_list.append(meta)

    # Format and print
    if args.compact:
        print(format_compact(metadata_list))
    else:
        print(format_list(metadata_list, args.show_paths))


if __name__ == "__main__":
    main()
