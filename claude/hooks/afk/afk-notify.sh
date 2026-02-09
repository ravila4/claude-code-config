#!/bin/bash
# AFK notification hook for Claude Code.
# Fires on Notification events (permission_prompt, elicitation_dialog).
# When AFK, speaks an alert so the user knows Claude needs attention.

set -euo pipefail

AFK_FLAG="/tmp/claude-afk"

# Not AFK -> do nothing
[ -f "$AFK_FLAG" ] || exit 0

# Extract notification details from stdin
INPUT=$(cat)
TYPE=$(echo "$INPUT" | jq -r '.notification_type // "unknown"')
MESSAGE=$(echo "$INPUT" | jq -r '.message // "Claude needs your attention"')

case "$TYPE" in
    permission_prompt)
        speak "Hey, I need permission for something. Check your screen." &
        ;;
    elicitation_dialog)
        speak "I have a question for you. Check your screen." &
        ;;
    *)
        speak "I need your attention. Check your screen." &
        ;;
esac

exit 0
