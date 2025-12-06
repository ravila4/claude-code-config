#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///
"""
Search Claude Code conversation logs by keyword, date, and file.

Usage:
    uv run search_conversations.py --keyword "plink manifest"
    uv run search_conversations.py --keyword "refactor" --since 2025-11-01
    uv run search_conversations.py --file "plink_merger.py"
    uv run search_conversations.py --keyword "checkpoint" --file "manifest" --limit 5
"""
import argparse
import json
import sys
from collections import defaultdict
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


def extract_file_paths(tool_use_block):
    """Extract file paths from tool use blocks."""
    if not isinstance(tool_use_block, dict):
        return []

    tool_name = tool_use_block.get('name', '')
    input_data = tool_use_block.get('input', {})

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


def score_relevance(text, keywords):
    """Score text relevance based on keyword matches."""
    if not keywords or not text:
        return 0

    text_lower = text.lower()
    score = 0

    for keyword in keywords:
        keyword_lower = keyword.lower()
        # Count occurrences
        count = text_lower.count(keyword_lower)
        score += count * 10

        # Bonus for exact word match (not substring)
        if f' {keyword_lower} ' in f' {text_lower} ':
            score += 5

    return score


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


def search_conversation(jsonl_path, keywords=None, file_filter=None):
    """Search a single conversation file for keywords and files."""
    results = {
        'path': str(jsonl_path),
        'matches': [],
        'score': 0,
        'files_touched': set(),
        'message_count': 0,
        'first_user_message': None
    }

    try:
        with open(jsonl_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)

                    # Count messages
                    if data.get('type') in ['user', 'assistant']:
                        results['message_count'] += 1

                        message = data.get('message', {})
                        content = message.get('content', '')

                        # Extract first user message for preview
                        if data.get('type') == 'user' and not results['first_user_message']:
                            text = extract_text_content(content)
                            results['first_user_message'] = text[:200]

                        # Keyword search in message content
                        if keywords:
                            text = extract_text_content(content)
                            score = score_relevance(text, keywords)
                            if score > 0:
                                results['matches'].append({
                                    'line': line_num,
                                    'type': data.get('type'),
                                    'score': score,
                                    'preview': text[:300]
                                })
                                results['score'] += score

                        # Extract file paths from tool use
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and item.get('type') == 'tool_use':
                                    paths = extract_file_paths(item)
                                    results['files_touched'].update(paths)

                except json.JSONDecodeError as e:
                    print(f"Warning: Malformed JSON at {jsonl_path}:{line_num}: {e}", file=sys.stderr)
                    continue
                except Exception as e:
                    print(f"Warning: Error processing {jsonl_path}:{line_num}: {e}", file=sys.stderr)
                    continue

    except FileNotFoundError:
        print(f"Error: File not found: {jsonl_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: Could not read {jsonl_path}: {e}", file=sys.stderr)
        return None

    # File filter matching
    if file_filter:
        file_matches = [f for f in results['files_touched'] if file_filter.lower() in f.lower()]
        if not file_matches:
            return None  # Skip if file filter doesn't match

    # Skip if no matches found
    if keywords and results['score'] == 0:
        return None

    # Convert set to list for JSON serialization
    results['files_touched'] = list(results['files_touched'])

    return results


def format_results(results, limit=10):
    """Format search results as markdown."""
    if not results:
        return "No conversations found matching the criteria."

    output = []
    output.append(f"# Search Results\n")
    output.append(f"Found {len(results)} conversations\n")

    for i, result in enumerate(results[:limit], 1):
        output.append(f"## {i}. {Path(result['path']).stem}")
        output.append(f"**Path:** `{result['path']}`")
        output.append(f"**Score:** {result['score']}")
        output.append(f"**Messages:** {result['message_count']}")

        if result['first_user_message']:
            output.append(f"\n**First request:** {result['first_user_message']}...")

        if result['files_touched']:
            output.append(f"\n**Files touched ({len(result['files_touched'])}):**")
            for file_path in sorted(result['files_touched'])[:10]:
                output.append(f"- `{file_path}`")
            if len(result['files_touched']) > 10:
                output.append(f"- *(... and {len(result['files_touched']) - 10} more)*")

        if result['matches']:
            output.append(f"\n**Top matches ({len(result['matches'])}):**")
            for match in sorted(result['matches'], key=lambda x: x['score'], reverse=True)[:3]:
                output.append(f"- Line {match['line']} ({match['type']}, score {match['score']})")
                output.append(f"  > {match['preview'][:200]}...")

        output.append("")

    if len(results) > limit:
        output.append(f"\n*Showing {limit} of {len(results)} results. Use --limit to see more.*")

    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='Search Claude Code conversation logs')
    parser.add_argument('--keyword', help='Keywords to search for (space-separated)')
    parser.add_argument('--file', help='Filter by file path substring')
    parser.add_argument('--since', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--until', help='End date (YYYY-MM-DD)')
    parser.add_argument('--limit', type=int, default=10, help='Max results to show (default: 10)')
    parser.add_argument('--log-dir', default='~/.claude/projects', help='Log directory (default: ~/.claude/projects)')

    args = parser.parse_args()

    # Parse keywords
    keywords = args.keyword.split() if args.keyword else None

    # Parse dates
    since = datetime.strptime(args.since, '%Y-%m-%d').date() if args.since else None
    until = datetime.strptime(args.until, '%Y-%m-%d').date() if args.until else None

    # Find conversations
    print(f"Searching conversations in {args.log_dir}...", file=sys.stderr)
    conversations = find_conversations(args.log_dir, since, until)
    print(f"Found {len(conversations)} conversation files", file=sys.stderr)

    # Search each conversation
    results = []
    for conv_path, mtime in conversations:
        result = search_conversation(conv_path, keywords, args.file)
        if result:
            results.append(result)

    # Sort by score (descending)
    results.sort(key=lambda x: x['score'], reverse=True)

    # Format and print results
    print(format_results(results, args.limit))


if __name__ == "__main__":
    main()
