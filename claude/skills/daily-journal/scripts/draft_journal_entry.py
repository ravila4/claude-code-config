#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///
"""
Draft journal entry from today's Claude Code activity.

Generates flexible journal entry with only relevant sections populated.

Usage:
    uv run draft_journal_entry.py
    uv run draft_journal_entry.py --date 2025-11-12
    uv run draft_journal_entry.py --mode full
    uv run draft_journal_entry.py --project /path/to/repo
"""
import argparse
import json
import subprocess
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


def find_conversations(date_str):
    """Find JSONL conversations for the specified date."""
    projects_dir = Path.home() / ".claude" / "projects"

    cmd = [
        "find", str(projects_dir), "-name", "*.jsonl",
        "-newermt", f"{date_str} 00:00:00",
        "!", "-newermt", f"{date_str} 23:59:59"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip().split('\n') if result.stdout.strip() else []


def extract_todos_from_logs(conversations):
    """Extract TodoWrite content from conversations."""
    todos = []

    for conv_path in conversations:
        try:
            with open(conv_path, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if data.get('type') == 'assistant':
                            message = data.get('message', {})
                            content = message.get('content', [])

                            if isinstance(content, list):
                                for item in content:
                                    if isinstance(item, dict) and item.get('type') == 'tool_use':
                                        if item.get('name') == 'TodoWrite':
                                            todo_list = item.get('input', {}).get('todos', [])
                                            for todo in todo_list:
                                                todos.append({
                                                    'content': todo.get('content', ''),
                                                    'status': todo.get('status', 'pending')
                                                })
                    except:
                        continue
        except:
            continue

    return todos


def extract_context_from_logs(conversations):
    """Extract initial user messages as context."""
    context_messages = []

    for conv_path in conversations:
        try:
            with open(conv_path, 'r') as f:
                user_msg_count = 0
                for line in f:
                    try:
                        data = json.loads(line)
                        if data.get('type') == 'user' and user_msg_count < 3:
                            message = data.get('message', {})
                            content = extract_text_content(message.get('content', ''))

                            # Skip system messages and interrupts
                            if content and not content.startswith('<') and not content.startswith('[Request interrupted'):
                                context_messages.append(content)
                                user_msg_count += 1
                    except:
                        continue
        except:
            continue

    return context_messages


def extract_bash_commands(conversations):
    """Extract bash commands from tool uses."""
    commands = []

    for conv_path in conversations:
        try:
            with open(conv_path, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if data.get('type') == 'assistant':
                            message = data.get('message', {})
                            content = message.get('content', [])

                            if isinstance(content, list):
                                for item in content:
                                    if isinstance(item, dict) and item.get('type') == 'tool_use':
                                        if item.get('name') == 'Bash':
                                            cmd = item.get('input', {}).get('command', '')
                                            desc = item.get('input', {}).get('description', '')
                                            if cmd and not cmd.startswith('ls ') and not cmd.startswith('cat '):
                                                commands.append({'command': cmd, 'description': desc})
                    except:
                        continue
        except:
            continue

    return commands


def extract_files_modified(conversations):
    """Extract files that were modified."""
    files = set()

    for conv_path in conversations:
        try:
            with open(conv_path, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if data.get('type') == 'assistant':
                            message = data.get('message', {})
                            content = message.get('content', [])

                            if isinstance(content, list):
                                for item in content:
                                    if isinstance(item, dict) and item.get('type') == 'tool_use':
                                        tool_name = item.get('name', '')
                                        if tool_name in ['Edit', 'Write']:
                                            file_path = item.get('input', {}).get('file_path')
                                            if file_path:
                                                files.add(file_path)
                    except:
                        continue
        except:
            continue

    return sorted(list(files))


def extract_open_questions(conversations):
    """Extract messages containing questions or uncertainty."""
    questions = []

    for conv_path in conversations:
        try:
            with open(conv_path, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if data.get('type') in ['user', 'assistant']:
                            message = data.get('message', {})
                            content = extract_text_content(message.get('content', ''))

                            # Look for questions or uncertainty markers
                            if content and ('?' in content or 'unclear' in content.lower() or 'not sure' in content.lower()):
                                # Extract just the question/uncertain statement
                                sentences = content.split('.')
                                for sent in sentences:
                                    if '?' in sent or 'unclear' in sent.lower() or 'not sure' in sent.lower():
                                        questions.append(sent.strip()[:200])
                    except:
                        continue
        except:
            continue

    return questions[:5]  # Limit to top 5


def get_git_commits(date_str, repo_path="."):
    """Get git commits for the specified date."""
    start = f"{date_str} 00:00:00"
    end = f"{date_str} 23:59:59"

    cmd = [
        "git", "-C", repo_path, "log",
        f"--since={start}", f"--until={end}",
        "--pretty=format:%h - %s"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout:
        return result.stdout.strip().split('\n')
    return []


def detect_project_focus(context_messages, files_modified):
    """Detect what project/area the day focused on."""
    # Look for project names in context
    text = ' '.join(context_messages).lower()

    # Common project indicators
    if 'plink' in text or any('plink' in f for f in files_modified):
        return "PLINK File Merging"
    if 'manifest' in text:
        return "Manifest System"
    if 'bioinformatics' in text:
        return "Bioinformatics"

    # Fallback: use most common directory in files
    if files_modified:
        dirs = [str(Path(f).parent) for f in files_modified]
        most_common = max(set(dirs), key=dirs.count) if dirs else None
        if most_common:
            return Path(most_common).name

    return None


def generate_tags(project_focus, context_messages, has_unresolved):
    """Generate appropriate tags."""
    tags = ["daily-log"]

    if project_focus:
        tags.append(project_focus.lower().replace(' ', '-'))

    # Add topic tags from context
    text = ' '.join(context_messages).lower()
    if 'test' in text or 'testing' in text:
        tags.append("testing")
    if 'bug' in text or 'error' in text or 'fix' in text:
        tags.append("debugging")
    if 'deploy' in text:
        tags.append("deployment")
    if 'refactor' in text:
        tags.append("refactoring")

    if has_unresolved:
        tags.append("unresolved")

    return tags


def draft_journal(date_str, project_path=".", mode="auto"):
    """Generate journal draft using Daily Log template structure.

    Output structure:
    - ## Summary - One-line main focus
    - ## Goals - Top-level task list with checkboxes
    - ## Notes - What happened (with project/task subsections)
    - ## Reflection - Structured bullets (what worked/didn't/questions/tomorrow)
    - ## Related - Linked project notes
    """
    # Find conversations
    conversations = find_conversations(date_str)

    if not conversations:
        return f"No conversations found for {date_str}"

    # Extract information
    todos = extract_todos_from_logs(conversations)
    context_messages = extract_context_from_logs(conversations)
    commands = extract_bash_commands(conversations)
    files_modified = extract_files_modified(conversations)
    open_questions = extract_open_questions(conversations)
    git_commits = get_git_commits(date_str, project_path)

    # Detect project and tags
    project_focus = detect_project_focus(context_messages, files_modified)
    tags = generate_tags(project_focus, context_messages, bool(open_questions))

    # Build journal entry
    output = []

    # YAML frontmatter
    output.append("---")
    output.append(f"date: {date_str}")
    output.append(f"tags: [{', '.join(tags)}]")
    output.append("---\n")

    # Summary section - one-line focus from context
    output.append("## Summary\n")
    if context_messages:
        # Extract first meaningful context message
        summary = context_messages[0][:200] if len(context_messages[0]) > 200 else context_messages[0]
        output.append(f"{summary}\n")
    else:
        output.append("*One-line: What was today's main focus?*\n")

    # Goals section (top-level)
    output.append("## Goals\n")
    if todos:
        # Group by status
        pending = [t for t in todos if t['status'] == 'pending']
        in_progress = [t for t in todos if t['status'] == 'in_progress']
        completed = [t for t in todos if t['status'] == 'completed']

        for todo in pending:
            output.append(f"- [ ] {todo['content']}")
        for todo in in_progress:
            output.append(f"- [ ] {todo['content']} (in progress)")
        for todo in completed:
            output.append(f"- [x] {todo['content']}")
        output.append("")
    else:
        output.append("- [ ] Task 1")
        output.append("- [ ] Task 2\n")

    # Notes section - what happened with project/task subsections
    output.append("## Notes\n")

    # Create project subsection if we have content
    if files_modified or git_commits or (commands and len(commands) > 2):
        if project_focus:
            output.append(f"### {project_focus}\n")
        else:
            output.append("### Technical Work\n")

        # Add git commits
        if git_commits:
            output.append("**Commits:**")
            for commit in git_commits:
                output.append(f"- {commit}")
            output.append("")

        # Add files modified
        if files_modified:
            output.append("**Files modified:**")
            for file in files_modified[:10]:  # Limit to 10
                output.append(f"- `{file}`")
            if len(files_modified) > 10:
                output.append(f"- _(and {len(files_modified) - 10} more)_")
            output.append("")

        # Add commands
        if commands and len(commands) > 2:
            output.append("**Commands:**")
            output.append("```bash")
            for cmd_info in commands[:10]:  # Limit to 10
                if cmd_info['description']:
                    output.append(f"# {cmd_info['description']}")
                output.append(cmd_info['command'])
                output.append("")
            output.append("```\n")
    else:
        output.append("*What happened today. Use subsections for different topics/projects.*\n")

    # Reflection section - structured bullets
    output.append("## Reflection\n")

    output.append("- **What worked:**")
    if mode == "full":
        output.append("- **What didn't:**")

    # Include open questions
    if open_questions:
        output.append("- **Open questions:**")
        for q in open_questions:
            output.append(f"  - {q}")
    elif mode == "full":
        output.append("- **Open questions:**")

    output.append("- **Tomorrow's focus:**")
    output.append("")

    # Related section - project links
    output.append("## Related\n")
    if project_focus:
        output.append(f"- [[{project_focus}]]")
    else:
        output.append("_Add links to related project notes_")
    output.append("")

    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='Draft journal entry from today\'s activity')
    parser.add_argument('--date', help='Date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--mode', choices=['full', 'quick', 'auto'], default='auto',
                        help='Journal mode: full (all sections), quick (minimal), auto (adaptive)')
    parser.add_argument('--project', default='.',
                        help='Git repository path (default: current directory)')
    parser.add_argument('--output', help='Output file (default: stdout)')

    args = parser.parse_args()

    # Get date
    if args.date:
        date_str = args.date
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')

    print(f"Drafting journal entry for {date_str}...", file=sys.stderr)

    # Generate draft
    journal_draft = draft_journal(date_str, args.project, args.mode)

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(journal_draft)
        print(f"Draft written to {args.output}", file=sys.stderr)
    else:
        print(journal_draft)


if __name__ == "__main__":
    main()
