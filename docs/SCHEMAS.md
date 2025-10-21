# Agent Schemas

This document describes the JSON Schema definitions in `claude/agents/schemas/` used across the agent ecosystem.

## Available Schemas

### `pattern.schema.json`
Defines the structure for code patterns stored and validated by `memory-knowledge-keeper`.

**Key fields:**
- `pattern_id`: Unique identifier
- `category`: Pattern category (data-fetching, error-handling, etc.)
- `pattern.DO`: Recommended approach with code and explanation
- `pattern.DONT`: Anti-pattern to avoid
- `confidence`: Score from 0.0 to 1.0
- `source`: Where the pattern came from (user instruction, docs, etc.)

**Example:**
```json
{
  "pattern_id": "pandas-chained-assignment",
  "category": "data-processing",
  "pattern": {
    "DO": {
      "code": "df.loc[mask, 'column'] = value",
      "explanation": "Use .loc for explicit assignment to avoid SettingWithCopyWarning"
    },
    "DONT": {
      "code": "df[mask]['column'] = value",
      "explanation": "Chained indexing may not modify the original DataFrame",
      "migration": "Replace with .loc indexing"
    }
  },
  "confidence": 0.95,
  "source": {
    "type": "user-instruction",
    "date": "2025-10-18",
    "verified": true
  }
}
```

### `memory.schema.json`
Defines the structure for `.memories/` files that store project-specific knowledge.

**Key sections:**
- `patterns`: Array of code patterns (references pattern.schema.json)
- `anti_patterns`: Patterns to avoid
- `debugging_solutions`: Historical error fixes
- `architectural_decisions`: Design decisions and rationale
- `preferences`: User and project preferences

**Example:**
```json
{
  "version": "1.0",
  "project": {
    "name": "my-python-project",
    "type": "python-package"
  },
  "created": "2025-10-18T10:00:00Z",
  "updated": "2025-10-18T15:30:00Z",
  "patterns": [
    { /* pattern object */ }
  ],
  "debugging_solutions": [
    {
      "error_signature": "pandas-settingwithcopywarning",
      "error_type": "SettingWithCopyWarning",
      "solution": "Use .loc for assignments",
      "confidence": 0.95,
      "source": "debugging-session",
      "timestamp": "2025-10-18T12:00:00Z"
    }
  ]
}
```

## Usage

### Validation
Agents should validate data against these schemas before storing or exchanging information. This ensures consistency across the ecosystem.

### Schema Evolution
When updating schemas:
1. Increment the version number
2. Document changes in this file
3. Ensure backward compatibility when possible
4. Update example payloads

### `architecture-review.schema.json`
Defines the structured output from `architecture-devils-advocate` agent for critical architecture reviews.

**Key fields:**
- `review_id`: Unique identifier (YYYY-MM-DD-{topic}-{hash})
- `architecture_summary`: What's being reviewed (type, description, components)
- `critical_issues`: Prioritized architectural concerns with severity and impact
- `dry_orthogonality_violations`: Instances of repeated logic or coupling
- `alternatives`: Alternative approaches with trade-off analysis
- `risk_assessment`: Potential failure modes and mitigation strategies
- `recommendations`: Actionable next steps prioritized by impact and effort

**Example:**
```json
{
  "review_id": "2025-10-19-dagster-pipeline-abc123",
  "timestamp": "2025-10-19T10:00:00Z",
  "architecture_summary": {
    "type": "data_pipeline",
    "description": "Dagster pipeline for processing experimental results",
    "components": ["raw_data_asset", "clean_data_asset", "analysis_asset"]
  },
  "critical_issues": [
    {
      "severity": "high",
      "category": "performance",
      "description": "Loading entire dataset into memory for cleaning",
      "impact": "OOM errors with datasets > 10GB",
      "affected_components": ["clean_data_asset"]
    }
  ],
  "dry_orthogonality_violations": [
    {
      "type": "repeated_logic",
      "description": "CSV parsing logic duplicated across assets",
      "locations": ["raw_data_asset", "clean_data_asset"],
      "impact": "Changes to parsing must be duplicated in multiple places"
    }
  ],
  "alternatives": [
    {
      "name": "Chunked processing with Polars",
      "description": "Use Polars lazy evaluation to process in chunks",
      "trade_offs": {
        "pros": ["Lower memory usage", "Faster execution", "Handles large files"],
        "cons": ["New dependency", "Learning curve for Polars API"]
      },
      "implementation_notes": "Use pl.scan_csv() instead of pd.read_csv()",
      "references": ["Polars User Guide: Lazy API"]
    }
  ],
  "risk_assessment": {
    "risks": [
      {
        "category": "performance_degradation",
        "description": "Pipeline fails with large datasets",
        "likelihood": "high",
        "impact": "high",
        "mitigation": "Implement chunked processing or switch to lazy evaluation"
      }
    ]
  },
  "recommendations": [
    {
      "priority": 1,
      "action": "Switch to Polars lazy evaluation for clean_data_asset",
      "rationale": "Prevents OOM errors and improves performance",
      "effort": "medium"
    },
    {
      "priority": 2,
      "action": "Extract CSV parsing to shared utility function",
      "rationale": "DRY principle - single source of truth for parsing logic",
      "effort": "low"
    }
  ]
}
```

## Integration with Agents

| Agent | Uses Schemas |
|-------|-------------|
| memory-knowledge-keeper | pattern.schema.json, memory.schema.json |
| python-code-reviewer | pattern.schema.json (via memory-knowledge-keeper) |
| python-debugger | memory.schema.json (debugging_solutions) |
| software-architect | memory.schema.json (architectural_decisions) |
| architecture-devils-advocate | architecture-review.schema.json |
| multi-perspective-reviewer | architecture-review.schema.json (consumes reviews) |
| All agents | memory.schema.json (via memory-knowledge-keeper) |

## Future Schemas

Planned schemas based on audit document:
- `integration-message.schema.json`: Inter-agent communication format
- `validation-result.schema.json`: Pattern validation results
