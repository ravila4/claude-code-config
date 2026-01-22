---
name: git-worktrees
description: Creates isolated git worktrees with smart directory selection and safety verification for feature work needing workspace isolation
---

# Git Worktrees

## Overview

Create isolated git worktrees for parallel branch development without disrupting your main workspace. Follows systematic directory selection and safety verification to ensure reliable isolation.

**Core Principle:** "Systematic directory selection + safety verification = reliable isolation."

## When to Use

Use git worktrees when you need to:
- Work on multiple branches simultaneously
- Test code in isolation without stashing
- Review PRs without disrupting current work
- Run long builds on one branch while coding on another
- Maintain production hotfix while developing features

## Workflow

### Phase 1: Directory Selection

Follow this hierarchy to determine worktree storage location:

1. **Check for `.worktrees/`** (preferred hidden location)
2. **Check for `worktrees/`** (alternative visible location)
3. **Consult CLAUDE.md** for user preferences
4. **Ask user** with this prompt:
   > No worktree directory found. Where should I create worktrees?
   > 1. `.worktrees/` (project-local, hidden)
   > 2. `~/.config/agents/worktrees/<project-name>/` (global location)
   >
   > Which would you prefer?

**Never assume** directory location without checking existing setup and CLAUDE.md first.

### Phase 2: Safety Verification

**For project-local directories:**

1. Verify target directory appears in `.gitignore`
2. If absent:
   - Add entry to `.gitignore`
   - Commit immediately: `git add .gitignore && git commit -m "Add worktrees directory to .gitignore"`
3. Only proceed after verification

**For global directories** (`~/.config/agents/worktrees`):
- Skip .gitignore check (directory is outside project)

**Never skip** .gitignore verification for project-local worktrees to prevent accidental repository pollution.

### Phase 3: Creation & Setup

1. **Detect project name** via git config or directory name
2. **Create worktree:**
   ```bash
   git worktree add <directory>/<branch-name> -b <branch-name>
   ```
3. **Auto-detect and install dependencies:**
   - Node.js: Check for `package.json` → run `npm install` or `yarn install`
   - Python: Check for `requirements.txt`, `pyproject.toml`, `Pipfile` → run appropriate installer
   - Rust: Check for `Cargo.toml` → run `cargo build`
   - Go: Check for `go.mod` → run `go mod download`
4. **Run baseline tests** to verify clean state:
   - npm: `npm test`
   - Python: `pytest` or `python -m pytest`
   - Rust: `cargo test`
   - Go: `go test ./...`
5. **Report readiness:**
   - Worktree location
   - Branch name
   - Dependency installation status
   - Test results

**Never proceed** with failing baseline tests without explicit user permission.

## Common Commands

**List worktrees:**
```bash
git worktree list
```

**Remove worktree:**
```bash
git worktree remove <directory>
```

**Prune deleted worktrees:**
```bash
git worktree prune
```

## Directory Structure Examples

**Project-local (hidden):**
```
my-project/
├── .git/
├── .worktrees/
│   ├── feature-auth/
│   └── bugfix-login/
├── .gitignore          # Contains: .worktrees/
└── src/
```

**Project-local (visible):**
```
my-project/
├── .git/
├── worktrees/
│   ├── feature-auth/
│   └── bugfix-login/
├── .gitignore          # Contains: worktrees/
└── src/
```

**Global:**
```
~/.config/agents/worktrees/
├── my-project/
│   ├── feature-auth/
│   └── bugfix-login/
└── other-project/
    └── hotfix-critical/
```

## Safety Checklist

Before creating worktree:
- [ ] Checked for existing `.worktrees/` or `worktrees/` directories
- [ ] Consulted CLAUDE.md for user preferences
- [ ] Verified .gitignore contains worktree directory (if project-local)
- [ ] Committed .gitignore changes if modified

After creating worktree:
- [ ] Dependencies installed successfully
- [ ] Baseline tests pass
- [ ] Reported location and status to user

## Best Practices

**Do:**
- Use descriptive branch names for worktrees
- Clean up worktrees when done (`git worktree remove`)
- Keep worktree directories out of version control
- Run baseline tests to verify clean state

**Don't:**
- Create worktrees without .gitignore verification
- Assume directory preferences without checking CLAUDE.md
- Proceed with failing tests without permission
- Commit worktree directories to the repository

## Integration with Other Workflows

**Works with:**
- TDD workflow (separate worktree for test development)
- Code review (review PR in isolated worktree)