---
name: speaking
description: Provides audio communication using text-to-speech to get user's attention when they're working in other windows. Use for task completions, important findings, blockers, or any message that benefits from audio delivery. Supports both short alerts and longer explanations via multi-threaded queue mode.
---

# Speaking

Audio communication channel using text-to-speech. Gets user's attention when they're working in other windows with natural-sounding speech.

## When to Use

**Use for:**
- Task completion updates (builds, tests, deployments)
- Important findings during research
- Blockers requiring input
- Long-running task results
- Any message when user may be context-switched to other windows

**Do NOT use for:**
- Trivial updates where text is sufficient
- Active back-and-forth conversations
- Every single message (use judiciously)

## Installation

The `speak` command is a `uv run --script` script. Symlink it onto your PATH:

```bash
ln -sf ~/.claude/skills/speaking/scripts/speak ~/.local/bin/speak
```

Dependencies (`kokoro-onnx`, `soundfile`) are resolved automatically by `uv run` on first invocation. Kokoro models (~340 MB) are downloaded on first use.

## Basic Usage

### Quick Message (Direct Mode)

For single, short messages:

```bash
echo "Build completed successfully" | speak
```

### Multi-Part Message (Queue Mode)

For longer messages with multiple thoughts. Uses multi-threading for seamless playback:

```bash
cat <<'EOF' | speak --queue
I finished debugging the memory leak.
The issue was in the DataFrame processing loop.
It was holding references to old data.
I added explicit cleanup and tests are passing now.
EOF
```

**Queue mode benefits:**
- Zero-lag between chunks (generates next while playing current)
- Buffers up to 3 chunks for smooth delivery
- Each line = separate audio chunk
- Natural pacing with pauses between thoughts

## Writing Speech-Optimized Text

### Voice and Tone

- **First person**: "I found", "I fixed", "I'm seeing"
- **Casual and direct**: Like talking to a colleague
- **Short sentences**: One idea per sentence
- **Active voice**: "Tests passed" not "Tests were passed"

### Punctuation for Natural Speech

- **Use periods** for pauses
- **Avoid**: Exclamation marks (spoken as "backslash"), dashes, semicolons
- **Keep it simple**: Natural speech punctuation only

### Code and Paths

Speak them naturally:

- `config.py` → "config dot pie"
- `src/utils.rs` → "source slash utils dot r s"
- `~/.bashrc` → "home dot bashrc"
- `MyClass.method()` → "the method function in MyClass"
- `user.email` → "the user email field"

### What to Include

- **Outcome**: What was accomplished
- **Key details**: Important context or decisions
- **Status**: "Tests passing", "Ready for review"
- **Blockers**: Issues needing attention
- **Next steps**: If relevant

### What to Exclude

- Code blocks
- Markdown formatting
- Overly technical implementation details
- File paths (unless critical to the message)

## Voice Options

The script supports multiple voices via the `--voice` flag:

**American voices:**
- Female: `af_sarah`, `af_river`, `af_bella`
- Male: `am_echo` (default), `am_puck`, `am_liam`

**British voices:**
- Female: `bf_alice`, `bf_emma`
- Male: `bm_fable`, `bm_daniel`

**Usage:**
```bash
echo "Hello" | speak --voice af_sarah
```

List all available voices:
```bash
speak --list-voices
```

## Advanced Options

### Speed Control

Adjust playback speed (default: 1.0):

```bash
echo "Faster speech" | speak --speed 1.2
echo "Slower speech" | speak --speed 0.8
```

### Combining Options

```bash
cat <<'EOF' | speak --queue --voice af_sarah --speed 1.1
First thought here.
Second thought here.
EOF
```

## Examples

### Example 1: Debug Completion

Long debugging session finished:

```bash
cat <<'EOF' | speak --queue
I found the authentication bug.
The session handler was using stale tokens.
I added a token refresh check in the middleware.
All tests are passing now.
EOF
```

### Example 2: Research Finding

Quick research update:

```bash
echo "I researched the caching approaches. Redis is the best fit for your use case. It has built in expiration and good Python support." | speak
```

### Example 3: Build Results

Test suite completed:

```bash
cat <<'EOF' | speak --queue
The test suite finished.
Twenty three tests passed.
Two tests failed in the auth module.
Both are timeout related.
Looks like a mock configuration issue.
EOF
```

### Example 4: Blocker

Hit an issue needing input:

```bash
cat <<'EOF' | speak --queue
I'm blocked on the database migration.
The production schema has extra columns not in staging.
I need to know if those columns are still in use.
Should I check with the team or drop them?
EOF
```

### Example 5: Multi-Step Task

Feature implementation complete:

```bash
cat <<'EOF' | speak --queue
I finished the O Auth integration.
I created an O Auth Handler class for token management.
I added middleware for automatic validation.
I also wrote seven tests and they all pass.
The P R is ready for review.
EOF
```

## Tips

1. **Lead with outcome** - "Finished X", "Found Y", "Tests passing"
2. **One idea per line** in queue mode - creates natural pauses
3. **Speak acronyms as letters** - "O Auth" not "OAuth", "P R" not "PR"
4. **Mention structural changes** - New files, moved code, deleted modules
5. **Keep it conversational** - You're updating a colleague, not writing docs
6. **Use queue mode for context** - Longer messages with multiple points
7. **Direct mode for alerts** - Single sentence updates

## Technical Details

### Installation

First run auto-installs required components:
- Kokoro TTS models (~340 MB)
- Python packages (kokoro-onnx, soundfile)

Requires `ffplay` for audio playback:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
apt install ffmpeg
```

### How Queue Mode Works

Queue mode uses multi-threading for seamless playback:

1. **Socket listener** - Receives audio generation requests
2. **Generator thread** - Creates audio from text
3. **Player thread** - Plays audio from buffer
4. **Buffer** - Holds up to 3 chunks for smooth delivery

Result: Next chunk generates while current chunk plays = zero lag between segments.

The background worker auto-starts on first use and shuts down after 30 seconds of inactivity.
