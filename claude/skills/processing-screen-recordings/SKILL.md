---
name: processing-screen-recordings
description: Transform screen recordings into enriched meeting notes with transcripts, key frame extraction, and Obsidian integration. This skill should be used when processing MP4 screen recordings, creating meeting summaries from video, extracting visual context from recordings, or when the user mentions transcribing meetings or screen captures.
---

# Processing Screen Recordings

Transform screen recordings (MP4) into comprehensive, enriched meeting notes by combining automated transcription, visual frame extraction, and document synthesis.

## Quick Reference

```bash
# Transcribe video to SRT (timestamped subtitles)
~/.claude/skills/processing-screen-recordings/scripts/transcribe.py recording.mp4

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
   Key Frames      Error Correction      Obsidian
   (optional)      (with source doc)     Integration
```

## Step 1: Transcribe Video

Run the transcription script:

```bash
~/.claude/skills/processing-screen-recordings/scripts/transcribe.py <video.mp4>
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
# Create output directory
mkdir -p "<video_basename>/"

# Extract frame at timestamp
ffmpeg -ss HH:MM:SS -i <video.mp4> -frames:v 1 -q:v 2 "<video_basename>/MM-SS_description.jpg" -y
```

**Naming convention:** `MM-SS_brief-description.jpg`

## Step 3: Process Extracted Frames

For each extracted frame:

1. **Read the image** to understand content
2. **Classify content type:**
   - `text_document` - Meeting notes, bullet points
   - `code` - Code snippets, terminal output
   - `annotated` - Hand-drawn diagrams/annotations
   - `visualization` - Charts, plots, graphs

3. **Extract key information:**
   - For code: Extract verbatim, note language
   - For text: Extract key points, preserve hierarchy
   - For visualizations: Describe what it shows, consider cropping

4. **Deduplicate:** If frames are nearly identical, keep only the latest timestamp version.

## Step 4: Correct Transcription Errors

If the user provides source notes or a reference document:

1. **Read the source document** to understand correct terminology
2. **Identify common transcription errors:**
   - Tool/product names (e.g., "Emperor" → "Empiroar")
   - Technical terms (e.g., "fee was" → "GWAS")
   - Acronyms (e.g., "M A C" → "MAC")
   - Proper nouns and names

3. **Create corrected transcript** with proper terminology

**Common bioinformatics corrections:**
| Misheard | Correct |
|----------|---------|
| Regini/Gini | Regenie |
| fee was/gbaz | GWAS |
| fee code | phecode |
| Fish exact | Fisher's exact |
| Plank | Plink |

## Step 5: Create Enriched Notes

Synthesize all sources into a comprehensive document:

**Structure:**
```markdown
# [Meeting Title]

**Date:** YYYY-MM-DD
**Participants:** [names]
**Duration:** ~XX minutes

## Executive Summary
[2-3 sentence overview]

## Key Discussion Points
[Main topics from transcript]

## Technical Details
[Code snippets, architecture decisions]

## Action Items
- [ ] Task 1
- [ ] Task 2

## Visualizations
![Description](path/to/frame.jpg)

```

**Include:**
- Context from transcript
- Corrected terminology
- Embedded visualizations (if extracted)
- Code snippets from frames
- Action items and next steps

## Step 6: Obsidian Integration (Optional)

To save to Obsidian vault at ${HOME}/Documents/Obsidian-Notes:

**YAML Frontmatter:**
```yaml
---
date: YYYY-MM-DD
participants: [Name1, Name2]
tags:
  - meeting
  - [topic-tag]
projects:
  - [Project-Name]
---
```

**Folder:** Place in appropriate location (e.g., `Empirico/Meetings/`)

**Internal Links:** Add `[[Related Note]]` links to existing relevant notes.

## File Organization

After processing, the directory structure:

```
recording_directory/
├── 2026-01-12_15-47-09.mp4          # Original video
├── 2026-01-12_15-47-09.srt          # Transcript
├── 2026-01-12_15-47-09_corrected.srt # Corrected transcript (if applicable)
└── 2026-01-12_15-47-09/             # Extracted frames folder
    ├── 05-22_editing-document.jpg
    ├── 17-25_code-review.jpg
    └── notes_corrected.md           # Final enriched notes
```

## Dependencies

- **ffmpeg** - Video/audio processing (`brew install ffmpeg`)
- **parakeet-mlx** - Speech-to-text (installed automatically by script via uv)
