#!/bin/bash

# PostToolUse hook for WebFetch
# Automatically prompts memory-knowledge-keeper to extract and store patterns from fetched documentation
#
# This hook triggers after every WebFetch call and suggests saving findings to .memories/

# Read the hook input (stdin contains JSON with tool info)
INPUT=$(cat)

# Extract tool name, URL, and response from the JSON input
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
URL=$(echo "$INPUT" | jq -r '.parameters.url // empty')
PROMPT=$(echo "$INPUT" | jq -r '.parameters.prompt // empty')

# Only process WebFetch calls
if [ "$TOOL_NAME" != "WebFetch" ]; then
  exit 0
fi

# Return hook output as JSON
cat <<EOF
{
  "decision": null,
  "reason": null,
  "hookSpecificOutput": {
    "additionalContext": "📚 WebFetch completed for: $URL

Consider using memory-knowledge-keeper agent to:
- Extract patterns and best practices from this documentation
- Store them in .memories/memories/ for future reference
- Set appropriate confidence scores based on source type (official_docs: 0.90)

Query asked: \"$PROMPT\"

If this documentation contains reusable patterns, coding standards, or API usage examples, please extract and store them for the project."
  }
}
EOF
