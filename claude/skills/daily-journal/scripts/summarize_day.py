#!/usr/bin/env -S uv run --script
# /// script
# dependencies = []
# ///
"""
Summarize the day's development activity from git commits and total recall.

Git-first approach: commits across repos are the most reliable "what did I do" signal.
Total recall (Contextify) discovers additional projects touched via conversation logs.

Usage:
    uv run summarize_day.py                    # Today's summary
    uv run summarize_day.py --date 2026-01-20  # Specific date
    uv run summarize_day.py --git-only         # Skip total recall (faster)
    uv run summarize_day.py --output ~/journal.md
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class Commit:
    """A git commit."""

    hash: str
    message: str
    files_changed: int = 0


@dataclass
class RepoActivity:
    """Activity in a single repository."""

    name: str
    path: Path
    commits: list[Commit] = field(default_factory=list)

    @property
    def commit_count(self) -> int:
        return len(self.commits)

    @property
    def total_files_changed(self) -> int:
        return sum(c.files_changed for c in self.commits)


@dataclass
class DayActivity:
    """All activity for a given day."""

    date: str
    repos: dict[str, RepoActivity] = field(default_factory=dict)
    session_projects: dict[str, int] = field(default_factory=dict)  # project -> session count

    @property
    def main_project(self) -> str | None:
        """Determine main project by commit count, then session count."""
        if not self.repos:
            return None

        # Score by commits (weighted heavily) + sessions
        scores: dict[str, float] = {}
        for name, repo in self.repos.items():
            scores[name] = repo.commit_count * 10 + repo.total_files_changed

        # Add session scores
        for project, count in self.session_projects.items():
            # Match session project names to repo names
            for name in self.repos:
                if project.lower() in name.lower() or name.lower() in project.lower():
                    scores[name] = scores.get(name, 0) + count * 5

        if not scores:
            return None
        return max(scores, key=lambda k: scores[k])

    @property
    def side_projects(self) -> list[str]:
        """All repos except main project."""
        main = self.main_project
        return [name for name in self.repos if name != main]


def run_command(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout, result.stderr


def scan_git_repos(projects_dir: Path, date_str: str) -> dict[str, RepoActivity]:
    """Find all repos in projects_dir with commits on given date."""
    repos: dict[str, RepoActivity] = {}

    if not projects_dir.exists():
        return repos

    for item in projects_dir.iterdir():
        if not item.is_dir():
            continue

        git_dir = item / ".git"
        if not git_dir.exists():
            continue

        commits = get_commits_for_date(item, date_str)
        if commits:
            repos[item.name] = RepoActivity(name=item.name, path=item, commits=commits)

    return repos


def get_commits_for_date(repo_path: Path, date_str: str) -> list[Commit]:
    """Get commits from a repo for a specific date."""
    start = f"{date_str} 00:00:00"
    end = f"{date_str} 23:59:59"

    # Get commits with stats
    cmd = [
        "git",
        "log",
        f"--since={start}",
        f"--until={end}",
        "--pretty=format:%h|%s",
        "--shortstat",
    ]

    returncode, stdout, _ = run_command(cmd, cwd=repo_path)
    if returncode != 0 or not stdout.strip():
        return []

    commits: list[Commit] = []
    lines = stdout.strip().split("\n")

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        if "|" in line:
            # This is a commit line
            parts = line.split("|", 1)
            if len(parts) == 2:
                hash_val, message = parts
                files_changed = 0

                # Look for stat line
                if i + 1 < len(lines):
                    stat_line = lines[i + 1].strip()
                    if "file" in stat_line and "changed" in stat_line:
                        # Parse "N file(s) changed"
                        try:
                            files_changed = int(stat_line.split()[0])
                        except (ValueError, IndexError):
                            pass
                        i += 1

                commits.append(Commit(hash=hash_val.strip(), message=message.strip(), files_changed=files_changed))
        i += 1

    return commits


def discover_sessions(date_str: str) -> dict[str, int]:
    """Use contextify-query to find projects with sessions on the date.

    Returns dict of project_name -> session_count.
    """
    sessions: dict[str, int] = {}

    # Check if contextify-query is available
    returncode, _, _ = run_command(["which", "contextify-query"])
    if returncode != 0:
        return sessions

    # Parse target date
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return sessions

    # Get activity for the past few days to ensure we capture the target date
    cmd = ["contextify-query", "activity", "--days", "7", "--json"]

    returncode, stdout, _ = run_command(cmd)
    if returncode != 0 or not stdout.strip():
        return sessions

    try:
        data = json.loads(stdout)
        entries = data.get("data", [])

        for item in entries:
            entry = item.get("entry", {})
            project_name = item.get("projectName", "")

            if not project_name:
                continue

            # Check timestamp matches target date
            timestamp = entry.get("timestamp", 0)
            if timestamp:
                entry_date = datetime.fromtimestamp(timestamp).date()
                if entry_date == target_date:
                    sessions[project_name] = sessions.get(project_name, 0) + 1
    except (json.JSONDecodeError, KeyError, TypeError):
        pass

    return sessions


def generate_tags(main_project: str | None, repos: dict[str, RepoActivity]) -> list[str]:
    """Generate tags for the journal entry."""
    tags = ["daily-log"]

    if main_project:
        # Normalize project name to tag format
        tag = main_project.lower().replace("_", "-").replace(" ", "-")
        if tag not in tags:
            tags.append(tag)

    # Add tags based on commit messages
    all_messages = []
    for repo in repos.values():
        all_messages.extend([c.message.lower() for c in repo.commits])

    message_text = " ".join(all_messages)
    if any(word in message_text for word in ["test", "testing", "spec"]):
        tags.append("testing")
    if any(word in message_text for word in ["fix", "bug", "error"]):
        tags.append("debugging")
    if any(word in message_text for word in ["refactor", "cleanup", "clean up"]):
        tags.append("refactoring")

    return tags


def format_summary(activity: DayActivity) -> str:
    """Generate one-line summary of the day's focus."""
    main = activity.main_project
    if not main:
        return "*One-line: What was today's main focus?*"

    main_repo = activity.repos.get(main)
    if not main_repo:
        return f"Worked on {main}"

    commit_count = main_repo.commit_count
    if commit_count == 1:
        # Use the commit message as summary
        return main_repo.commits[0].message
    else:
        return f"Worked on {main} ({commit_count} commits)"


def format_project_section(repo: RepoActivity) -> list[str]:
    """Format a project section with commits."""
    lines: list[str] = []

    if repo.commits:
        lines.append("**Commits:**")
        for commit in repo.commits:
            lines.append(f"- {commit.message}")
        lines.append("")

    if repo.total_files_changed > 0:
        lines.append(f"**Files changed:** {repo.total_files_changed}")
        lines.append("")

    return lines


def generate_journal(activity: DayActivity) -> str:
    """Generate markdown journal entry following the template structure."""
    lines: list[str] = []

    # YAML frontmatter
    tags = generate_tags(activity.main_project, activity.repos)
    lines.append("---")
    lines.append(f"date: {activity.date}")
    lines.append("tags:")
    for tag in tags:
        lines.append(f"  - {tag}")
    lines.append("---")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(format_summary(activity))
    lines.append("")

    # Goals - extract from commits or placeholder
    lines.append("## Goals")
    lines.append("")
    if activity.repos:
        # Mark completed tasks from commits
        all_commits = []
        for repo in activity.repos.values():
            all_commits.extend(repo.commits)
        if all_commits:
            for commit in all_commits[:5]:  # Top 5 commits as goals
                lines.append(f"- [x] {commit.message}")
        lines.append("- [ ] *Add remaining tasks*")
    else:
        lines.append("- [ ] Task 1")
        lines.append("- [ ] Task 2")
    lines.append("")

    # Notes
    lines.append("## Notes")
    lines.append("")
    lines.append("*What happened today. Use subsections for different topics/projects.*")
    lines.append("*Link to [[projects]] and [[concepts]] as you mention them.*")
    lines.append("")

    # Main project section
    main = activity.main_project
    if main and main in activity.repos:
        main_repo = activity.repos[main]
        lines.append(f"### {main}")
        lines.append("")
        lines.extend(format_project_section(main_repo))

    # Side projects
    side_projects = activity.side_projects
    if side_projects:
        lines.append("### Side Projects")
        lines.append("")
        for name in side_projects:
            repo = activity.repos[name]
            lines.append(f"**{name}:** {repo.commit_count} commit(s)")
            if repo.commits:
                lines.append(f"  - {repo.commits[0].message}")
        lines.append("")

    # Fallback if no activity
    if not activity.repos:
        lines.append("### Project/Task Name (if applicable)")
        lines.append("")
        lines.append("*Technical details, decisions, code snippets, investigation work.*")
        lines.append("")

    # Reflection
    lines.append("## Reflection")
    lines.append("")
    lines.append("- **What worked:**")
    lines.append("- **What didn't:**")
    lines.append("- **Open questions:**")
    lines.append("- **Tomorrow's focus:**")
    lines.append("")

    # Related
    lines.append("## Related")
    lines.append("")
    if main:
        lines.append(f"- [[{main}]]")
    for name in side_projects[:3]:  # Top 3 side projects
        lines.append(f"- [[{name}]]")
    if not activity.repos:
        lines.append("- [[Project links]]")
        lines.append("- [[Concept notes]]")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize development activity from git commits and total recall"
    )
    parser.add_argument(
        "--date",
        help="Date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--projects-dir",
        default=str(Path.home() / "Projects"),
        help="Directory containing git repositories (default: ~/Projects)",
    )
    parser.add_argument(
        "--git-only",
        action="store_true",
        help="Skip total recall, use only git data (faster)",
    )
    parser.add_argument(
        "--output",
        help="Output file (default: stdout)",
    )

    args = parser.parse_args()

    # Get date
    date_str = args.date or datetime.now().strftime("%Y-%m-%d")
    projects_dir = Path(args.projects_dir)

    print(f"Summarizing activity for {date_str}...", file=sys.stderr)

    # Scan git repos
    print(f"Scanning git repos in {projects_dir}...", file=sys.stderr)
    repos = scan_git_repos(projects_dir, date_str)
    print(f"Found {len(repos)} repo(s) with activity", file=sys.stderr)

    # Discover sessions via total recall
    sessions: dict[str, int] = {}
    if not args.git_only:
        print("Discovering sessions via total recall...", file=sys.stderr)
        sessions = discover_sessions(date_str)
        if sessions:
            print(f"Found sessions in {len(sessions)} project(s)", file=sys.stderr)

    # Build activity summary
    activity = DayActivity(date=date_str, repos=repos, session_projects=sessions)

    # Generate journal
    journal = generate_journal(activity)

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(journal)
        print(f"Written to {output_path}", file=sys.stderr)
    else:
        print(journal)


if __name__ == "__main__":
    main()
