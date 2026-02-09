"""Tests for briefing script (text chunking for TTS pipeline)."""

import importlib
import importlib.machinery
import importlib.util
import sys
from unittest.mock import MagicMock


def _import_briefing():
    """Import the briefing script as a module (extensionless file)."""
    from pathlib import Path

    script_path = Path(__file__).parent / "briefing"
    # Pre-inject heavy dependencies that aren't needed for unit tests
    for mod in ("mlx_audio", "mlx_audio.tts.utils", "mlx_audio.utils",
                "mlx_audio.audio_io", "mlx.core", "httpx"):
        if mod not in sys.modules:
            sys.modules[mod] = MagicMock()
    loader = importlib.machinery.SourceFileLoader("briefing", str(script_path))
    spec = importlib.util.spec_from_loader("briefing", loader)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestSplitIntoChunks:
    def test_splits_on_double_newlines(self):
        """Paragraphs separated by blank lines become separate chunks."""
        briefing = _import_briefing()
        # Each paragraph must be >= 100 chars (MIN_CHUNK_CHARS) to split
        para1 = "First paragraph with plenty of text to comfortably exceed the minimum chunk size threshold for independent splitting."
        para2 = "Second paragraph that also has more than enough text to exceed the minimum chunk size threshold on its own merits."
        text = f"{para1}\n\n{para2}"
        chunks = briefing.split_into_chunks(text)
        assert len(chunks) == 2
        assert chunks[0].startswith("First paragraph")
        assert chunks[1].startswith("Second paragraph")

    def test_merges_short_paragraphs(self):
        """Paragraphs shorter than MIN_CHUNK_CHARS get merged with the next one."""
        briefing = _import_briefing()
        text = "Short.\n\nAlso short.\n\nThis third paragraph is long enough to stand on its own and exceed the minimum character threshold for a chunk."
        chunks = briefing.split_into_chunks(text)
        # "Short." and "Also short." should be merged together or with the third
        assert len(chunks) <= 2
        # The short paragraphs should appear somewhere in the output
        combined = " ".join(chunks)
        assert "Short." in combined
        assert "Also short." in combined

    def test_trailing_text_appended_to_last_chunk(self):
        """Leftover text below threshold gets appended to the last chunk."""
        briefing = _import_briefing()
        text = (
            "A long enough paragraph that definitely exceeds the minimum chunk size threshold for splitting.\n\n"
            "Tiny tail."
        )
        chunks = briefing.split_into_chunks(text)
        assert len(chunks) == 1
        assert chunks[0].endswith("Tiny tail.")

    def test_empty_input_returns_empty_list(self):
        """Empty or whitespace-only input returns no chunks."""
        briefing = _import_briefing()
        assert briefing.split_into_chunks("") == []
        assert briefing.split_into_chunks("   \n\n  ") == []

    def test_single_paragraph(self):
        """A single paragraph (no double newlines) returns one chunk."""
        briefing = _import_briefing()
        text = "Just one paragraph with no blank lines in it at all."
        chunks = briefing.split_into_chunks(text)
        assert len(chunks) == 1
        assert chunks[0] == text
