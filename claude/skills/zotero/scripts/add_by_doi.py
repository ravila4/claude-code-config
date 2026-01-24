#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///
"""
Add a paper to Zotero by DOI.

Fetches metadata from CrossRef API and creates the item via zot CLI.

Usage:
    uv run scripts/add_by_doi.py 10.1038/s41586-023-06957-x
    uv run scripts/add_by_doi.py https://www.nature.com/articles/s41586-023-06957-x
    uv run scripts/add_by_doi.py https://doi.org/10.1038/s41586-023-06957-x

Options:
    --collection KEY    Add to collection (can be specified multiple times)
    --tag TAG           Add tag (can be specified multiple times)
    --dry-run           Print JSON without creating item
"""

import argparse
import json
import re
import subprocess
import sys

import httpx

CROSSREF_API = "https://api.crossref.org/works"
USER_AGENT = "ZoteroSkill/1.0 (mailto:user@example.com)"

# Patterns to extract DOI from various URL formats
DOI_PATTERNS = [
    # Direct DOI
    r"^(10\.\d{4,}/[^\s]+)$",
    # doi.org URL
    r"doi\.org/(10\.\d{4,}/[^\s?#]+)",
    # Nature articles
    r"nature\.com/articles/(s?\d+-\d+-\d+-[a-z0-9]+)",
    # Generic DOI in URL
    r"(10\.\d{4,}/[^\s?#]+)",
]


def extract_doi(input_str: str) -> str | None:
    """Extract DOI from input string (URL or direct DOI)."""
    input_str = input_str.strip()

    for pattern in DOI_PATTERNS:
        match = re.search(pattern, input_str, re.IGNORECASE)
        if match:
            doi = match.group(1)
            # Nature article IDs need prefix
            if pattern == DOI_PATTERNS[2]:
                doi = f"10.1038/{doi}"
            return doi

    return None


def fetch_crossref_metadata(doi: str) -> dict | None:
    """Fetch metadata from CrossRef API."""
    url = f"{CROSSREF_API}/{doi}"
    headers = {"User-Agent": USER_AGENT}

    try:
        response = httpx.get(url, headers=headers, timeout=30, follow_redirects=True)
        response.raise_for_status()
        data = response.json()
        return data.get("message", {})
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            print(f"DOI not found in CrossRef: {doi}", file=sys.stderr)
        else:
            print(f"CrossRef API error: {e}", file=sys.stderr)
        return None
    except httpx.RequestError as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return None


def crossref_to_zotero(cr: dict) -> dict:
    """Convert CrossRef metadata to Zotero format."""
    item = {
        "itemType": "journalArticle",
        "title": cr.get("title", [""])[0] if cr.get("title") else "",
        "creators": [],
        "abstractNote": cr.get("abstract", ""),
        "publicationTitle": cr.get("container-title", [""])[0] if cr.get("container-title") else "",
        "date": "",
        "volume": cr.get("volume", ""),
        "issue": cr.get("issue", ""),
        "pages": cr.get("page", ""),
        "DOI": cr.get("DOI", ""),
        "ISSN": cr.get("ISSN", [""])[0] if cr.get("ISSN") else "",
        "url": cr.get("URL", ""),
        "tags": [],
        "collections": [],
    }

    # Parse date
    date_parts = cr.get("published", {}).get("date-parts", [[]])
    if date_parts and date_parts[0]:
        parts = date_parts[0]
        if len(parts) >= 1:
            item["date"] = str(parts[0])
        if len(parts) >= 2:
            item["date"] = f"{parts[0]}-{parts[1]:02d}"
        if len(parts) >= 3:
            item["date"] = f"{parts[0]}-{parts[1]:02d}-{parts[2]:02d}"

    # Parse authors
    for author in cr.get("author", []):
        if author.get("name"):
            # Organization/group author
            item["creators"].append({
                "creatorType": "author",
                "name": author["name"],
            })
        elif author.get("family"):
            item["creators"].append({
                "creatorType": "author",
                "firstName": author.get("given", ""),
                "lastName": author["family"],
            })

    # Clean abstract (remove HTML tags)
    if item["abstractNote"]:
        item["abstractNote"] = re.sub(r"<[^>]+>", "", item["abstractNote"])

    return item


def create_zotero_item(item: dict) -> str | None:
    """Create item in Zotero via zot CLI. Returns item key on success."""
    json_str = json.dumps(item)

    try:
        result = subprocess.run(
            ["zot", "--profile", "web", "items", "create", "--from-json", json_str],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            print(f"zot create failed: {result.stderr}", file=sys.stderr)
            return None

        # Parse response to get item key
        try:
            response = json.loads(result.stdout)
            if "success" in response:
                keys = list(response["success"].values())
                if keys:
                    return keys[0]
            elif "successful" in response:
                keys = list(response["successful"].keys())
                if keys:
                    return response["successful"][keys[0]].get("key")
        except json.JSONDecodeError:
            pass

        # If we can't parse the key, item was still created
        return "created"

    except FileNotFoundError:
        print("zot command not found. Run: uv tool install pyzotero-cli", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print("zot command timed out", file=sys.stderr)
        return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add a paper to Zotero by DOI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("identifier", help="DOI or URL containing DOI")
    parser.add_argument(
        "--collection", "-c",
        action="append",
        default=[],
        help="Collection key to add item to (can repeat)",
    )
    parser.add_argument(
        "--tag", "-t",
        action="append",
        default=[],
        help="Tag to add (can repeat)",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Print Zotero JSON without creating item",
    )

    args = parser.parse_args()

    # Extract DOI
    doi = extract_doi(args.identifier)
    if not doi:
        print(f"Could not extract DOI from: {args.identifier}", file=sys.stderr)
        return 1

    print(f"DOI: {doi}", file=sys.stderr)

    # Fetch metadata
    print("Fetching metadata from CrossRef...", file=sys.stderr)
    crossref_data = fetch_crossref_metadata(doi)
    if not crossref_data:
        return 1

    # Convert to Zotero format
    zotero_item = crossref_to_zotero(crossref_data)

    # Add collections and tags from args
    zotero_item["collections"] = args.collection
    zotero_item["tags"] = [{"tag": t} for t in args.tag]

    if args.dry_run:
        print(json.dumps(zotero_item, indent=2))
        return 0

    # Create item
    print("Creating Zotero item...", file=sys.stderr)
    item_key = create_zotero_item(zotero_item)
    if not item_key:
        return 1

    title = zotero_item.get("title", "Unknown")
    creators = zotero_item.get("creators", [])
    if creators:
        first_author = creators[0].get("lastName") or creators[0].get("name", "")
        author_str = f"{first_author} et al." if len(creators) > 1 else first_author
    else:
        author_str = "Unknown"

    print(f"\nAdded: {author_str} - {title[:60]}{'...' if len(title) > 60 else ''}")
    print(f"Key: {item_key}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
