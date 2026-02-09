"""Tests for afk-stop-hook.sh bash script."""

import json
import subprocess
from pathlib import Path

import pytest

HOOK_SCRIPT = Path(__file__).parent / "afk-stop-hook.sh"
AFK_FLAG = Path("/tmp/claude-afk")


def run_hook(stdin_data: dict) -> subprocess.CompletedProcess:
    """Run the hook script with JSON on stdin, return CompletedProcess."""
    return subprocess.run(
        ["bash", str(HOOK_SCRIPT)],
        input=json.dumps(stdin_data),
        capture_output=True,
        text=True,
        timeout=5,
    )


@pytest.fixture(autouse=True)
def _cleanup_afk_flag():
    """Ensure AFK flag is cleaned up after each test."""
    yield
    AFK_FLAG.unlink(missing_ok=True)


class TestAfkStopHook:
    def test_exits_zero_when_flag_missing(self):
        """No AFK flag -> allow stop (exit 0, no output)."""
        AFK_FLAG.unlink(missing_ok=True)
        result = run_hook({"stop_hook_active": False})
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_exits_zero_when_stop_hook_active(self):
        """AFK flag exists but stop_hook_active is true -> allow stop (prevent loop)."""
        AFK_FLAG.touch()
        result = run_hook({"stop_hook_active": True})
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_blocks_when_afk_and_not_stop_hook_active(self):
        """AFK flag exists and stop_hook_active is false -> block with reason."""
        AFK_FLAG.touch()
        result = run_hook({"stop_hook_active": False})
        assert result.returncode == 0

        output = json.loads(result.stdout)
        assert output["decision"] == "block"
        assert "reason" in output
        # Reason should instruct Claude to speak and listen
        assert "speak" in output["reason"].lower() or "listen" in output["reason"].lower()

    def test_block_reason_mentions_listen(self):
        """Block reason should tell Claude to run listen command."""
        AFK_FLAG.touch()
        result = run_hook({"stop_hook_active": False})
        output = json.loads(result.stdout)
        assert "listen" in output["reason"]

    def test_block_reason_mentions_afk_disable(self):
        """Block reason should tell Claude how to disable AFK mode."""
        AFK_FLAG.touch()
        result = run_hook({"stop_hook_active": False})
        output = json.loads(result.stdout)
        assert "/tmp/claude-afk" in output["reason"]
