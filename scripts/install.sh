#!/bin/bash

# Installation script for claude-code-agents
# Creates symlinks from this repo to ~/.claude

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "📦 Installing claude-code-agents..."
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
                echo "✓ $name already linked correctly"
                return
            fi
        fi

        echo "⚠️  $name already exists at $target"
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

    echo "→ Linking $name"
    ln -s "$source" "$target"
}

# Link agents directory
create_symlink "$REPO_DIR/claude/agents" "$CLAUDE_DIR/agents" "agents"

# Link commands directory
create_symlink "$REPO_DIR/claude/commands" "$CLAUDE_DIR/commands" "commands"

# Link config directory if it exists
if [ -d "$REPO_DIR/claude/config" ]; then
    create_symlink "$REPO_DIR/claude/config" "$CLAUDE_DIR/config" "config"
fi

# Link plugins directory if it exists
if [ -d "$REPO_DIR/claude/plugins" ]; then
    create_symlink "$REPO_DIR/claude/plugins" "$CLAUDE_DIR/plugins" "plugins"
fi

# Link skills directory if it exists
if [ -d "$REPO_DIR/claude/skills" ]; then
    create_symlink "$REPO_DIR/claude/skills" "$CLAUDE_DIR/skills" "skills"
fi

# Link scripts directory if it exists
if [ -d "$REPO_DIR/claude/scripts" ]; then
    create_symlink "$REPO_DIR/claude/scripts" "$CLAUDE_DIR/scripts" "scripts"
fi

# Link hooks directory if it exists
if [ -d "$REPO_DIR/claude/hooks" ]; then
    create_symlink "$REPO_DIR/claude/hooks" "$CLAUDE_DIR/hooks" "hooks"
fi

# Link CLAUDE.md if it exists
if [ -f "$REPO_DIR/CLAUDE.md" ]; then
    create_symlink "$REPO_DIR/claude/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md" "CLAUDE.md"
fi

# Link settings.json if it exists
if [ -f "$REPO_DIR/claude/settings.json" ]; then
    create_symlink "$REPO_DIR/claude/settings.json" "$CLAUDE_DIR/settings.json" "settings.json"
fi

# Link settings.local.json if it exists
if [ -f "$REPO_DIR/claude/settings.local.json" ]; then
    create_symlink "$REPO_DIR/claude/settings.local.json" "$CLAUDE_DIR/settings.local.json" "settings.local.json"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Your agent definitions and commands are now available in Claude Code."
echo ""
echo "To verify installation:"
echo "  ls -la ~/.claude"
echo ""
echo "To uninstall:"
echo "  ./uninstall.sh"
echo ""
