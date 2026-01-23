---
name: zotero
description: Write operations for Zotero reference library - creating items, managing collections, organizing references. This skill should be used when adding new papers, creating/managing collections, or reorganizing the library. For searching and reading, use the Zotero MCP tools directly.
---

# Zotero Write Operations

This skill handles write operations for Zotero that MCP tools don't support: creating items, managing collections, and organizing references.

**For read operations** (search, get metadata, read fulltext, export BibTeX), use the Zotero MCP tools directly - they're faster and support semantic search.

## Prerequisites

1. **Zotero 7** desktop app running
2. **Local API enabled:** Settings > Advanced > "Allow other applications to communicate with Zotero"
3. **API key** for write operations (stored in keychain)

**Setup:** Run `uv run scripts/setup.py` to configure profiles and verify API key.

## Write Workflows

All write operations require the web API profile. Load the API key first:

```bash
source ~/.zshrc  # loads ZOTERO_API_KEY
```

### Create Item from Metadata

```bash
# Get template for item type
zot --profile web util item-template journalArticle

# Create with JSON
zot --profile web items create --from-json '{
  "itemType": "journalArticle",
  "title": "Paper Title",
  "creators": [
    {"creatorType": "author", "firstName": "Jane", "lastName": "Smith"}
  ],
  "date": "2024",
  "DOI": "10.1234/example",
  "publicationTitle": "Nature Methods"
}'
```

**Item types:** `journalArticle`, `book`, `bookSection`, `conferencePaper`, `thesis`, `preprint`, `webpage`, `report`

**Creator format:**
- Named authors: `{"creatorType": "author", "firstName": "Jane", "lastName": "Smith"}`
- Organizations: `{"creatorType": "author", "name": "WHO"}`

### Create Collection

```bash
# Create top-level collection
zot --profile web collections create --name "GWAS Papers"

# Create subcollection (provide parent key)
zot --profile web collections create --name "Methodology" --parent-id ABC12345
```

### Add Items to Collection

```bash
# Add single item
zot --profile web collections add-item COLLECTION_KEY --item-id ITEM_KEY

# Add multiple items
zot --profile web collections add-item COLLECTION_KEY --item-id KEY1 --item-id KEY2
```

### Move Item Between Collections

```bash
# Remove from old collection
zot --profile web collections remove-item OLD_COLLECTION --item-id ITEM_KEY

# Add to new collection
zot --profile web collections add-item NEW_COLLECTION --item-id ITEM_KEY
```

### Update Item Metadata

```bash
zot --profile web items update ITEM_KEY --field title "New Title" --field date "2025"
```

### Delete Items

```bash
# Delete item (moves to trash)
zot --profile web items delete ITEM_KEY

# Delete multiple
zot --profile web items delete KEY1 KEY2 KEY3
```

### Delete Collection

```bash
zot --profile web collections delete COLLECTION_KEY
```

## Common Patterns

### Bulk Import Workflow

1. Search for existing item to avoid duplicates (use MCP `zotero_semantic_search`)
2. If not found, create item with full metadata
3. Add to appropriate collection
4. Apply tags for organization

### Collection Organization Workflow

1. List collections (use MCP `zotero_get_collections`)
2. Create new collection if needed
3. Search for items to organize (use MCP `zotero_semantic_search`)
4. Add items to collection

## Error Reference

| Error | Cause | Solution |
|-------|-------|----------|
| "API key is required" | Key not loaded | Run `source ~/.zshrc` |
| "Item not found" | Invalid key | Verify key with MCP search |
| "Permission denied" | API key lacks write access | Regenerate key with write permissions |

## Scripts

| Script | Purpose |
|--------|---------|
| `setup.py` | One-time setup (install CLI, configure profiles, verify API key) |
| `get_library_id.py` | Auto-discover library ID from running Zotero |
