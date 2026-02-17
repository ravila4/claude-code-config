# Callout Conventions

Obsidian callout types used in daily journal entries, with placement guidance and real examples.

## `[!info]` — Context and References

**Placement:** Top of entry for continuity; inline for reference material.

```markdown
> [!info] Context
> Continued from [[2026-01-30]] - testing whether filtered phenotypes fix the LOCO offset mismatch.
```

**Collapsible variant** (`[!info]-`) for bulky reference material:

```markdown
> [!info]- Cloud Logging URLs
> - [empiroar](https://console.cloud.google.com/logs/query;query=...)
> - [regenie](https://console.cloud.google.com/logs/query;query=...)
```

## `[!success]` — Wins, Milestones, Progress

Flexible title — scale to match the magnitude. "Win" for a single thing, "Big day" for multiple breakthroughs, "Progress" for incremental.

```markdown
> [!success] Win
> Both Score test and Firth regression produce **identical results** between empiroar and regenie (r=1.0000 for both BETA and P-value).
```

```markdown
> [!success] Big day
>
> - Solved the LOCO offset mystery (WGR variant mismatch)
> - Confirmed regenie filters nulls internally
> - Designed clean architecture for job registry + remote execution
```

```markdown
> [!success] Progress
>
> - Created filtered phenotype file (non-null only: 166,460 samples from 370k total)
> - Submitted regenie step1 with filtered phenotypes
```

## `[!warning]` — Concerns, Friction, Blockers

For things that are impeding work or showing signs of future trouble.

```markdown
> [!warning] Blocker
> Still can't get regenie step 2 to recognize the covariate file.
```

```markdown
> [!warning] Growing Pain
> The flat TSV registry is starting to show friction as the column count grows (now 46 → 52 with this PR). The core issue isn't the storage format -- it's that many columns are **structurally null** depending on the tool/step combination.
```

## `[!question]` — Open Loops

For things still being thought through. Strikethrough completed items rather than deleting them.

```markdown
> [!question] Still thinking about...
>
> - ~~Need to run join for all_firth experiment, then analyze both~~ Done!
> - Should we switch the registry to a relational format?
```

## `[!bug]` — Bugs Discovered

For bugs found during the day's work.

```markdown
> [!bug] Script Bug Found
> The sample filtering script was silently dropping samples with missing FID fields instead of mapping them.
```

## `[!note]` — Observations

For non-actionable insights, things noticed but not necessarily acted on.

```markdown
> [!note] Observation: empiroar regression-only vs regenie elapsed
> empiroar completes regression in ~40min vs regenie's ~2hr for the same variant set.
```
