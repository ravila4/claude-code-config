# Claude Code Hooks

This directory contains hooks that execute at specific points during Claude Code's operation.

## Installed Hooks

No hooks are currently installed.

## Hook Development

### PostToolUse Hook Format

Hooks receive JSON on stdin:
```json
{
  "tool_name": "ToolName",
  "parameters": {
    "param1": "value1"
  },
  "result": "..."
}
```

Hooks must output JSON:
```json
{
  "decision": null,
  "reason": null,
  "hookSpecificOutput": {
    "additionalContext": "message to add to Claude's context"
  }
}
```

## References

- [Claude Code Hooks Documentation](https://docs.claude.com/en/docs/claude-code/hooks)
