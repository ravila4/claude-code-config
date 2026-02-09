"""Tests for listen script (voice recording + transcription)."""

import importlib
import importlib.machinery
import importlib.util
import sys
import wave
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np


def _import_listen():
    """Import the listen script as a module (extensionless file)."""
    script_path = Path(__file__).parent / "listen"
    # Pre-inject dependencies that may not be installed in test env
    if "sounddevice" not in sys.modules:
        sys.modules["sounddevice"] = MagicMock()
    if "faster_whisper" not in sys.modules:
        sys.modules["faster_whisper"] = MagicMock()
    loader = importlib.machinery.SourceFileLoader("listen", str(script_path))
    spec = importlib.util.spec_from_loader("listen", loader)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_mock_sd(fake_input_stream_fn):
    """Create a mock sounddevice module with a custom InputStream factory."""
    mock_sd = MagicMock()
    mock_sd.InputStream = fake_input_stream_fn
    return mock_sd


def _make_mock_faster_whisper(mock_model):
    """Create a mock faster_whisper module with a custom WhisperModel."""
    mock_fw = MagicMock()
    mock_fw.WhisperModel = MagicMock(return_value=mock_model)
    return mock_fw


# --- Voice recording ---


class TestRecordVoice:
    def test_returns_none_on_pure_silence(self, tmp_path):
        """If all audio frames are below threshold, return None (no speech detected)."""
        listen = _import_listen()
        silence = np.zeros((1024, 1), dtype=np.float32)

        def fake_input_stream(**kwargs):
            callback = kwargs["callback"]
            for _ in range(20):
                callback(silence, None, None, None)
            return MagicMock(
                __enter__=lambda s: s,
                __exit__=lambda s, *a: False,
            )

        mock_sd = _make_mock_sd(fake_input_stream)
        with patch.dict("sys.modules", {"sounddevice": mock_sd}):
            result = listen.record_voice(
                timeout=0.1,
                silence_threshold=0.01,
                silence_duration=0.5,
                output_path=tmp_path / "test.wav",
            )

        assert result is None

    def test_returns_path_when_speech_then_silence(self, tmp_path):
        """If speech is detected followed by silence, return the WAV path."""
        listen = _import_listen()
        speech = np.full((1024, 1), 0.1, dtype=np.float32)
        silence = np.zeros((1024, 1), dtype=np.float32)

        def fake_input_stream(**kwargs):
            callback = kwargs["callback"]
            for _ in range(5):
                callback(speech, None, None, None)
            for _ in range(20):
                callback(silence, None, None, None)
            return MagicMock(
                __enter__=lambda s: s,
                __exit__=lambda s, *a: False,
            )

        mock_sd = _make_mock_sd(fake_input_stream)
        with patch.dict("sys.modules", {"sounddevice": mock_sd}):
            out = tmp_path / "test.wav"
            result = listen.record_voice(
                timeout=5,
                silence_threshold=0.01,
                silence_duration=0.5,
                output_path=out,
            )

        assert result == out
        assert out.exists()
        # Verify it's a valid WAV file
        with wave.open(str(out), "rb") as wf:
            assert wf.getnchannels() == 1
            assert wf.getsampwidth() == 2  # 16-bit
            assert wf.getframerate() == 16000


# --- Transcription ---


class TestTranscribeAudio:
    def test_returns_transcribed_text(self, tmp_path):
        """transcribe_audio returns joined segment text."""
        listen = _import_listen()
        audio_path = tmp_path / "test.wav"
        audio_path.touch()

        mock_segment_1 = MagicMock()
        mock_segment_1.text = " Hello world"
        mock_segment_2 = MagicMock()
        mock_segment_2.text = " how are you"

        mock_model = MagicMock()
        mock_model.transcribe.return_value = (
            iter([mock_segment_1, mock_segment_2]),
            MagicMock(),
        )

        mock_fw = _make_mock_faster_whisper(mock_model)
        with patch.dict("sys.modules", {"faster_whisper": mock_fw}):
            result = listen.transcribe_audio(audio_path)

        assert result == "Hello world how are you"

    def test_returns_none_on_empty_transcription(self, tmp_path):
        """transcribe_audio returns None when whisper produces no segments."""
        listen = _import_listen()
        audio_path = tmp_path / "test.wav"
        audio_path.touch()

        mock_model = MagicMock()
        mock_model.transcribe.return_value = (iter([]), MagicMock())

        mock_fw = _make_mock_faster_whisper(mock_model)
        with patch.dict("sys.modules", {"faster_whisper": mock_fw}):
            result = listen.transcribe_audio(audio_path)

        assert result is None

    def test_returns_none_on_whitespace_only(self, tmp_path):
        """transcribe_audio returns None when whisper only returns whitespace."""
        listen = _import_listen()
        audio_path = tmp_path / "test.wav"
        audio_path.touch()

        mock_segment = MagicMock()
        mock_segment.text = "   "

        mock_model = MagicMock()
        mock_model.transcribe.return_value = (iter([mock_segment]), MagicMock())

        mock_fw = _make_mock_faster_whisper(mock_model)
        with patch.dict("sys.modules", {"faster_whisper": mock_fw}):
            result = listen.transcribe_audio(audio_path)

        assert result is None
