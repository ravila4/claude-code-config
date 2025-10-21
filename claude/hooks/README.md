# Claude Code Hooks

This directory contains hooks that execute at specific points during Claude Code's operation.

## Installed Hooks

### `webfetch-post.sh` - PostToolUse Hook for WebFetch

**Purpose:** Automatically prompts memory-knowledge-keeper to extract and store patterns after documentation is fetched.

**Triggers:** After every `WebFetch` tool call

**What it does:**
1. Detects when WebFetch has completed
2. Extracts the URL and query that was asked
3. Adds contextual reminder to Claude about storing patterns
4. Suggests using memory-knowledge-keeper agent for extraction

**Why this is useful:**
- Ensures documentation findings don't get lost
- Prompts pattern extraction for official docs (0.90 confidence)
- Builds institutional knowledge automatically
- Reminds to store in `.memories/memories/` per flat-file spec

**Example output:**
```
📚 WebFetch completed for: https://pandas.pydata.org/docs/user_guide/indexing.html

Consider using memory-knowledge-keeper agent to:
- Extract patterns and best practices from this documentation
- Store them in .memories/memories/ for future reference
- Set appropriate confidence scores based on source type (official_docs: 0.90)

Query asked: "How to properly assign values to DataFrame subsets"
```

## Hook Configuration

Hooks are configured in `config.json`:

```json
{
  "postToolUse": [
    {
      "matcher": "WebFetch",
      "command": "claude/hooks/webfetch-post.sh"
    }
  ]
}
```

## Activating Hooks

To use these hooks in your Claude Code session:

### Option 1: Symlink to global hooks directory
```bash
# Create global hooks directory if it doesn't exist
mkdir -p ~/.claude/hooks

# Symlink this config
ln -sf $(pwd)/claude/hooks/config.json ~/.claude/hooks/config.json
ln -sf $(pwd)/claude/hooks/webfetch-post.sh ~/.claude/hooks/webfetch-post.sh
```

### Option 2: Copy to global hooks directory
```bash
cp claude/hooks/config.json ~/.claude/hooks/
cp claude/hooks/webfetch-post.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/webfetch-post.sh
```

### Option 3: Add to settings.local.json
Add to `~/.claude/settings.local.json`:
```json
{
  "hooks": {
    "postToolUse": [
      {
        "matcher": "WebFetch",
        "command": "/absolute/path/to/claude-code-agents/claude/hooks/webfetch-post.sh"
      }
    ]
  }
}
```

## Hook Development

### PostToolUse Hook Format

Hooks receive JSON on stdin:
```json
{
  "tool_name": "WebFetch",
  "parameters": {
    "url": "https://example.com",
    "prompt": "What is X?"
  },
  "result": "..."
}
```

Hooks must output JSON:
```json
{
  "decision": null,  // or "block" to prevent tool execution
  "reason": null,    // explanation if blocking
  "hookSpecificOutput": {
    "additionalContext": "message to add to Claude's context"
  }
}
```

### Testing Hooks

```bash
# Test hook with sample input
echo '{"tool_name":"WebFetch","parameters":{"url":"https://pandas.pydata.org","prompt":"test"}}' | \
  ./claude/hooks/webfetch-post.sh
```

## References

- [Claude Code Hooks Documentation](https://docs.claude.com/en/docs/claude-code/hooks)
- [Flat-File Memory Spec](../../docs/CLAUDE_FLAT_FILE_MEMORY_SPEC.md)
- [memory-knowledge-keeper agent](../agents/memory-knowledge-keeper.md)
