#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["parakeet-mlx"]
# ///
"""Convert screen recordings to transcripts with timestamps."""

import argparse
import subprocess
import sys
from pathlib import Path


def convert_to_mp3(video_path: Path) -> Path:
    """Convert video to MP3 audio."""
    mp3_path = video_path.with_suffix(".mp3")

    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-vn", "-acodec", "libmp3lame", "-q:a", "2",
        str(mp3_path), "-y"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ffmpeg error: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    return mp3_path


def transcribe(audio_path: Path, output_format: str = "srt") -> Path:
    """Transcribe audio using parakeet-mlx."""
    cmd = [
        "parakeet-mlx", str(audio_path),
        "--output-dir", str(audio_path.parent),
        "--output-format", output_format,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"parakeet-mlx error: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    return audio_path.with_suffix(f".{output_format}")


def main():
    parser = argparse.ArgumentParser(description="Transcribe screen recordings")
    parser.add_argument("videos", nargs="+", type=Path, help="Video files to transcribe")
    parser.add_argument("--format", "-f", default="srt", choices=["srt", "vtt", "txt", "json"],
                        help="Output format (default: srt)")
    parser.add_argument("--keep-mp3", action="store_true", help="Keep intermediate MP3 files")
    args = parser.parse_args()

    for video_path in args.videos:
        if not video_path.exists():
            print(f"File not found: {video_path}", file=sys.stderr)
            continue

        print(f"Processing: {video_path.name}")

        print("  Converting to MP3...")
        mp3_path = convert_to_mp3(video_path)

        print("  Transcribing...")
        output_path = transcribe(mp3_path, args.format)

        if not args.keep_mp3:
            mp3_path.unlink()

        print(f"  Done: {output_path.name}")


if __name__ == "__main__":
    main()
