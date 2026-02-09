#!/bin/bash
# Toggle AFK mode for Claude Code's AFK controller hook.
# Usage: toggle-afk.sh [on|off]

AFK_FLAG="/tmp/claude-afk"

case "${1:-}" in
    on)
        touch "$AFK_FLAG"
        echo "AFK mode ON"
        ;;
    off)
        rm -f "$AFK_FLAG"
        echo "AFK mode OFF"
        ;;
    *)
        if [ -f "$AFK_FLAG" ]; then
            rm -f "$AFK_FLAG"
            echo "AFK mode OFF"
        else
            touch "$AFK_FLAG"
            echo "AFK mode ON"
        fi
        ;;
esac
