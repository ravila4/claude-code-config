#!/bin/bash

# Installation script for claude-code-config
# Creates symlinks from this repo to ~/.claude

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "Installing claude-code-config..."
echo "Repository: $REPO_DIR"
echo "Target: $CLAUDE_DIR"
echo ""

# Create ~/.claude if it doesn't exist
if [ ! -d "$CLAUDE_DIR" ]; then
    echo "Creating $CLAUDE_DIR directory..."
    mkdir -p "$CLAUDE_DIR"
fi

# Function to create symlink with backup
create_symlink() {
    local source="$1"
    local target="$2"
    local name="$3"

    if [ -e "$target" ] || [ -L "$target" ]; then
        if [ -L "$target" ]; then
            existing_link=$(readlink "$target")
            if [ "$existing_link" = "$source" ]; then
                echo "* $name already linked correctly"
                return
            fi
        fi

        echo "! $name already exists at $target"
        read -p "   Backup and replace? [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            backup="${target}.backup.$(date +%Y%m%d_%H%M%S)"
            echo "   Creating backup: $backup"
            mv "$target" "$backup"
        else
            echo "   Skipping $name"
            return
        fi
    fi

    echo "> Linking $name"
    ln -s "$source" "$target"
}

# Link directories
create_symlink "$REPO_DIR/claude/agents" "$CLAUDE_DIR/agents" "agents"
create_symlink "$REPO_DIR/claude/hooks" "$CLAUDE_DIR/hooks" "hooks"
create_symlink "$REPO_DIR/claude/skills" "$CLAUDE_DIR/skills" "skills"

# Link files
create_symlink "$REPO_DIR/claude/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md" "CLAUDE.md"
create_symlink "$REPO_DIR/claude/settings.json" "$CLAUDE_DIR/settings.json" "settings.json"

echo ""
echo "Installation complete!"
echo ""
echo "To verify: ls -la ~/.claude"
echo "To uninstall: $REPO_DIR/scripts/uninstall.sh"
echo ""
