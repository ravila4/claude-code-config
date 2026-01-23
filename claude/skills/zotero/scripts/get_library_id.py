#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///
"""
Auto-discover the Zotero library ID via the local API.

The library ID is needed for pyzotero-cli profile configuration.
This script queries the local Zotero API to get the current user's library ID.

Usage:
    uv run scripts/get_library_id.py

Returns:
    Prints the library ID to stdout, or an error message to stderr.
"""

import subprocess
import sys
from pathlib import Path

import httpx

# Add scripts directory to path for _common import
sys.path.insert(0, str(Path(__file__).parent))
from _common import (
    ZOTERO_API_BASE,
    ZOTERO_TIMEOUT,
    is_zotero_running,
    launch_zotero,
    wait_for_zotero,
)


def get_library_id() -> str | None:
    """
    Get the library ID from the local Zotero API.

    The local API uses userID 0 as a placeholder, but the actual library ID
    is returned in the item metadata.
    """
    try:
        # Get a single item to extract the library ID
        response = httpx.get(
            f"{ZOTERO_API_BASE}/users/0/items?limit=1&format=json",
            timeout=10,
        )
        response.raise_for_status()

        items = response.json()
        if items:
            # Extract library ID from first item
            item = items[0]
            library = item.get("library", {})
            library_id = library.get("id")
            if library_id:
                return str(library_id)

        # If no items, try to get from collections
        response = httpx.get(
            f"{ZOTERO_API_BASE}/users/0/collections?limit=1&format=json",
            timeout=10,
        )
        response.raise_for_status()

        collections = response.json()
        if collections:
            collection = collections[0]
            library = collection.get("library", {})
            library_id = library.get("id")
            if library_id:
                return str(library_id)

        # Empty library - no way to discover ID
        return None

    except httpx.HTTPError as e:
        print(f"Error querying Zotero API: {e}", file=sys.stderr)
        return None


def main() -> int:
    """Main entry point."""
    if not is_zotero_running():
        print("Zotero not running. Launching...", file=sys.stderr)
        try:
            launch_zotero()
        except subprocess.CalledProcessError:
            print("Failed to launch Zotero", file=sys.stderr)
            return 1

        if not wait_for_zotero():
            print(
                f"Zotero did not start within {ZOTERO_TIMEOUT}s. "
                "Please start Zotero manually and ensure the local API is enabled.",
                file=sys.stderr,
            )
            return 1
        print("Zotero started.", file=sys.stderr)

    library_id = get_library_id()

    if library_id:
        print(library_id)
        return 0
    else:
        print(
            "Could not determine library ID. Your library may be empty. "
            "Add at least one item to Zotero to auto-discover the library ID.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
