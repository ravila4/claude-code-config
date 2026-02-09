#!/bin/bash
# AFK stop hook for Claude Code.
# When AFK flag is set, blocks Claude from stopping and instructs it to
# speak a summary and listen for voice reply.
#
# Reads JSON from stdin (Claude Code Stop hook format).
# Outputs block JSON to stdout when AFK and not already in a hook loop.

set -euo pipefail

AFK_FLAG="/tmp/claude-afk"

# No AFK flag -> let Claude stop normally
[ -f "$AFK_FLAG" ] || exit 0

# Read stdin and extract stop_hook_active
INPUT=$(cat)
STOP_HOOK_ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false')

# Already in a hook loop -> let Claude stop (prevent infinite cycle)
[ "$STOP_HOOK_ACTIVE" = "true" ] && exit 0

# AFK and first stop -> block and instruct Claude to speak + listen
cat <<'EOF'
{
  "decision": "block",
  "reason": "User is AFK. Do the following:\n1. Compose a brief, conversational voice summary of what you just did or what you need.\n2. Run speak and listen as a SINGLE chained command: `speak \"your summary here\" && listen`\n   - speak will voice the summary via TTS\n   - listen will play a chime and capture the user's voice reply\n   - Do NOT pass any flags to listen -- defaults are correct\n3. If you got a reply (non-empty stdout from listen), continue working on whatever they said.\n4. If no reply (empty output), stop.\n5. If the user says they're back, run `rm /tmp/claude-afk` to disable AFK mode."
}
EOF
