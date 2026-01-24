---
name: video-to-notes
description: Transform screen recordings into enriched meeting notes with transcripts, key frame extraction, and Obsidian integration. This skill should be used when processing MP4 screen recordings, creating meeting summaries from video, extracting visual context from recordings, or when the user mentions transcribing meetings or screen captures.
---

# Video to Notes

Transform screen recordings (MP4) into comprehensive, enriched meeting notes by combining automated transcription, visual frame extraction, and document synthesis.

## Quick Reference

```bash
# Transcribe video to SRT (timestamped subtitles)
~/.claude/skills/video-to-notes/scripts/transcribe.py recording.mp4

# Apply high-frequency replacements (in-place)
~/.claude/skills/video-to-notes/scripts/apply_replacements.py recording.srt -i

# Split SRT for parallel correction (outputs JSON with chunk info)
~/.claude/skills/video-to-notes/scripts/split_srt.py recording.srt --chunk-size 35

# Extract frame at specific timestamp
ffmpeg -ss 00:05:22 -i recording.mp4 -frames:v 1 -q:v 2 output.jpg -y
```

## Workflow Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  MP4 Video  │ ──▶ │  Transcript │ ──▶ │  Enriched   │
│             │     │    (SRT)    │     │    Notes    │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
   Key Frames       Parallel LLM         Obsidian
   (optional)       Correction           Integration
```

## Step 1: Transcribe Video

Run the transcription script:

```bash
~/.claude/skills/video-to-notes/scripts/transcribe.py <video.mp4>
```

**Options:**
- `--format srt` (default) - Timestamped subtitles
- `--format txt` - Plain text
- `--format json` - Structured JSON
- `--keep-mp3` - Retain intermediate audio file

**Output:** Creates `<basename>.srt` in same directory as video.

**Requirements:** `ffmpeg` must be installed (`brew install ffmpeg`).

## Step 2: Extract Key Frames (Optional)

Ask the user: "Would you like to extract key frames from the video for visual context?"

If yes, identify timestamps where visual context adds value:
- Code being shown/edited
- Diagrams or architecture drawings
- Charts, plots, or data visualizations
- UI demonstrations
- Hand-drawn annotations

**Extract frames:**

```bash
mkdir -p "<video_basename>/"
ffmpeg -ss HH:MM:SS -i <video.mp4> -frames:v 1 -q:v 2 "<video_basename>/MM-SS_description.jpg" -y
```

**Naming convention:** `MM-SS_brief-description.jpg`

## Step 3: Evaluate and Process Extracted Frames

**CRITICAL:** Most screen recording frames add NO value to meeting notes. Evaluate each frame critically before including it.

For detailed evaluation criteria, classification types, and the decision matrix, read:
`~/.claude/skills/video-to-notes/references/frame-evaluation.md`

**Quick decision guide:**
- DELETE: Redundant, noisy, or better as text
- EXTRACT: Contains code/text not in transcript → extract then delete image
- RE-CREATE: Hand-drawn concepts → create clean Graphviz/TikZ diagram
- KEEP: Only if visual is truly essential to understanding

## Step 4: Correct Transcription Errors (Parallel Processing)

Use parallel tasks with a fast, cost-effective model for transcript correction.

### 4.1 Apply Programmatic Replacements

```bash
~/.claude/skills/video-to-notes/scripts/apply_replacements.py <file>.srt -i
```

Uses `~/.config/transcription/replacements.json` for common error corrections.

### 4.2 Load Domain Word List

Read `~/.config/transcription/word_list.txt` for domain-specific correct terms.

### 4.3 Split Transcript into Chunks

```bash
~/.claude/skills/video-to-notes/scripts/split_srt.py <file>.srt --chunk-size 35
```

Smaller chunks (35-50 blocks) with more parallel agents is faster than larger chunks.

### 4.4 Launch Parallel Correction Tasks

Launch multiple Task tool calls **in a single message** for parallel execution.

**Task parameters:**
- `subagent_type`: "general-purpose"
- `model`: Use a fast model (e.g., `haiku`, `gpt-4o-mini`, `gemini-flash`)
- `prompt`: See template in `references/transcript-correction-prompt.md`

For the full prompt template and merge instructions, read:
`~/.claude/skills/video-to-notes/references/transcript-correction-prompt.md`

### 4.5 Update Word List (Optional)

If the model suggests new terms, ask the user if they want to add them to `~/.config/transcription/word_list.txt`.

## Step 5: Create Enriched Notes

Synthesize all sources into a comprehensive document:

**Structure:**
```markdown
---
date: YYYY-MM-DD
participants:
  - Name1
  - Name2
tags:
  - empirico/meeting
  - [topic-tag]
projects:
  - [Project-Name]
---

## Summary

Brief overview of the meeting purpose and key outcomes (2-3 sentences).

## Topics

### Topic Name

Discussion content with [[internal links]] where appropriate.

#### Subtopic (if needed)

More detailed content, code snippets, architecture decisions.

### Another Topic

Continue organizing by main discussion themes.

## Action Items (If Applicable)

- [ ] Task 1 with owner
- [ ] Task 2 with owner
```

**Guidelines:**
- Use `## Summary` (not "Executive Summary")
- Organize all discussion under `## Topics` with descriptive subsections
- Consolidate ALL action items into single `## Action Items` section at end
- Use checkbox format `- [ ]` for action items
- Include `empirico/meeting` tag for Empirico meetings
- Add `[[internal links]]` to related Obsidian notes
- Embed visualizations inline within relevant topic sections: `![[diagram.svg]]`

## Step 6: Obsidian Integration (Optional)

To save to Obsidian vault at ${HOME}/Documents/Obsidian-Notes:

**Folder:** Place in appropriate location (e.g., `Empirico/Meetings/`)

**Filename convention:** `YYYY-MM-DD - Meeting Title.md`

**Internal Links:** Add `[[Related Note]]` links to existing relevant notes throughout the document.

## File Organization

After processing, the directory structure:

```
recording_directory/
├── 2026-01-12_15-47-09.mp4           # Original video
├── 2026-01-12_15-47-09.srt           # Raw transcript
├── 2026-01-12_15-47-09.corrected.srt # Corrected transcript
├── 2026-01-12_15-47-09.corrections.json # Correction report
└── 2026-01-12_15-47-09/              # Extracted frames folder
    ├── 05-22_editing-document.jpg
    ├── 17-25_code-review.jpg
    └── meeting_notes.md              # Final enriched notes
```

## Dependencies

- **ffmpeg** - Video/audio processing (`brew install ffmpeg`)
- **parakeet-mlx** - Speech-to-text (installed automatically by script via uv)

## Configuration

User-specific files in `~/.config/transcription/`:
- `word_list.txt` - Domain-specific correct terms for LLM context
- `replacements.json` - High-frequency error mappings for programmatic replacement
