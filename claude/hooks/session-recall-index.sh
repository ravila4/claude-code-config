#!/bin/bash
# Auto-index Claude Code sessions into session-recall on session stop.
# Runs sr index (incremental, idempotent) to pick up the just-completed session.

set -euo pipefail

# Only run if sr is installed
command -v sr &>/dev/null || exit 0

# Run index in background so we don't delay Claude stopping
sr index >> /tmp/session-recall-index.log 2>&1 &
