# Search Strategies Reference

## Contents

- [Relevance Scoring Algorithm](#relevance-scoring-algorithm)
- [Multi-Keyword Semantics](#multi-keyword-semantics)
- [Optimization Strategies](#optimization-strategies)
- [Handling Typos and Variants](#handling-typos-and-variants)
- [Semantic Search (Not Implemented)](#semantic-search-not-implemented)
- [File Path Matching Strategy](#file-path-matching-strategy)
- [Ranking and Sorting](#ranking-and-sorting)
- [Result Limiting](#result-limiting)
- [Time-Based Filtering Strategy](#time-based-filtering-strategy)
- [Combined Filter Logic](#combined-filter-logic)
- [Scoring Refinements (Future)](#scoring-refinements-future)
- [Performance Benchmarks](#performance-benchmarks)
- [Search Quality Metrics](#search-quality-metrics)
- [Future Research Directions](#future-research-directions)

## Relevance Scoring Algorithm

### Current Implementation

The `search_conversations.py` script uses a simple frequency-based scoring:

```python
def score_relevance(text, keywords):
    score = 0
    for keyword in keywords:
        # Count occurrences (10 points each)
        count = text.lower().count(keyword.lower())
        score += count * 10

        # Bonus for exact word match (5 points)
        if f' {keyword.lower()} ' in f' {text.lower()} ':
            score += 5

    return score
```

**Scoring breakdown:**
- **10 points** per keyword occurrence (substring match)
- **+5 points** for exact word boundary match
- **Total:** Sum across all keywords

### Example Scoring

Text: "The plink_merger pipeline processes plink files efficiently"
Keywords: ["plink", "merger"]

**Scoring:**
- "plink" appears 2 times: 2 × 10 = 20 points
- "plink" exact word match: +5 points
- "merger" appears 1 time: 1 × 10 = 10 points
- "merger" is substring (plink_merger), no exact match bonus
- **Total: 35 points**

## Multi-Keyword Semantics

Keywords are treated as **OR** (union), not AND (intersection):
- `--keyword "plink manifest"` finds conversations with "plink" OR "manifest"
- Higher score if both appear, but not required

**Why OR instead of AND:**
- More forgiving (fewer false negatives)
- Users can refine by inspecting top results
- Combined with other filters (file, date) for precision

**Alternative approach (not implemented):**
Could offer `--require-all` flag for AND semantics.

## Optimization Strategies

### For Large Log Sets (1000+ conversations)

**Problem:** Scanning all JSONL files can be slow.

**Strategies:**

1. **Date filtering first:**
   ```bash
   --since 2025-11-01  # Reduces file count before parsing
   ```

2. **File filtering:**
   ```bash
   --file "plink_merger"  # Only parse conversations touching that file
   ```

3. **Limit early:**
   ```bash
   --limit 5  # Show top 5, skip sorting rest
   ```

**Future optimization:** Index conversations (SQLite/JSON) with:
- File paths touched
- Date ranges
- Common keywords
- Message counts

### For Slow Regex Searches

Current implementation uses string methods (`count`, `in`), not regex.

**Why:** Performance! String methods are faster than regex for simple substring matching.

**When regex helps:**
- Pattern matching: "error.*failed"
- Word boundaries: `\bplink\b`
- Case-insensitive with special chars

**Not implemented yet:** Could add `--regex` flag for power users.

## Handling Typos and Variants

### Current Limitation

Exact substring match only. Typos fail:
- Search "manafest" won't find "manifest"
- Search "plink" won't find "PLINK" (case-insensitive, but...)

### Workarounds

1. **Try multiple spellings:**
   ```bash
   --keyword "manifest checkpoint status"  # OR semantics helps
   ```

2. **Use abbreviations:**
   ```bash
   --keyword "plink plnk"  # Common typos
   ```

3. **Partial words:**
   ```bash
   --keyword "manif"  # Catches "manifest", "manifold"
   ```

### Future Enhancement: Fuzzy Matching

Could use Levenshtein distance for typo tolerance:

```python
from difflib import get_close_matches

def fuzzy_keywords(keyword, text_words, cutoff=0.8):
    return get_close_matches(keyword, text_words, cutoff=cutoff)
```

**Trade-off:** Slower, more false positives.

## Semantic Search (Not Implemented)

### What It Would Enable

Find conversations by meaning, not keywords:
- Search "authentication" finds "login", "credentials", "OAuth"
- Search "error handling" finds "exception", "try/catch", "failure"

### Implementation Approaches

1. **Embedding-based:**
   - Generate embeddings for each message (sentence-transformers)
   - Store in vector database (FAISS, ChromaDB)
   - Similarity search at query time

2. **LLM-based:**
   - Pass conversation to LLM with query
   - Ask "Is this conversation about X?"
   - Rank by LLM confidence

**Trade-offs:**
- Much slower (embeddings or LLM calls)
- Requires dependencies (transformers, torch)
- Higher resource usage
- More false positives (semantic similarity != relevance)

**When worth it:**
- Large conversation corpus (5000+)
- Frequent searches
- Willing to pre-process logs

## File Path Matching Strategy

### Current Implementation

Simple substring match (case-insensitive):

```python
if file_filter.lower() in file_path.lower():
    matched = True
```

**Examples:**
- Filter "plink_merger.py" matches "/path/to/plink_merger.py"
- Filter "merger" matches "plink_merger.py", "merger_cli.py", "test_merger.py"
- Filter "scripts/plink" matches "scripts/plink_merger/plink_merger.py"

### Glob Pattern Matching (Future)

Could support glob patterns:

```bash
--file "scripts/plink_merger/*.py"  # Only Python files in that dir
--file "**/*_test.py"  # All test files
```

**Implementation:**
```python
from pathlib import Path
import fnmatch

if fnmatch.fnmatch(file_path, file_filter):
    matched = True
```

## Ranking and Sorting

### Primary Sort Key

Conversations sorted by **total relevance score** (descending).

**Why:** Most relevant results first.

### Tie-Breaking (Not Implemented)

When scores equal, could sort by:
1. **Recency** - More recent first
2. **Message count** - More active conversations first
3. **File count** - More files touched = more substantial

**Current behavior:** Arbitrary order (file system order).

## Result Limiting

### How --limit Works

```bash
--limit 10  # Show top 10 results
```

**Process:**
1. Score all conversations
2. Sort by score (descending)
3. Take first N results
4. Format and display

**Performance note:** Still scores ALL conversations, just displays fewer. For performance, combine with date/file filters.

### Pagination (Not Implemented)

Could add offset for pagination:

```bash
--limit 10 --offset 0   # Results 1-10
--limit 10 --offset 10  # Results 11-20
```

## Time-Based Filtering Strategy

### File Modification Time

```python
mtime = datetime.fromtimestamp(stat.st_mtime)
if since and mtime.date() < since:
    continue
```

**Uses:** File modification time (when JSONL file last changed).

**Limitation:** Not conversation start time (first message timestamp).

**Why:** Faster! No need to open file and parse first line.

### Conversation Timestamp (Future)

Could extract from first message:

```python
with open(jsonl_file) as f:
    first_line = f.readline()
    data = json.loads(first_line)
    conversation_time = datetime.fromisoformat(data['timestamp'])
```

**Trade-off:** Slower (open every file), but more accurate.

## Combined Filter Logic

### Multiple Filters (AND)

All filters must match:

```bash
--keyword "plink" --file "merger" --since 2025-11-01
```

**Logic:**
1. Find files modified since 2025-11-01
2. Parse each file
3. Check if "plink" keyword found
4. Check if "merger" in file paths touched
5. Include only if all conditions met

### Filter Order for Performance

Optimal order:
1. **Date filter** - Reduces file count (fast)
2. **File filter** - Reduces parsing load (medium)
3. **Keyword filter** - Scores remaining (slow)

**Current implementation:** Date filtering happens first (during file discovery), others during parsing.

## Scoring Refinements (Future)

### Position-Based Scoring

Give higher weight to keywords in:
- First user message (conversation topic)
- Headings/titles
- Tool names
- File paths

### Context-Aware Scoring

Consider surrounding words:
- "memory leak bug" > "memory" + "leak" + "bug" separately
- Phrase matching with proximity scoring

### User Feedback Loop

Track which results users select:
- Boost similar conversations
- Learn user's search intent
- Personalized ranking

## Performance Benchmarks

### Current Performance (Approximate)

- **100 conversations:** ~1-2 seconds
- **500 conversations:** ~5-10 seconds
- **1000 conversations:** ~15-20 seconds

**Bottleneck:** File I/O and JSON parsing.

### Optimization Ideas

1. **Parallel processing:**
   ```python
   from multiprocessing import Pool
   with Pool() as pool:
       results = pool.map(search_conversation, file_paths)
   ```

2. **Incremental indexing:**
   - Process new files only
   - Cache results in SQLite
   - Update index on file changes

3. **Lazy evaluation:**
   - Stream results as found
   - Stop early when enough high-scoring matches

## Search Quality Metrics

### Precision

Of returned results, how many are relevant?

**Current:** Unknown (no user feedback yet).

**How to measure:** Track which results user views/summarizes.

### Recall

Of all relevant conversations, how many found?

**Challenge:** Hard to know ground truth (all relevant conversations).

**Proxy metric:** User satisfaction ("Did I find what I needed?")

### Ranking Quality

Are most relevant results at top?

**Measure:** Mean Reciprocal Rank (MRR)
- If first relevant result at position 1: score = 1.0
- If first relevant result at position 2: score = 0.5
- If first relevant result at position 3: score = 0.33

## Future Research Directions

1. **Query expansion:** "plink" → ["plink", "PLINK", "plnk", "plink_merger"]
2. **Temporal decay:** Boost recent conversations
3. **Active learning:** Improve from user clicks
4. **Cross-conversation links:** "Related conversations"
5. **Summarization integration:** Search summaries instead of full text
