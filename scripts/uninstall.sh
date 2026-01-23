#!/bin/bash

# Uninstallation script for claude-code-config
# Removes symlinks from ~/.claude

set -e

CLAUDE_DIR="$HOME/.claude"

echo "Uninstalling claude-code-config..."
echo ""

# Function to remove symlink if it exists
remove_symlink() {
    local target="$1"
    local name="$2"

    if [ -L "$target" ]; then
        echo "x Removing $name symlink"
        rm "$target"
    elif [ -e "$target" ]; then
        echo "! $name exists but is not a symlink, skipping"
    else
        echo "  $name not found, skipping"
    fi
}

# Remove symlinks
remove_symlink "$CLAUDE_DIR/agents" "agents"
remove_symlink "$CLAUDE_DIR/hooks" "hooks"
remove_symlink "$CLAUDE_DIR/skills" "skills"
remove_symlink "$CLAUDE_DIR/CLAUDE.md" "CLAUDE.md"
remove_symlink "$CLAUDE_DIR/settings.json" "settings.json"

echo ""
echo "Uninstallation complete!"
echo ""
echo "Note: Backup files (.backup.*) were not removed."
echo ""
