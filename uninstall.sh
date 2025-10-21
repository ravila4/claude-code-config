#!/bin/bash

# Uninstallation script for claude-code-agents
# Removes symlinks from ~/.claude

set -e

CLAUDE_DIR="$HOME/.claude"

echo "🗑️  Uninstalling claude-code-agents..."
echo ""

# Function to remove symlink if it exists
remove_symlink() {
    local target="$1"
    local name="$2"

    if [ -L "$target" ]; then
        echo "✗ Removing $name symlink"
        rm "$target"
    elif [ -e "$target" ]; then
        echo "⚠️  $name exists but is not a symlink, skipping"
    else
        echo "  $name not found, skipping"
    fi
}

# Remove symlinks
remove_symlink "$CLAUDE_DIR/agents" "agents"
remove_symlink "$CLAUDE_DIR/commands" "commands"
remove_symlink "$CLAUDE_DIR/config" "config"
remove_symlink "$CLAUDE_DIR/plugins" "plugins"
remove_simlink "$CLAUDE_DIR/skills" "skills"
remove_symlink "$CLAUDE_DIR/scripts" "scripts"
remove_symlink "$CLAUDE_DIR/hooks" "hooks"
remove_symlink "$CLAUDE_DIR/CLAUDE.md" "CLAUDE.md"
remove_symlink "$CLAUDE_DIR/settings.json" "settings.json"
remove_symlink "$CLAUDE_DIR/settings.local.json" "settings.local.json"

echo ""
echo "✅ Uninstallation complete!"
echo ""
echo "Note: Backup files (.backup.*) were not removed."
echo "You can safely delete them manually if no longer needed."
echo ""
