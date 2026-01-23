"""
Shared utilities for Zotero skill scripts.

This module contains common functions used across multiple scripts
to avoid code duplication.
"""

import shutil
import subprocess
import sys
import time

import httpx

ZOTERO_API_BASE = "http://localhost:23119/api"
ZOTERO_TIMEOUT = 30  # seconds to wait for Zotero to start


def is_zotero_running() -> bool:
    """Check if Zotero local API is available."""
    try:
        response = httpx.get(f"{ZOTERO_API_BASE}/users/0/items?limit=1", timeout=2)
        return response.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


def launch_zotero() -> None:
    """Launch Zotero app (cross-platform)."""
    if sys.platform == "darwin":
        subprocess.run(["open", "-a", "Zotero"], check=True)
    elif sys.platform == "linux":
        # Try common Zotero executable names
        for cmd in ["zotero", "zotero-bin"]:
            if shutil.which(cmd):
                # Launch in background, detached from terminal
                subprocess.Popen(
                    [cmd],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                return
        raise FileNotFoundError("Zotero not found in PATH. Install Zotero or add it to PATH.")
    else:
        raise NotImplementedError(f"Platform {sys.platform} not supported")


def wait_for_zotero(timeout: int = ZOTERO_TIMEOUT) -> bool:
    """Wait for Zotero API to become available."""
    start = time.time()
    while time.time() - start < timeout:
        if is_zotero_running():
            return True
        time.sleep(1)
    return False


def ensure_zotero_running() -> bool:
    """Ensure Zotero is running, launching if needed."""
    if is_zotero_running():
        return True

    print("Zotero not running. Launching...", file=sys.stderr)
    try:
        launch_zotero()
    except subprocess.CalledProcessError:
        print("Failed to launch Zotero", file=sys.stderr)
        return False

    if not wait_for_zotero():
        print(
            f"Zotero did not start within {ZOTERO_TIMEOUT}s. "
            "Please start Zotero manually.",
            file=sys.stderr,
        )
        return False

    print("Zotero started.", file=sys.stderr)
    return True
