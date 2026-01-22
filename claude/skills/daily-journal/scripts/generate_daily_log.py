#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///
"""
Orchestration script to generate daily development journal.

Combines log analysis with git history to create Obsidian entry.

Usage:
    uv run generate_daily_log.py [--date YYYY-MM-DD] [--output FILE]

If --date not specified, uses today's date.
If --output not specified, prints to stdout.
"""
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
import json

def find_debug_logs(date_str):
    """Find all debug logs for the specified date."""
    debug_dir = Path.home() / ".claude" / "debug"

    # Use find command to get logs from that date
    cmd = [
        "find", str(debug_dir), "-name", "*.txt",
        "-newermt", f"{date_str} 00:00:00",
        "!", "-newermt", f"{date_str} 23:59:59"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip().split('\n') if result.stdout.strip() else []

def find_jsonl_logs(date_str):
    """Find JSONL logs for the specified date."""
    projects_dir = Path.home() / ".claude" / "projects"

    cmd = [
        "find", str(projects_dir), "-name", "*.jsonl",
        "-newermt", f"{date_str} 00:00:00",
        "!", "-newermt", f"{date_str} 23:59:59"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip().split('\n') if result.stdout.strip() else []

def get_git_commits(date_str, repo_path="."):
    """Get git commits for the specified date."""
    start = f"{date_str} 00:00:00"
    end = f"{date_str} 23:59:59"

    cmd = [
        "git", "-C", repo_path, "log",
        f"--since={start}", f"--until={end}",
        "--stat", "--pretty=format:%n%h - %s%n%b"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else "No git commits found."

def analyze_debug_log(log_path):
    """Quick analysis of debug log for session type."""
    try:
        with open(log_path, 'r') as f:
            content = f.read()

        interactions = content.count("UserCommandMessage")
        tools = content.count("executePreToolHooks")
        files = content.count("Tracked file modification")
        permissions = content.count("Permission suggestions")

        # Classify session
        if interactions >= 3 and files >= 1:
            session_type = "ACTIVE"
        elif permissions >= 1:
            session_type = "BLOCKED"
        else:
            session_type = "MINIMAL"

        return {
            'path': log_path,
            'interactions': interactions,
            'tools': tools,
            'files': files,
            'permissions': permissions,
            'type': session_type
        }
    except Exception as e:
        return {'path': log_path, 'error': str(e)}

def generate_report(date_str, repo_path="."):
    """Generate daily development journal report."""
    print(f"# Daily Development Journal - {date_str}")
    print()

    # Find logs
    debug_logs = find_debug_logs(date_str)
    jsonl_logs = find_jsonl_logs(date_str)

    print(f"## Session Summary")
    print()
    print(f"- Debug logs found: {len([l for l in debug_logs if l])}")
    print(f"- JSONL logs found: {len([l for l in jsonl_logs if l])}")
    print()

    # Analyze debug logs
    if debug_logs and debug_logs[0]:
        print("## Sessions")
        print()
        for log_path in debug_logs:
            if not log_path:
                continue
            analysis = analyze_debug_log(log_path)
            if 'error' not in analysis:
                print(f"### {Path(log_path).stem}")
                print(f"- Type: **{analysis['type']}**")
                print(f"- Interactions: {analysis['interactions']}")
                print(f"- Tools: {analysis['tools']}")
                print(f"- Files modified: {analysis['files']}")
                if analysis['permissions'] > 0:
                    print(f"- Permissions requested: {analysis['permissions']}")
                print()

    # Git commits
    print("## Git Activity")
    print()
    commits = get_git_commits(date_str, repo_path)
    if commits and commits != "No git commits found.":
        print("```")
        print(commits)
        print("```")
    else:
        print("No git commits found.")
    print()

    # Instructions for manual analysis
    print("## Next Steps")
    print()
    print("Run detailed analysis on each ACTIVE session:")
    print()
    for log_path in debug_logs:
        if not log_path:
            continue
        analysis = analyze_debug_log(log_path)
        if 'error' not in analysis and analysis['type'] == 'ACTIVE':
            jsonl_name = Path(log_path).stem
            print(f"```bash")
            print(f"# Extract user journey")
            print(f"python3 scripts/extract_user_journey.py ~/.claude/projects/*/{jsonl_name}.jsonl")
            print()
            print(f"# Extract thinking and tools")
            print(f"python3 scripts/extract_thinking.py ~/.claude/projects/*/{jsonl_name}.jsonl")
            print()
            print(f"# Conversation flow")
            print(f"python3 scripts/conversation_flow.py ~/.claude/projects/*/{jsonl_name}.jsonl")
            print(f"```")
            print()

def main():
    parser = argparse.ArgumentParser(description='Generate daily development journal')
    parser.add_argument('--date', help='Date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--output', help='Output file (default: stdout)')
    parser.add_argument('--repo', default='.', help='Git repository path (default: current directory)')

    args = parser.parse_args()

    # Get date
    if args.date:
        date_str = args.date
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')

    # Generate report
    if args.output:
        import sys
        original_stdout = sys.stdout
        with open(args.output, 'w') as f:
            sys.stdout = f
            generate_report(date_str, args.repo)
            sys.stdout = original_stdout
        print(f"Report written to {args.output}")
    else:
        generate_report(date_str, args.repo)

if __name__ == "__main__":
    main()
