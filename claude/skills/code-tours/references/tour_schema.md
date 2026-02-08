# CodeTour .tour File Schema

## File Location

Place tour files in `.tours/` at the project root. Name files as `kebab-case.tour`.

Ensure `.tours/` is gitignored unless tours are meant to be shared.

## Minimal Valid Tour

```json
{
  "$schema": "https://aka.ms/codetour-schema",
  "title": "Tour title",
  "steps": [
    {
      "title": "Step title",
      "description": "Markdown description of this location.",
      "file": "src/main.py",
      "line": 10
    }
  ]
}
```

## Full Schema

### Tour-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `$schema` | No | Always `"https://aka.ms/codetour-schema"` |
| `title` | **Yes** | Display name of the tour |
| `description` | No | Brief summary of what the tour covers |
| `ref` | No | Git ref (branch/tag/commit SHA) the tour was created against |
| `isPrimary` | No | Boolean; marks this as the default tour |
| `nextTour` | No | Title of the next tour to play after this one |
| `steps` | **Yes** | Array of step objects |

### Step-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `description` | **Yes** | Markdown content explaining this step |
| `title` | No | Short label for the step (shown in tour navigation) |
| `file` | No | Workspace-relative path to a file |
| `line` | No | 1-based line number within the file. Use when pinned to a `ref`. |
| `pattern` | No | Regex to locate the step. **Use `line` or `pattern`, not both.** |
| `directory` | No | Workspace-relative path to a directory (overrides `file`) |
| `selection` | No | Object: `{start: {line, character}, end: {line, character}}` (1-based) |

### Choosing `line` vs `pattern`

Use **`line`** when:
- The tour is pinned to a specific commit via `ref` (line numbers are stable at that ref)
- The tour is ephemeral and will be consumed immediately

Use **`pattern`** when:
- The tour should survive edits to the file
- No `ref` is set
- The target code has a distinctive signature

**Good patterns** (unique, stable):
- `def process_payment\\(` -- unique function signature
- `class UserSerializer` -- class definition
- `CACHE_TTL\\s*=` -- specific config constant

**Bad patterns** (ambiguous, fragile):
- `return` -- matches everywhere
- `import` -- too common
- `def get` -- matches many functions

**JSON escaping**: Backslashes in regex must be double-escaped in JSON. The regex `cache\.invalidate` becomes `"cache\\.invalidate"` in JSON.

### General tips

- Keep `file` paths workspace-relative with forward slashes.
- Always include a `title` on each step for navigation clarity.

## Compatibility

- **VS Code**: Full support via the [CodeTour extension](https://marketplace.visualstudio.com/items?itemName=vsls-contrib.codetour)
- **Neovim**: Basic support via [codetour.nvim](https://github.com/magnuswahlstrand/codetour.nvim) (loads tours, navigates steps)
- **IntelliJ**: Community plugin available
- **Raw JSON**: Human-readable as fallback; file:line references can be followed manually
