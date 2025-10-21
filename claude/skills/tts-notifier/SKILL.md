---
name: tts-notifier
description: Provides audio notifications for completed tasks using text-to-speech. Use when long-running tasks complete (debugging, research, builds) or when users explicitly request audio updates. Creates brief, casual verbal summaries optimized for TTS playback.
---

# TTS Notifier

## Overview

Generate friendly audio notifications that summarize completed work. Maintain user engagement during long-running tasks by providing natural-sounding verbal updates when work completes.

## When to Use

**Use for:**
- Long-running tasks (debugging, research, builds, deployments)
- When user may have switched context
- Explicit audio notification requests
- Multi-step workflows that deserve a summary

**Do NOT use for:**
- Brief, trivial tasks
- Active real-time conversations
- Errors requiring immediate text-based attention

## Workflow

### 1. Identify Task Type

Determine notification structure based on what was accomplished:
- **Implementation/Debugging** - Code changes, fixes, features
- **Research** - Information gathering, analysis
- **Build/Test** - Compilation, testing, deployment
- **Multi-step workflows** - Complex tasks with multiple phases

### 2. Distill to Essentials

Extract key information for audio playback:

**Implementation/Debugging:**
- High-level summary ("I fixed bugs A, B, and C")
- Important details or blockers (if needed)
- Next steps (if relevant)

**Research (brief by default):**
- Single summary of key findings
- Detailed breakdown only if user requested depth

### 3. Write Speech-Optimized Text

**Voice and tone:**
- First-person ("I added", "I found")
- Casual and friendly
- Short, simple sentences
- Direct and clear

**Punctuation:**
- Avoid exclamation marks
- No dashes, semicolons
- Use periods for pauses

**File paths (speak them out):**
- `my_file.txt` → "my_file dot text"
- `~/.config` → "home dot config"
- `src/utils.rs` → "source slash utils dot r s"

**Code symbols (natural language):**
- `MyClass.my_function` → "function my_function in class MyClass"
- `user.name` → "the user name field"

**Include:**
- Outcome summary
- Structural changes user may not expect
- Function/struct names when relevant
- Status ("All tests passing")
- Blockers or next steps

**Exclude:**
- Code blocks
- File paths (unless critical)
- Implementation details
- Markdown formatting

### 4. Execute with tts-notify

Use the bundled `scripts/tts-notify` tool:

**Single call with multiple chunks (RECOMMENDED):**
```bash
cat <<'EOF' | scripts/tts-notify --queue
I fixed the authentication bug. It was pretty tricky.
The session handler was using stale tokens.
I added a refresh check in the middleware.
EOF
```

**Direct mode (single message):**
```bash
echo "Task completed successfully." | scripts/tts-notify
```

**Key points:**
- Use `--queue` for multiple chunks (eliminates lag between audio)
- Each line in input becomes a separate audio chunk
- Chunks play in order with seamless transitions
- Single call avoids multiple permission prompts

## Tool Reference

### Basic Usage

```bash
# Multiple chunks in one call (preferred)
cat <<'EOF' | scripts/tts-notify --queue
First chunk.
Second chunk.
Third chunk.
EOF

# Single message (direct mode)
echo "Single message." | scripts/tts-notify

# With voice selection
cat <<'EOF' | scripts/tts-notify --queue --voice af_sarah
Chunk using Sarah voice.
EOF

# With speed control
echo "Faster speech." | scripts/tts-notify --speed 1.2
```

### Voice Options

Popular voices:
- American female: `af_sarah`, `af_river`, `af_bella`
- American male: `am_echo` (default), `am_puck`, `am_liam`
- British female: `bf_alice`, `bf_emma`
- British male: `bm_fable`, `bm_daniel`

List all voices: `scripts/tts-notify --list-voices`

### Installation

First run auto-installs:
- Kokoro TTS models (~340 MB)
- Required Python packages

Requires `ffplay` for audio playback:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
apt install ffmpeg
```

## Examples

### Example 1: Debug Task

User debugged memory leak, then switched context.

```bash
cat <<'EOF' | scripts/tts-notify --queue
I found the memory leak in the data processor.
It was holding references to old DataFrames.
I added explicit cleanup with del and garbage collection.
Memory usage is now stable during long runs.
EOF
```

### Example 2: Research (Brief)

User asked about data streaming approaches.

```bash
echo "I researched real time streaming. WebSockets are best for your use case. Low latency and good browser support." | scripts/tts-notify
```

### Example 3: Build and Test

Long test suite finished.

```bash
cat <<'EOF' | scripts/tts-notify --queue
The test suite finished. Twenty three tests passed.
Two tests failed in the authentication module.
Both failures are timeout related.
Looks like a mock configuration issue.
EOF
```

### Example 4: Multi-Step Implementation

New feature with multiple components.

```bash
cat <<'EOF' | scripts/tts-notify --queue
I'm done with the OAuth feature.
I added an OAuthHandler class with token refresh logic.
I also created middleware for automatic token validation.
Seven tests passed but one is timing out.
EOF
```

## Tips

1. **Start with outcome** - "I fixed X", "The build completed"
2. **Mention structural changes** - Moved files, deleted code
3. **Natural language** - "user name field" not "user dot name"
4. **Speak file extensions** - "dot py" not ".py"
5. **Avoid robotic punctuation** - No semicolons, dashes, exclamations
6. **Keep it casual** - Like talking to a colleague

## Progressive Disclosure

Keep notifications brief by default. Only add detail when:
- Task was particularly complex
- User explicitly requested depth
- Important blockers or next steps exist
- Structural changes may surprise user
