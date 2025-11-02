---
description: "Generate and play a TTS audio summary of recent work"
argumentHint: "optional: custom summary text (otherwise I'll summarize recent context)"
tools:
  - Task
  - Read
---

# TTS Status Notification

Use Task tool with subagent_type="tts-status-notifier" to generate a casual, conversational audio summary.

If provided with custom text in $ARGUMENTS, use that for creating context.
Otherwise, use our recent conversation as context.

Don't return any output text. Just execute the Task tool to play the audio notification.
