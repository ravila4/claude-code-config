---
name: dataframe-analysis
description: Opinionated best practices for DataFrame-based analysis. Use when joining datasets, creating analysis tables, writing plotting functions, or comparing results across dimensions. Covers wide table design, boolean flag patterns, join validation, and column naming conventions.
triggers:
  - user-invocable
---

# DataFrame Analysis Best Practices

Opinionated patterns for DataFrame-centric analysis. The core philosophy: one wide table with semantic columns beats many filtered subsets.

Examples use bioinformatics data (GWAS, variant annotations, QC metrics) but patterns apply broadly to any tabular analysis.

## Core Principles

### 1. One Wide Table

Join everything upfront into a single table. Each row is the unit of analysis (variant, gene, sample, user, transaction). Columns are cheap; mid-analysis joins are expensive—both cognitively and computationally.

```python
# Join once, use everywhere
df = (
    gwas1
    .merge(gwas2, on="variant_id", suffixes=("_gwas1", "_gwas2"), how="outer", validate="1:1")
    .merge(annotations, on="variant_id", how="left", validate="1:1")
    .merge(qc_metrics, on="variant_id", how="left", validate="1:1")
)
```

**Not this:**
```python
# BAD: Creating mini-DataFrames for each plot
plot_data = pd.DataFrame({
    "p_gwas1": gwas1.loc[common_idx, "pvalue"],
    "p_gwas2": gwas2.loc[common_idx, "pvalue"],
})
# Now you need another one for the next plot...
```

Benefits:
- Adding a dimension (color by consequence, facet by MAF) = one parameter change
- No namespace clutter from `df_rare`, `df_sig`, `df_european`
- Consistent row alignment across all analyses

**When NOT to use wide tables:**
- Memory genuinely constrained and columns won't be needed
- Truly independent analyses with no shared dimensions
- Complex m:n relationships that would explode row count

### 2. Boolean Flags Over Filtered Copies

Add `is_*` or `pass_*` boolean columns instead of creating subset DataFrames.

```python
# Flags
df["is_rare"] = df["maf"] < 0.01
df["is_sig_p5e8"] = df["pvalue"] < 5e-8
df["pass_qc"] = (df["call_rate"] > 0.95) & (df["hwe_p"] > 1e-6)
df["is_eur"] = df["ancestry"] == "EUR"

# Combine naturally
rare_significant = df[df.is_rare & df.is_sig_p5e8]
```

Naming conventions:
- `is_*`: state/category membership (`is_rare`, `is_coding`, `is_eur`)
- `pass_*`: QC filter outcomes (`pass_qc`, `pass_geno`, `pass_hwe`)
- Encode thresholds in name when ambiguous: `is_sig_p5e8`, `is_rare_maf01`

### 3. Pre-computed Bins for Stratification

Create categorical bin columns upfront for faceting and groupby operations.

```python
df["maf_bin"] = pd.cut(
    df["maf"],
    bins=[0, 0.001, 0.01, 0.05, 0.5],
    labels=["ultra_rare", "rare", "low_freq", "common"]
)
df["consequence_group"] = df["consequence"].map(CONSEQUENCE_GROUPS)
```

Benefits:
- Ready for `sns.FacetGrid` or `df.groupby()` without recomputing
- Consistent bin definitions across all plots

### 4. Canonical Derived Columns

Compute derived values once and store them. Never mix "compute on the fly" across different functions.

```python
# Compute once. clip() prevents -inf from log(0)
df["neglog10_p"] = -np.log10(df["pvalue"].clip(lower=1e-300))
df["abs_beta"] = df["beta"].abs()
df["odds_ratio"] = np.exp(df["beta"])
```

### 5. Plot Functions: DataFrame + Column Names

Pass the full DataFrame and specify columns by name. Never extract to arrays first.

```python
def plot_manhattan(
    df: pd.DataFrame,
    *,
    chrom_col: str = "chrom",
    pos_col: str = "pos",
    pval_col: str = "neglog10_p",
    color_col: str | None = None,
    highlight_col: str | None = None,  # boolean column for highlighting points
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """Manhattan plot from DataFrame columns."""
    plot_df = df[df[highlight_col]] if highlight_col else df
    # ... plotting logic
```

Benefits:
- Adding color/facet = one more parameter
- No data restructuring when requirements change
- Function signature documents the expected schema

## Recommended Build Order

When constructing a wide analysis table:

1. **Join** all source tables (validate cardinality)
2. **Add provenance flags** (`has_*`, `in_*`) to track join missingness
3. **Add boolean flags** (`is_*`, `pass_*`) for filtering conditions
4. **Add categorical bins** (`*_bin`, `*_group`) for stratification
5. **Add derived columns** (transforms, computed values)

## Join Hygiene

### Always Validate Cardinality

```python
df = left.merge(right, on="variant_id", how="outer", validate="1:1")
```

### Track Join Missingness

After outer joins, add provenance flags and inspect immediately:

```python
df["has_gwas1"] = df["pvalue_gwas1"].notna()
df["has_gwas2"] = df["pvalue_gwas2"].notna()
df["in_both"] = df["has_gwas1"] & df["has_gwas2"]

# Immediately inspect—are nulls expected?
print(df[["has_gwas1", "has_gwas2", "in_both"]].value_counts())
```

### Diagnostic Pattern: Boolean Combinations

Understand filter interactions before committing to a subset:

```python
# Cross-tabulate two flags
pd.crosstab(df.pass_qc, df.is_rare)

# Multi-flag breakdown
df.groupby(["pass_qc", "is_rare", "is_sig_p5e8"]).size()
```

## Anti-patterns

### Don't: Silent Fallbacks for Expected Columns

```python
# BAD: Hides schema bugs, produces misleading results
if "regression_type" in df.columns:
    df["is_score_test"] = df["regression_type"] == "score"
else:
    df["is_score_test"] = False  # Silent failure - missing column looks like valid data!
```

Access the column directly and use `.fillna(False)` to handle NaN values:

```python
# GOOD: Fails loudly if column missing, handles NaN gracefully
df["is_score_test"] = (df["regression_type"] == "score").fillna(False)
```

- Column missing → KeyError (surfaces schema mismatches immediately)
- Column has NaN → becomes False (sensible default for boolean flags)

If a column is **truly optional** (rare), use a conditional with a warning:

```python
if "regression_type" in df.columns:
    df["is_score_test"] = (df["regression_type"] == "score").fillna(False)
else:
    import warnings
    warnings.warn("regression_type column not found, is_score_test defaulting to False")
    df["is_score_test"] = False
```

### Don't: Assume Categorical Values

Never assume the values in categorical columns - check first with `.value_counts()`:

```python
# BAD: Assuming value format without checking
df["is_score_test"] = df["regression_type"] == "score"  # Wrong! Actual value is "ScoreTest"

# GOOD: Check actual values first
df["regression_type"].value_counts()
# regression_type
# FisherExact        176518
# ScoreTest            9028
# FirthRegression       567

# Then use the actual values
df["is_score_test"] = (df["regression_type"] == "ScoreTest").fillna(False)
```

This applies to any column where values aren't obvious: enums, status codes, test types, categories. When in doubt, inspect before coding.

### Don't: Create Dictionary → DataFrame for Plots

```python
# BAD: Loses column metadata, can't easily add dimensions later
plot_dict = {"x": df["maf"].values, "y": df["neglog10_p"].values}
plot_df = pd.DataFrame(plot_dict)
```

### Don't: Multiple Filtered DataFrames

```python
# BAD: Proliferating subsets = namespace clutter, easy to use wrong one
df_rare = df[df.maf < 0.01]
df_common = df[df.maf >= 0.01]
df_rare_sig = df_rare[df_rare.pvalue < 5e-8]
```

### Don't: Inconsistent Transforms

```python
# BAD: Same transform computed differently = subtle bugs
def plot_qq(df):
    y = -np.log10(df["pvalue"])  # computed here

def plot_manhattan(df):
    y = df["neglog10_p"]  # uses pre-computed column
```

## Quick Reference: Column Naming

| Type | Pattern | Examples |
|------|---------|----------|
| Boolean flags | `is_*`, `pass_*` | `is_rare`, `is_sig_p5e8`, `pass_qc` |
| Categorical bins | `*_bin`, `*_group` | `maf_bin`, `consequence_group` |
| Provenance | `has_*`, `in_*` | `has_gwas1`, `in_both` |
| Transforms | descriptive | `neglog10_p`, `abs_beta`, `odds_ratio` |
| Source suffix | `_source` | `pvalue_gwas1`, `beta_ukb` |
