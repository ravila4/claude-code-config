#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///
"""
One-time setup for Zotero skill.

This script:
1. Installs pyzotero-cli via uv
2. Auto-discovers your library ID
3. Creates/updates ~/.config/zotcli/config.ini
4. Verifies API key is in macOS keychain

Usage:
    uv run scripts/setup.py

After running, you'll have both 'local' and 'web' profiles configured.
"""

import configparser
import os
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

CONFIG_PATH = Path.home() / ".config" / "zotcli" / "config.ini"
KEYCHAIN_SERVICE = "zotero-api-key"


def print_step(msg: str) -> None:
    """Print a step message."""
    print(f"\n→ {msg}")


def print_success(msg: str) -> None:
    """Print a success message."""
    print(f"  ✓ {msg}")


def print_error(msg: str) -> None:
    """Print an error message."""
    print(f"  ✗ {msg}", file=sys.stderr)


def print_info(msg: str) -> None:
    """Print an info message."""
    print(f"  {msg}")


def install_pyzotero_cli() -> bool:
    """Install pyzotero-cli via uv tool."""
    print_step("Installing pyzotero-cli...")
    try:
        result = subprocess.run(
            ["uv", "tool", "install", "pyzotero-cli"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            if "already installed" in result.stderr.lower():
                print_success("pyzotero-cli already installed")
            else:
                print_success("pyzotero-cli installed")
            return True
        else:
            # Check if already installed (different uv versions report differently)
            check = subprocess.run(
                ["uv", "tool", "list"],
                capture_output=True,
                text=True,
            )
            if "pyzotero-cli" in check.stdout:
                print_success("pyzotero-cli already installed")
                return True
            print_error(f"Failed to install: {result.stderr}")
            return False
    except FileNotFoundError:
        print_error("uv not found. Install from https://docs.astral.sh/uv/")
        return False


def ensure_zotero_running() -> bool:
    """Ensure Zotero is running, launching if needed."""
    print_step("Checking Zotero...")

    if is_zotero_running():
        print_success("Zotero is running")
        return True

    print_info("Zotero not running, launching...")
    try:
        launch_zotero()
    except subprocess.CalledProcessError:
        print_error("Failed to launch Zotero")
        return False

    if wait_for_zotero():
        print_success("Zotero started")
        return True
    else:
        print_error(
            f"Zotero did not respond within {ZOTERO_TIMEOUT}s. "
            "Please start Zotero manually and ensure local API is enabled: "
            "Settings > Advanced > Allow other applications to communicate with Zotero"
        )
        return False


def get_library_id() -> str | None:
    """Get the library ID from the local Zotero API."""
    try:
        # Try items first
        response = httpx.get(
            f"{ZOTERO_API_BASE}/users/0/items?limit=1&format=json",
            timeout=10,
        )
        response.raise_for_status()
        items = response.json()
        if items:
            library_id = items[0].get("library", {}).get("id")
            if library_id:
                return str(library_id)

        # Try collections
        response = httpx.get(
            f"{ZOTERO_API_BASE}/users/0/collections?limit=1&format=json",
            timeout=10,
        )
        response.raise_for_status()
        collections = response.json()
        if collections:
            library_id = collections[0].get("library", {}).get("id")
            if library_id:
                return str(library_id)

        return None
    except httpx.HTTPError:
        return None


def discover_library_id() -> str | None:
    """Discover library ID from Zotero."""
    print_step("Discovering library ID...")

    library_id = get_library_id()
    if library_id:
        print_success(f"Library ID: {library_id}")
        return library_id
    else:
        print_error(
            "Could not discover library ID. Your library may be empty. "
            "Add at least one item to Zotero first."
        )
        return None


def read_existing_config() -> configparser.ConfigParser:
    """Read existing config or return empty parser."""
    config = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        config.read(CONFIG_PATH)
    return config


def write_config(library_id: str) -> bool:
    """Write the config file with both profiles."""
    print_step(f"Writing config to {CONFIG_PATH}...")

    config = read_existing_config()

    # Ensure sections exist
    for section in ["profile.local", "profile.web", "zotcli"]:
        if not config.has_section(section):
            config.add_section(section)

    # Set local profile
    config.set("profile.local", "library_id", library_id)
    config.set("profile.local", "library_type", "user")
    config.set("profile.local", "local", "true")

    # Set web profile
    config.set("profile.web", "library_id", library_id)
    config.set("profile.web", "library_type", "user")

    # Set default profile
    config.set("zotcli", "current_profile", "local")

    # Write config
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            config.write(f)
        print_success("Config written")
        return True
    except OSError as e:
        print_error(f"Failed to write config: {e}")
        return False


def check_api_key() -> bool:
    """Check if API key is available (cross-platform)."""
    print_step("Checking for API key...")

    # Check environment variable first (works on all platforms)
    if os.environ.get("ZOTERO_API_KEY"):
        print_success("API key found in environment")
        return True

    # Platform-specific keychain check
    if sys.platform == "darwin":
        try:
            result = subprocess.run(
                [
                    "security", "find-generic-password",
                    "-a", os.environ.get("USER", ""),
                    "-s", KEYCHAIN_SERVICE,
                    "-w",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.stdout.strip():
                print_success("API key found in macOS Keychain")
                return True
        except Exception:
            pass
    elif sys.platform == "linux":
        try:
            result = subprocess.run(
                [
                    "secret-tool", "lookup",
                    "service", KEYCHAIN_SERVICE,
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.stdout.strip():
                print_success("API key found in secret storage")
                return True
        except Exception:
            pass

    print_info("API key not found (needed for web API: create items, export BibTeX)")
    print_info("")
    print_info("To set up API key:")
    print_info("  1. Create a key at: https://www.zotero.org/settings/security#applications")
    print_info("     - Check 'Allow library access'")
    print_info("     - Check 'Allow write access' if you want to create/update items")
    print_info("")

    if sys.platform == "darwin":
        print_info("  2. Store in macOS Keychain:")
        print_info(f'     security add-generic-password -a "$USER" -s "{KEYCHAIN_SERVICE}" -w "YOUR_API_KEY"')
        print_info("")
        print_info("  3. Add to ~/.zshrc:")
        print_info(f'     export ZOTERO_API_KEY=$(security find-generic-password -a "$USER" -s "{KEYCHAIN_SERVICE}" -w 2>/dev/null)')
    elif sys.platform == "linux":
        print_info("  2. Store in secret storage (GNOME Keyring / KWallet):")
        print_info(f'     secret-tool store --label="Zotero API Key" service {KEYCHAIN_SERVICE}')
        print_info("")
        print_info("  3. Add to your shell config (~/.zshrc or ~/.bashrc):")
        print_info(f'     export ZOTERO_API_KEY=$(secret-tool lookup service {KEYCHAIN_SERVICE} 2>/dev/null)')
    else:
        print_info("  2. Set environment variable:")
        print_info('     export ZOTERO_API_KEY="YOUR_API_KEY"')

    print_info("")
    print_info("  4. Reload shell: source ~/.zshrc  # or ~/.bashrc")
    return False


def verify_zot_command() -> bool:
    """Verify zot command works."""
    print_step("Verifying zot command...")

    try:
        result = subprocess.run(
            ["zot", "--local", "items", "count"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            count = result.stdout.strip()
            print_success(f"zot works - library has {count} items")
            return True
        else:
            print_error(f"zot command failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print_error("zot command not found - check PATH")
        return False
    except subprocess.TimeoutExpired:
        print_error("zot command timed out")
        return False


def main() -> int:
    """Main entry point."""
    print("=" * 50)
    print("Zotero Skill Setup")
    print("=" * 50)

    # Step 1: Install pyzotero-cli
    if not install_pyzotero_cli():
        return 1

    # Step 2: Ensure Zotero is running
    if not ensure_zotero_running():
        return 1

    # Step 3: Discover library ID
    library_id = discover_library_id()
    if not library_id:
        return 1

    # Step 4: Write config
    if not write_config(library_id):
        return 1

    # Step 5: Check API key (optional)
    check_api_key()

    # Step 6: Verify everything works
    if not verify_zot_command():
        return 1

    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)
    print("\nYou can now use:")
    print("  zot --local items list --top --limit 10    # Search locally")
    print("  zot --profile web items get KEY --output bibtex  # Export BibTeX")
    print("")

    return 0


if __name__ == "__main__":
    sys.exit(main())
