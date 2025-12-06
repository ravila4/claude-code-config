#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///
"""
Find conversations that touched specific files.

Shows detailed file operation history across conversations.

Usage:
    uv run find_by_file.py "plink_merger.py"
    uv run find_by_file.py "scripts/plink_merger/*.py"
    uv run find_by_file.py "*.py" --since 2025-11-01
"""
import argparse
import fnmatch
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


def extract_file_operations(content):
    """Extract file operations from tool use blocks."""
    if not isinstance(content, list):
        return []

    operations = []
    for item in content:
        if isinstance(item, dict) and item.get('type') == 'tool_use':
            tool_name = item.get('name', '')
            tool_input = item.get('input', {})

            if tool_name in ['Read', 'Edit', 'Write', 'NotebookEdit']:
                file_path = tool_input.get('file_path') or tool_input.get('notebook_path')
                if file_path:
                    op_data = {
                        'tool': tool_name,
                        'file_path': file_path,
                        'tool_id': item.get('id', '')
                    }

                    # Add operation-specific details
                    if tool_name == 'Edit':
                        op_data['old_string'] = tool_input.get('old_string', '')[:100]
                        op_data['new_string'] = tool_input.get('new_string', '')[:100]
                    elif tool_name == 'Write':
                        content_len = len(tool_input.get('content', ''))
                        op_data['content_length'] = content_len

                    operations.append(op_data)

            elif tool_name == 'Glob':
                path = tool_input.get('path')
                pattern = tool_input.get('pattern')
                if path:
                    operations.append({
                        'tool': 'Glob',
                        'file_path': path,
                        'pattern': pattern,
                        'tool_id': item.get('id', '')
                    })

    return operations


def matches_pattern(file_path, pattern, use_glob=False):
    """Check if file path matches pattern."""
    if use_glob:
        return fnmatch.fnmatch(file_path, pattern)
    else:
        # Simple substring match (case-insensitive)
        return pattern.lower() in file_path.lower()


def search_file_operations(jsonl_path, file_pattern, use_glob=False):
    """Search a conversation for operations on matching files."""
    result = {
        'path': str(jsonl_path),
        'file_name': Path(jsonl_path).stem,
        'operations': [],
        'first_user_message': None,
        'timestamp': None
    }

    try:
        with open(jsonl_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)

                    if not result['timestamp'] and 'timestamp' in data:
                        result['timestamp'] = data['timestamp']

                    msg_type = data.get('type')
                    message = data.get('message', {})
                    content = message.get('content', '')

                    # Capture first user message
                    if msg_type == 'user' and not result['first_user_message']:
                        text = extract_text_content(content)
                        if text and not text.startswith('<'):
                            result['first_user_message'] = text[:200]

                    # Extract file operations
                    if msg_type == 'assistant':
                        ops = extract_file_operations(content)
                        for op in ops:
                            if matches_pattern(op['file_path'], file_pattern, use_glob):
                                # Get surrounding text context
                                text = extract_text_content(content)
                                op['line'] = line_num
                                op['context'] = text[:300] if text else ''
                                op['timestamp'] = data.get('timestamp')
                                result['operations'].append(op)

                except json.JSONDecodeError as e:
                    print(f"Warning: Malformed JSON at {jsonl_path}:{line_num}: {e}", file=sys.stderr)
                    continue
                except Exception as e:
                    print(f"Warning: Error at {jsonl_path}:{line_num}: {e}", file=sys.stderr)
                    continue

    except FileNotFoundError:
        print(f"Error: File not found: {jsonl_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: Could not read {jsonl_path}: {e}", file=sys.stderr)
        return None

    return result if result['operations'] else None


def format_results(results, file_pattern):
    """Format search results as markdown."""
    if not results:
        return f"No conversations found touching files matching: {file_pattern}"

    # Aggregate by file path
    files_touched = {}
    for result in results:
        for op in result['operations']:
            file_path = op['file_path']
            if file_path not in files_touched:
                files_touched[file_path] = []
            files_touched[file_path].append({
                'conversation': result['file_name'],
                'conversation_path': result['path'],
                'operation': op,
                'timestamp': result['timestamp']
            })

    output = []
    output.append(f"# File Operation History: {file_pattern}\n")
    output.append(f"Found {len(results)} conversations touching {len(files_touched)} files\n")

    # Show by file
    for file_path in sorted(files_touched.keys()):
        touches = files_touched[file_path]
        output.append(f"## `{file_path}`\n")
        output.append(f"**Touched in {len(touches)} conversations**\n")

        # Sort by timestamp
        touches.sort(key=lambda x: x['timestamp'] if x['timestamp'] else '', reverse=True)

        for touch in touches:
            op = touch['operation']
            dt_str = "unknown time"
            if touch['timestamp']:
                dt = datetime.fromisoformat(touch['timestamp'].replace('Z', '+00:00'))
                dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')

            output.append(f"### {touch['conversation']} - {dt_str}")
            output.append(f"**Operation:** {op['tool']}")
            output.append(f"**Line:** {op['line']}")

            if op['tool'] == 'Edit' and 'old_string' in op:
                output.append(f"**Change:** `{op['old_string'][:50]}...` → `{op['new_string'][:50]}...`")
            elif op['tool'] == 'Write' and 'content_length' in op:
                output.append(f"**Content:** {op['content_length']} characters")

            if op.get('context'):
                output.append(f"\n**Context:**")
                output.append(f"> {op['context'][:200]}...\n")

            output.append("")

    # Summary by conversation
    output.append("\n## Conversation Summary\n")
    for result in sorted(results, key=lambda x: x['timestamp'] if x['timestamp'] else '', reverse=True):
        dt_str = "unknown time"
        if result['timestamp']:
            dt = datetime.fromisoformat(result['timestamp'].replace('Z', '+00:00'))
            dt_str = dt.strftime('%Y-%m-%d %H:%M')

        output.append(f"### {result['file_name']} - {dt_str}")
        output.append(f"**Path:** `{result['path']}`")
        output.append(f"**Operations:** {len(result['operations'])}")

        if result['first_user_message']:
            output.append(f"**Request:** {result['first_user_message']}...")

        # Group operations by tool
        tool_counts = {}
        for op in result['operations']:
            tool_counts[op['tool']] = tool_counts.get(op['tool'], 0) + 1

        output.append(f"**Tools:** {', '.join(f'{tool}({count})' for tool, count in tool_counts.items())}\n")

    return '\n'.join(output)


def find_conversations(log_dir, since=None, until=None):
    """Find all JSONL conversation files in the log directory."""
    log_dir = Path(log_dir).expanduser()

    if not log_dir.exists():
        print(f"Error: Log directory not found: {log_dir}", file=sys.stderr)
        return []

    conversations = []
    for jsonl_file in log_dir.rglob('*.jsonl'):
        try:
            stat = jsonl_file.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)

            # Date filtering
            if since and mtime.date() < since:
                continue
            if until and mtime.date() > until:
                continue

            conversations.append((jsonl_file, mtime))
        except Exception as e:
            print(f"Warning: Could not stat {jsonl_file}: {e}", file=sys.stderr)
            continue

    return sorted(conversations, key=lambda x: x[1], reverse=True)


def main():
    parser = argparse.ArgumentParser(description='Find conversations that touched specific files')
    parser.add_argument('file_pattern', help='File path or pattern to search for')
    parser.add_argument('--glob', action='store_true',
                        help='Use glob pattern matching instead of substring')
    parser.add_argument('--since', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--until', help='End date (YYYY-MM-DD)')
    parser.add_argument('--log-dir', default='~/.claude/projects',
                        help='Log directory (default: ~/.claude/projects)')

    args = parser.parse_args()

    # Parse dates
    since = datetime.strptime(args.since, '%Y-%m-%d').date() if args.since else None
    until = datetime.strptime(args.until, '%Y-%m-%d').date() if args.until else None

    # Find conversations
    print(f"Searching for files matching: {args.file_pattern}", file=sys.stderr)
    conversations = find_conversations(args.log_dir, since, until)
    print(f"Scanning {len(conversations)} conversations...", file=sys.stderr)

    # Search each conversation
    results = []
    for conv_path, mtime in conversations:
        result = search_file_operations(conv_path, args.file_pattern, args.glob)
        if result:
            results.append(result)

    print(f"Found {len(results)} conversations with matching files\n", file=sys.stderr)

    # Format and print
    print(format_results(results, args.file_pattern))


if __name__ == "__main__":
    main()
