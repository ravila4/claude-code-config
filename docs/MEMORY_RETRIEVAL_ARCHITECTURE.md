# Memory Retrieval Architecture

## Problem Statement

The flat-file memory specification ([CLAUDE_FLAT_FILE_MEMORY_SPEC.md](CLAUDE_FLAT_FILE_MEMORY_SPEC.md)) defines **how** to store memories (schemas, file formats, atomic writes), but only vaguely specifies **how** to retrieve them.

### Current State

**Storage:** ✅ Well-specified
- Schemas for patterns, sources, backlog, events
- Atomic write protocol (tmp → fsync → rename)
- Deterministic file naming (`mem_<uuid>.json`)
- Validation against JSON schemas

**Retrieval:** ⚠️ Underspecified
- Section 8 says agents "may" filter/search
- "Simple substring search" on title/do_text/dont_text
- "Crude lexical match score" + recency boost + confidence
- **No concrete implementation or responsible agent**

### Memory Storage Patterns

**Direct Writers** (agents that write directly to `.memories/` subdirectories):
- `gemini-consultant` → `.memories/external-llm-cache/gemini/`
- `gpt5-consultant` → `.memories/external-llm-cache/gpt5/`
- `codex-consultant` → `.memories/external-llm-cache/codex/`
- `architecture-devils-advocate` → `.memories/architecture-reviews/`
- `multi-perspective-reviewer` → `.memories/reviews/`

**Indirect Writers** (agents that should use memory-knowledge-keeper):
- `python-code-reviewer`, `python-debugger`, `software-architect`, `mermaid-expert`, `visual-design-critic`
- They reference storing in `.memories/` but don't specify HOW

**The Gap:** memory-knowledge-keeper claims to "query knowledge graphs" and "retrieve historical context" but provides no implementation details.

---

## Short-term Solution: Flat-File Search

### Design Principles

1. **memory-knowledge-keeper is the primary retrieval agent**
2. **Use existing Claude Code tools** (Grep, Read, Glob)
3. **Implement the ranking algorithm from the spec** (recency + confidence + lexical match)
4. **Keep result sets small** (top 20 max, compact snippets)
5. **Provide clean API** for other agents to query memories

### Implementation Strategy

#### 1. Search by Category/Tags (Fast Filter)

Use `Glob` to find all memory files, then `Grep` to filter by category:

```bash
# Find all pattern memory files
claude/agents/schemas/*.json
.memories/memories/mem_*.json

# Grep for category
grep -l '"category": "data-fetching"' .memories/memories/mem_*.json
```

#### 2. Semantic Search (Substring Match)

Use `Grep` with case-insensitive substring search:

```bash
# Search in title, do_text, dont_text
grep -i "pandas.*chained" .memories/memories/mem_*.json
```

#### 3. Load and Rank Results

Use `Read` to load matching files, parse JSON, then rank:

**Ranking Formula (from spec Section 8):**
```python
score = (confidence * 0.5) + (recency_boost * 0.3) + (lexical_match * 0.2)

where:
  confidence = 0.0-1.0 from memory file
  recency_boost = 1.0 if < 30 days old, else exponential decay
  lexical_match = substring matches / total words (crude)
```

#### 4. Return Compact Results

```json
{
  "query": "pandas chained assignment",
  "matches": [
    {
      "id": "2b6ce1b8-2b2f-4a9e-9f47-3b5409185f0e",
      "title": "Pandas chained assignment pattern",
      "category": "data-processing",
      "confidence": 0.95,
      "learned_at": "2025-10-18T13:40:35Z",
      "do_snippet": "df.loc[mask, 'column'] = value",
      "dont_snippet": "df[mask]['column'] = value",
      "score": 0.89
    }
  ],
  "total_scanned": 47,
  "returned": 1
}
```

### Memory-Knowledge-Keeper Retrieval API

Other agents should call memory-knowledge-keeper with queries like:

```markdown
I need to retrieve patterns related to "pandas DataFrame assignment"

Context:
- Category: data-processing
- Severity: error or warning
- Recent (last 30 days preferred)
- Top 5 results

Please return:
- Pattern ID
- DO/DONT snippets
- Confidence score
- When it was learned
```

memory-knowledge-keeper executes:
1. Grep `.memories/memories/` for category + keywords
2. Read matching files
3. Parse JSON and rank by formula
4. Return top N with compact snippets

### Cache Retrieval for External LLMs

Similar strategy for external-llm-cache:

```bash
# Find all Gemini responses about a topic (no time limit)
find .memories/external-llm-cache/gemini/ -name "*dataframe*"

# Or search by most recent first
ls -t .memories/external-llm-cache/gemini/*dataframe*
```

Load JSON and check timestamp:
```json
{
  "timestamp": "2025-10-18T16:00:00Z",
  "question": "Why DataFrame returning NaN",
  "response_summary": "...",
  "cached_days_ago": 1
}
```

**Important distinction:**
- **External LLM consultant agents** use 24h cache validity to avoid redundant API calls for the **exact same question**
- **memory-knowledge-keeper retrieval** returns **all relevant cached responses** regardless of age
  - Old cached responses are still valuable context (even months/years later)
  - Include timestamp and age so user knows how old the information is
  - Rank by relevance, not just recency
  - User decides if older information is still applicable

---

## Long-term Vision: Vector Database

### Motivation

Flat-file search works for small memory sets (< 1000 patterns) but doesn't scale:
- Substring matching is crude (misses semantic similarity)
- Full file scans get expensive
- No true "knowledge graph" traversal

### Architecture

```
┌─────────────────────────────────────┐
│  Claude Code Agents                 │
│  ├── python-debugger                │
│  ├── memory-knowledge-keeper        │
│  └── ... other agents               │
└──────────┬──────────────────────────┘
           │
           │ (writes to)
           ↓
┌─────────────────────────────────────┐
│  .memories/ (Flat Files)            │
│  ├── memories/mem_*.json            │
│  ├── external-llm-cache/            │
│  ├── reviews/                       │
│  └── architecture-reviews/          │
└──────────┬──────────────────────────┘
           │
           │ (ingested by)
           ↓
┌─────────────────────────────────────┐
│  Memory Ingestor                    │
│  (Periodic sync)                    │
└──────────┬──────────────────────────┘
           │
           ↓
┌─────────────────────────────────────┐
│  PostgreSQL + pgvector              │
│                                     │
│  Tables:                            │
│  ├── patterns                       │
│  │   ├── id (uuid)                  │
│  │   ├── title, category, severity  │
│  │   ├── do_text, dont_text         │
│  │   ├── confidence, learned_at     │
│  │   ├── embedding (vector)         │
│  │                                  │
│  ├── sources                        │
│  ├── backlog                        │
│  ├── events                         │
│  └── llm_cache                      │
│      ├── llm_name, timestamp        │
│      ├── question_embedding         │
│      └── response_text              │
└──────────┬──────────────────────────┘
           │
           │ (queried via)
           ↓
┌─────────────────────────────────────┐
│  query-memories CLI Utility         │
│                                     │
│  $ query-memories \                 │
│      --query "pandas assignment" \  │
│      --category data-processing \   │
│      --top 5                        │
│                                     │
│  Returns:                           │
│  - Semantic similarity score        │
│  - Weighted by confidence + recency │
│  - With DO/DONT snippets            │
└─────────────────────────────────────┘
```

### CLI Utility Design

```bash
# Basic query
query-memories --query "pandas chained assignment" --top 5

# Filter by category
query-memories --query "error handling" --category debugging --top 3

# Recency-weighted
query-memories --query "dagster patterns" --recent 30d

# Confidence threshold
query-memories --query "database schema" --min-confidence 0.8
```

**Returns:**
```json
{
  "query": "pandas chained assignment",
  "results": [
    {
      "id": "2b6ce1b8-2b2f-4a9e-9f47-3b5409185f0e",
      "title": "Pandas chained assignment pattern",
      "similarity": 0.94,
      "confidence": 0.95,
      "recency_days": 1,
      "composite_score": 0.91,
      "do_text": "df.loc[mask, 'column'] = value",
      "dont_text": "df[mask]['column'] = value"
    }
  ]
}
```

### Embedding Strategy

**What to embed:**
- `title + do_text + dont_text + category`
- Concatenate into single text passage
- Generate embedding using sentence-transformers or OpenAI embeddings API

**Similarity search:**
```sql
SELECT
  id, title, do_text, dont_text, confidence, learned_at,
  1 - (embedding <=> query_embedding) AS similarity
FROM patterns
WHERE category = 'data-processing'
ORDER BY
  (1 - (embedding <=> query_embedding)) * 0.5 +  -- semantic similarity
  confidence * 0.3 +                              -- confidence weight
  CASE
    WHEN learned_at > NOW() - INTERVAL '30 days' THEN 0.2
    ELSE 0.1
  END                                              -- recency boost
DESC
LIMIT 5;
```

### Ingestor Implementation

Periodic background job (cron or systemd timer):

```python
# ingest-memories.py
import json
import glob
from datetime import datetime
from sentence_transformers import SentenceTransformer
import psycopg2

model = SentenceTransformer('all-MiniLM-L6-v2')

for filepath in glob.glob('.memories/memories/mem_*.json'):
    with open(filepath) as f:
        memory = json.load(f)

    # Create embedding
    text = f"{memory['title']} {memory['do_text']} {memory['dont_text']} {memory['category']}"
    embedding = model.encode(text).tolist()

    # Upsert to DB
    conn = psycopg2.connect("dbname=memories user=postgres")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO patterns (id, title, category, do_text, dont_text,
                              confidence, learned_at, embedding)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
          embedding = EXCLUDED.embedding,
          confidence = EXCLUDED.confidence
    """, (memory['id'], memory['title'], memory['category'],
          memory['do_text'], memory['dont_text'],
          memory['confidence'], memory['learned_at'],
          embedding))
    conn.commit()
```

### Agent Integration

Agents can query via CLI:

```python
# In memory-knowledge-keeper agent
result = subprocess.run([
    'query-memories',
    '--query', 'pandas chained assignment',
    '--category', 'data-processing',
    '--top', '5',
    '--format', 'json'
], capture_output=True, text=True)

memories = json.loads(result.stdout)
```

Or via Python library:

```python
from memory_retrieval import MemoryRetriever

retriever = MemoryRetriever(db_url='postgresql://localhost/memories')
results = retriever.query(
    query="pandas chained assignment",
    category="data-processing",
    top_k=5,
    min_confidence=0.7
)
```

---

## Migration Path

### Phase 1: Flat-File Search (Immediate)
**Timeline:** Now
**Effort:** Low (use existing Grep/Read tools)
**Benefit:** Functional retrieval for small memory sets

**Actions:**
1. Update memory-knowledge-keeper with concrete search implementation
2. Document search patterns for other agents
3. Provide examples of querying memories

### Phase 2: CLI Utility (Short-term)
**Timeline:** 1-2 weeks
**Effort:** Medium (Python script + basic ranking)
**Benefit:** Centralized retrieval logic, better ranking

**Actions:**
1. Create `query-memories` Python script
2. Implement ranking formula from spec
3. Add JSON output format
4. Document usage for agents

### Phase 3: Vector DB (Long-term)
**Timeline:** 1-3 months
**Effort:** High (DB setup, embedding generation, ingestor)
**Benefit:** Scales to thousands of memories, semantic search

**Actions:**
1. Set up PostgreSQL + pgvector
2. Create schema and tables
3. Build ingestor with sentence-transformers
4. Migrate `query-memories` to use vector DB
5. Add vector search to memory-knowledge-keeper

---

## Current Recommendation

**For this agent ecosystem consolidation:**
1. Update memory-knowledge-keeper with concrete flat-file search implementation
2. Document the retrieval API for other agents
3. Note the vector DB path as future work

**Future work should prioritize:**
- CLI utility for centralized retrieval logic
- Vector DB when memory count > 500 patterns
- Semantic search for better pattern matching
