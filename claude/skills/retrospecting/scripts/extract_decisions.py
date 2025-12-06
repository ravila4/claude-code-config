#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///
"""
Extract design decisions and clarifying questions from Claude Code conversations.

Finds AskUserQuestion tool uses and the user's responses to track decision-making.

Usage:
    uv run extract_decisions.py <conversation.jsonl>
    uv run extract_decisions.py --search-all --since 2025-11-01
    uv run extract_decisions.py --search-all --topic "architecture"
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


def find_ask_user_question_tools(content):
    """Find AskUserQuestion tool use blocks in message content."""
    if not isinstance(content, list):
        return []

    questions = []
    for item in content:
        if isinstance(item, dict) and item.get('type') == 'tool_use':
            if item.get('name') == 'AskUserQuestion':
                questions.append({
                    'tool_id': item.get('id', ''),
                    'input': item.get('input', {})
                })
    return questions


def extract_decisions(jsonl_path):
    """Extract all AskUserQuestion interactions from a conversation."""
    decisions = []
    messages = []

    try:
        # First pass: collect all messages
        with open(jsonl_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                    messages.append({
                        'line': line_num,
                        'type': data.get('type'),
                        'timestamp': data.get('timestamp'),
                        'message': data.get('message', {})
                    })
                except json.JSONDecodeError as e:
                    print(f"Warning: Malformed JSON at {jsonl_path}:{line_num}: {e}", file=sys.stderr)
                    continue
                except Exception as e:
                    print(f"Warning: Error at {jsonl_path}:{line_num}: {e}", file=sys.stderr)
                    continue

        # Second pass: find AskUserQuestion tools and their responses
        for i, msg in enumerate(messages):
            if msg['type'] == 'assistant':
                content = msg['message'].get('content', [])
                ask_tools = find_ask_user_question_tools(content)

                for ask_tool in ask_tools:
                    # Extract the questions from the tool input
                    questions_data = ask_tool['input'].get('questions', [])

                    # Find the user's response (look ahead for tool_result then user message)
                    tool_id = ask_tool['tool_id']
                    user_response = None

                    # Look for the user message that contains answers
                    for j in range(i + 1, min(i + 5, len(messages))):
                        if messages[j]['type'] == 'user':
                            # Check if this message has the answers
                            msg_content = messages[j]['message'].get('content', '')
                            # AskUserQuestion responses are in the tool input's 'answers' field
                            # But we need to find the actual user response message
                            text = extract_text_content(msg_content)
                            if text and not text.startswith('[Request interrupted'):
                                user_response = text
                                break

                    # Also check the tool_result for the answers field
                    for j in range(i + 1, min(i + 3, len(messages))):
                        if messages[j]['type'] == 'tool_result':
                            # The actual answers might be in a subsequent AskUserQuestion call
                            pass

                    # Look for answers in the questions_data itself (they get populated there)
                    answers = ask_tool['input'].get('answers', {})

                    decisions.append({
                        'line': msg['line'],
                        'timestamp': msg['timestamp'],
                        'questions': questions_data,
                        'answers': answers,
                        'user_response_text': user_response
                    })

    except FileNotFoundError:
        print(f"Error: File not found: {jsonl_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: Could not read {jsonl_path}: {e}", file=sys.stderr)
        return None

    return {
        'path': str(jsonl_path),
        'file_name': Path(jsonl_path).stem,
        'decisions': decisions
    }


def format_decisions(result):
    """Format extracted decisions as markdown."""
    if not result or not result['decisions']:
        return f"No decisions found in {result['path'] if result else 'conversation'}"

    output = []
    output.append(f"# Design Decisions: {result['file_name']}\n")
    output.append(f"**File:** `{result['path']}`\n")
    output.append(f"**Total decision points:** {len(result['decisions'])}\n")

    for i, decision in enumerate(result['decisions'], 1):
        output.append(f"## Decision Point {i}")

        if decision['timestamp']:
            dt = datetime.fromisoformat(decision['timestamp'].replace('Z', '+00:00'))
            output.append(f"**Time:** {dt.strftime('%Y-%m-%d %H:%M:%S')}")

        output.append(f"**Line:** {decision['line']}\n")

        # Show the questions
        output.append("### Questions Asked\n")
        for j, q_data in enumerate(decision['questions'], 1):
            question = q_data.get('question', 'Unknown question')
            header = q_data.get('header', '')
            options = q_data.get('options', [])

            output.append(f"**Q{j}:** {question}")
            if header:
                output.append(f"*Category: {header}*")

            if options:
                output.append("\n**Options:**")
                for opt in options:
                    label = opt.get('label', '')
                    desc = opt.get('description', '')
                    output.append(f"- **{label}**: {desc}")
            output.append("")

        # Show the answers
        if decision['answers']:
            output.append("### User's Answers\n")
            for q_text, answer in decision['answers'].items():
                output.append(f"**Q:** {q_text}")
                output.append(f"**A:** {answer}\n")

        if decision['user_response_text']:
            output.append("### User Response Context\n")
            preview = decision['user_response_text'][:400]
            if len(decision['user_response_text']) > 400:
                preview += "..."
            output.append(f"> {preview}\n")

        output.append("---\n")

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
    parser = argparse.ArgumentParser(description='Extract design decisions from conversations')
    parser.add_argument('conversation', nargs='?', help='Path to conversation JSONL file')
    parser.add_argument('--search-all', action='store_true',
                        help='Search all conversations in log directory')
    parser.add_argument('--topic', help='Filter by topic keyword in questions/answers')
    parser.add_argument('--since', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--until', help='End date (YYYY-MM-DD)')
    parser.add_argument('--log-dir', default='~/.claude/projects',
                        help='Log directory (default: ~/.claude/projects)')

    args = parser.parse_args()

    if not args.conversation and not args.search_all:
        parser.error("Must provide either conversation file or --search-all")

    # Parse dates
    since = datetime.strptime(args.since, '%Y-%m-%d').date() if args.since else None
    until = datetime.strptime(args.until, '%Y-%m-%d').date() if args.until else None

    if args.search_all:
        # Search all conversations
        print(f"Searching for decisions in {args.log_dir}...", file=sys.stderr)
        conversations = find_conversations(args.log_dir, since, until)
        print(f"Found {len(conversations)} conversation files", file=sys.stderr)

        all_decisions = []
        for conv_path, mtime in conversations:
            result = extract_decisions(conv_path)
            if result and result['decisions']:
                # Filter by topic if specified
                if args.topic:
                    filtered_decisions = []
                    topic_lower = args.topic.lower()
                    for decision in result['decisions']:
                        # Check if topic appears in questions or answers
                        text = json.dumps(decision).lower()
                        if topic_lower in text:
                            filtered_decisions.append(decision)
                    if filtered_decisions:
                        result['decisions'] = filtered_decisions
                        all_decisions.append(result)
                else:
                    all_decisions.append(result)

        # Print summary
        print(f"\n# Design Decisions Summary\n")
        print(f"Found {len(all_decisions)} conversations with decisions\n")

        for result in all_decisions:
            print(f"## {result['file_name']}")
            print(f"**Path:** `{result['path']}`")
            print(f"**Decision points:** {len(result['decisions'])}\n")

        # Print detailed view for each
        for result in all_decisions:
            print("\n" + "="*80 + "\n")
            print(format_decisions(result))

    else:
        # Single conversation
        print(f"Extracting decisions from: {args.conversation}", file=sys.stderr)
        result = extract_decisions(args.conversation)

        if result:
            # Filter by topic if specified
            if args.topic and result['decisions']:
                filtered = []
                topic_lower = args.topic.lower()
                for decision in result['decisions']:
                    text = json.dumps(decision).lower()
                    if topic_lower in text:
                        filtered.append(decision)
                result['decisions'] = filtered

            print(format_decisions(result))
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
