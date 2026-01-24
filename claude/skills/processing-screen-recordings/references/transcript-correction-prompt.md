# Transcript Correction Prompt Template

Use this prompt template when launching parallel correction tasks. The prompt is model-agnostic - use with any fast, cost-effective model (e.g., `haiku`, `gpt-4o-mini`, `gemini-flash`).

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
