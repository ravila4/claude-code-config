---
name: process-monitor
description: Monitor background jobs (builds, pipelines, remote SSH commands) by polling with timed background Bash commands. This skill should be used when checking on long-running processes, waiting for jobs to complete, or polling remote servers for job status.
---

# Process Monitor

Poll background jobs using timed background Bash commands. The task-notification system handles wakeup — no user interaction required to fire.

## The Pattern

Run a single background Bash command that sleeps, then checks:

```bash
sleep 300 && docker inspect --format='{{.State.Status}}' my-build 2>&1
```

Use `run_in_background: true` on the Bash tool. When the command completes, a task-notification fires automatically. The check-command output is captured in the task output — read results directly, no extra round trip.

## Timing Strategy

**Known duration** — single sleep at the expected completion time:

```bash
# Job takes ~15 minutes
sleep 900 && ssh -o ConnectTimeout=10 user@host "batch list-jobs --status RUNNING" 2>&1
```

**Unknown duration** — escalating backoff. Set one timer, check results, set the next if not done. Use judgment on intervals based on the expected scale of the job (e.g., a compile might warrant 1m/5m/10m; a multi-hour pipeline might start at 10m/30m/60m).

## Rules

1. **One timer at a time.** Cancel stale timers with `TaskStop` before setting new ones.
2. **Append the check command to `sleep`.** Results arrive with the notification — no extra turn needed.
3. **Keep check commands short and read-only.** Status queries, not mutations.
4. **After notification fires, read results and decide:** done, failed, or set the next timer.
5. **If the check command itself fails** (e.g., SSH timeout, connection refused), treat it as "not done" and set the next timer with a shorter interval.

## Examples

### Remote job status via SSH

```bash
sleep 300 && echo "=== RUNNING ===" && ssh -o ConnectTimeout=10 user@host "batch list-jobs --status RUNNING" 2>&1 && echo "=== FAILED ===" && ssh -o ConnectTimeout=10 user@host "batch list-jobs --status FAILED" 2>&1
```

### Docker build

```bash
sleep 120 && docker inspect --format='{{.State.Status}}' my-container 2>&1
```

### Generic command completion

```bash
sleep 60 && ps -p <pid> > /dev/null 2>&1 && echo "STILL RUNNING" || echo "DONE"
```

## Anti-Patterns

| Approach | Why it fails |
|----------|-------------|
| **Agent-managed `sleep`** | Agents in background tasks skip or shorten long sleeps. Unreliable. |
| **Background loops** (`for i in 1..N; do sleep; check; done`) | Notifications only fire on task completion, not per iteration. No intermediate visibility. |
