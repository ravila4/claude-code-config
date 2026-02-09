#!/bin/bash
# Auto-index Claude Code sessions into session-recall on session stop.
# Runs sr index (incremental, idempotent) to pick up the just-completed session.

set -euo pipefail

SR="/Users/ricardoavila/Projects/session-log/.venv/bin/sr"

# Only run if sr is installed
[ -x "$SR" ] || exit 0

# Run index in background so we don't delay Claude stopping
"$SR" index >> /tmp/session-recall-index.log 2>&1 &
