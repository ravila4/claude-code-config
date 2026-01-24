# Transcript Correction Prompt Template

Use this prompt template when launching parallel correction tasks. The prompt is model-agnostic - use with any fast, cost-effective model (e.g., `haiku`, `gpt-4o-mini`, `gemini-flash`).

## Parallel Execution Pattern

**CRITICAL: Launch ALL tasks in a SINGLE message**

```
Correct (parallel - 1x time):
┌─────────────────────────────────────────┐
│ Single message with 8 Task tool calls   │
│ → All run simultaneously                │
│ → Total time = slowest single chunk     │
└─────────────────────────────────────────┘

Wrong (sequential - 8x time):
┌─────────────────────────────────────────┐
│ Message 1: Task 1 → wait for result     │
│ Message 2: Task 2 → wait for result     │
│ ... (8 separate round-trips)            │
│ → Total time = sum of all chunks        │
└─────────────────────────────────────────┘
```

### Chunk Size Guidance

| Recording Length | Chunk Size | Parallel Agents | Rationale |
|------------------|------------|-----------------|-----------|
| < 20 min | 50 blocks | 3-5 | Fewer chunks, still fast |
| 20-40 min | 35-40 blocks | 6-10 | Sweet spot for parallelism |
| > 40 min | 30-35 blocks | 10-15 | More agents = faster overall |

**Key insight:** Smaller chunks with more agents completes faster than larger chunks with fewer agents, because all agents run simultaneously.

## Prompt Template

```
You are a transcript correction assistant. Fix transcription errors in this SRT chunk.

DOMAIN WORD LIST (correct spellings):
[paste word list contents here]

SRT CHUNK TO CORRECT:
[paste chunk contents here]

Return ONLY a JSON object with this exact structure (no markdown, no explanation):
{
  "corrections": [
    {"line": 12, "original": "fee was", "corrected": "GWAS"},
    {"line": 45, "original": "Regini", "corrected": "Regenie"}
  ],
  "suggested_new_terms": ["TermNotInList"],
  "corrected_srt": "1\n00:00:00,000 --> 00:00:05,000\nCorrected text here\n\n2\n..."
}

Rules:
- Only include actual corrections in the "corrections" array
- Preserve all SRT timing and formatting exactly
- Focus on technical terms, tool names, acronyms, and proper nouns
- Add terms to "suggested_new_terms" if you correct something not in the word list
- If unsure, keep the original text
```

## Task Parameters

When launching parallel correction tasks:

```python
Task(
    description="Correct transcript chunk N",
    subagent_type="general-purpose",
    model="haiku",  # or other fast model
    prompt=<prompt from template above>
)
```

## Merging Results

After all parallel tasks complete:

1. **Combine corrected SRT chunks** in order into `<basename>.corrected.srt`
2. **Merge all corrections** into a single `corrections.json`:

```json
{
  "source_file": "2026-01-22_15-48-04.srt",
  "total_corrections": 18,
  "corrections": [
    {"line": 12, "original": "fee was", "corrected": "GWAS"},
    {"line": 45, "original": "Regini", "corrected": "Regenie"}
  ],
  "suggested_new_terms": ["NewTerm1", "NewTerm2"]
}
```

3. **Report to user:**
   - Number of corrections made
   - List of corrections (original → corrected)
   - Any suggested new terms for the word list
