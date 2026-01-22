# Bioinformatics Visualization Patterns

## Differential Expression

### Volcano Plot

Show -log10(p-value) vs log2(fold-change) with FDR thresholds and labeled top hits.

```python
import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text

fig, ax = plt.subplots(figsize=(4, 4))

# Color by significance
colors = np.where(
    (df['padj'] < 0.05) & (df['log2FC'] > 1), 'red',
    np.where((df['padj'] < 0.05) & (df['log2FC'] < -1), 'blue', 'grey')
)

ax.scatter(df['log2FC'], -np.log10(df['pvalue']), c=colors, alpha=0.5, s=10)

# FDR threshold line
ax.axhline(-np.log10(0.05), color='black', linestyle='--', linewidth=0.5)

# Fold-change thresholds
ax.axvline(1, color='black', linestyle='--', linewidth=0.5)
ax.axvline(-1, color='black', linestyle='--', linewidth=0.5)

# Label top hits
top_genes = df.nsmallest(10, 'pvalue')
texts = [ax.text(row['log2FC'], -np.log10(row['pvalue']), row['gene'])
         for _, row in top_genes.iterrows()]
adjust_text(texts)

ax.set_xlabel('log2(Fold Change)')
ax.set_ylabel('-log10(p-value)')
```

### MA Plot

Show log2(fold-change) vs mean expression to identify intensity bias.

```python
ax.scatter(df['baseMean'], df['log2FC'], alpha=0.3, s=5)
ax.axhline(0, color='red', linestyle='--')
ax.set_xscale('log')
ax.set_xlabel('Mean Expression')
ax.set_ylabel('log2(Fold Change)')
```

## Dimensionality Reduction

### UMAP/t-SNE Guidelines

- Color by cell type, condition, or QC metric
- Avoid over-interpretation of distances (especially t-SNE)
- Stratify by batch/condition in faceted subplots
- Always set random seeds for reproducibility

```python
import scanpy as sc

# Reproducible embedding
sc.tl.umap(adata, random_state=42)

# Faceted by condition
fig, axes = plt.subplots(1, 3, figsize=(10, 3))
for ax, condition in zip(axes, conditions):
    subset = adata[adata.obs['condition'] == condition]
    sc.pl.umap(subset, color='cell_type', ax=ax, show=False, title=condition)
```

### PCA Visualization

- Scree plot for variance explained
- Loadings plot for feature contributions
- Biplot for combined view

```python
# Scree plot
variance_ratio = pca.explained_variance_ratio_
ax.bar(range(1, len(variance_ratio)+1), variance_ratio)
ax.set_xlabel('Principal Component')
ax.set_ylabel('Variance Explained')
```

## Quality Control

### Read Depth Distributions

```python
# Violin/box per sample
sns.violinplot(data=df, x='sample', y='read_depth', inner='box')
plt.xticks(rotation=45)
```

### Mitochondrial Fraction (scRNA-seq)

```python
sc.pl.violin(adata, 'pct_counts_mt', groupby='sample')
```

### Saturation Curves

Plot unique molecules vs sequencing depth to assess library complexity.

## Heatmaps

### Clustered Heatmap

```python
import seaborn as sns

# Row-normalize for gene expression
row_normalized = (df - df.mean(axis=1).values[:, None]) / df.std(axis=1).values[:, None]

g = sns.clustermap(
    row_normalized,
    cmap='RdBu_r',  # Diverging for comparison to mean
    center=0,
    row_cluster=True,
    col_cluster=True,
    figsize=(8, 10),
    dendrogram_ratio=(0.1, 0.1),
    cbar_pos=(0.02, 0.8, 0.03, 0.15)
)
```

### Color Scale Guidelines

- **Diverging** (RdBu_r, coolwarm): When comparing to control/mean, center on zero
- **Sequential** (viridis, plasma): For absolute values
- **Clip at percentiles** (1st-99th) if outliers saturate scale

## Networks and Pathways

### Network Visualization

```python
import networkx as nx

G = nx.from_pandas_edgelist(edges_df, 'source', 'target')

# Node attributes
node_sizes = [centrality[n] * 1000 for n in G.nodes()]
node_colors = [expression[n] for n in G.nodes()]

pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, node_size=node_sizes, node_color=node_colors,
        cmap='viridis', with_labels=True, font_size=8)
```

### Pathway Enrichment Dot Plot

```python
# Dot plot: x = fold enrichment, y = pathway, size = gene count, color = -log10(p)
ax.scatter(df['fold_enrichment'], df['pathway'],
           s=df['gene_count']*10, c=-np.log10(df['pvalue']), cmap='Reds')
```

## Set Overlaps

### UpSet Plot (preferred over Venn)

```python
from upsetplot import plot, from_contents

# Create membership dict
sets = {
    'Set A': list_a,
    'Set B': list_b,
    'Set C': list_c
}

plot(from_contents(sets), show_counts=True)
```

Venn diagrams become unreadable beyond 3 sets. UpSet plots scale to any number of sets and show intersection sizes as bars.

## Distribution Comparisons

### Raincloud Plot

Half-violin + jittered points + box plot for complete distribution view.

```python
import ptitprince as pt

pt.RainCloud(data=df, x='group', y='value', palette='Set2',
             width_viol=0.6, alpha=0.65, dodge=True)
```

### Strip/Swarm for Small n

```python
# When n < 30 per group, show individual points
sns.swarmplot(data=df, x='group', y='value', size=4)
sns.boxplot(data=df, x='group', y='value', showcaps=False,
            boxprops={'facecolor': 'none'}, whiskerprops={'linewidth': 0})
```
