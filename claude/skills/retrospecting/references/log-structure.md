# Claude Code Log Structure Reference

## Contents

- [JSONL File Format](#jsonl-file-format)
- [Message Types](#message-types)
- [Content Block Types](#content-block-types)
- [File Path Extraction Patterns](#file-path-extraction-patterns)
- [Content Structure Variations](#content-structure-variations)
- [Message Ordering](#message-ordering)
- [Special Cases](#special-cases)
- [Parsing Best Practices](#parsing-best-practices)
- [Example Parsing Code](#example-parsing-code)

## JSONL File Format

Claude Code stores conversations as newline-delimited JSON (JSONL). Each line is a complete JSON object representing a single message or event.

## Message Types

### User Messages

```json
{
  "type": "user",
  "timestamp": "2025-11-12T20:00:00.000Z",
  "message": {
    "role": "user",
    "content": "Find conversations about plink_merger"
  }
}
```

**Fields:**
- `type`: Always "user"
- `timestamp`: ISO 8601 format with timezone
- `message.role`: Always "user"
- `message.content`: String or array of content blocks

### Assistant Messages

```json
{
  "type": "assistant",
  "timestamp": "2025-11-12T20:00:01.000Z",
  "message": {
    "role": "assistant",
    "content": [
      {"type": "text", "text": "I'll search for those conversations."},
      {"type": "thinking", "thinking": "Let me plan the search..."},
      {"type": "tool_use", "name": "Bash", "id": "...", "input": {...}}
    ]
  }
}
```

**Fields:**
- `type`: Always "assistant"
- `timestamp`: ISO 8601 format
- `message.role`: Always "assistant"
- `message.content`: Array of content blocks (text, thinking, tool_use)

### Tool Result Messages

```json
{
  "type": "tool_result",
  "timestamp": "2025-11-12T20:00:02.000Z",
  "message": {
    "role": "user",
    "content": [
      {
        "type": "tool_result",
        "tool_use_id": "...",
        "content": "Tool output here"
      }
    ]
  }
}
```

**Fields:**
- `type`: "tool_result"
- `message.role`: "user" (tool results presented as user input)
- `message.content`: Array with tool_result block

## Content Block Types

### Text Block

Regular message text displayed to user.

```json
{
  "type": "text",
  "text": "Here's what I found..."
}
```

### Thinking Block

Internal reasoning (not visible to user in standard UI).

```json
{
  "type": "thinking",
  "thinking": "I need to consider the file structure before..."
}
```

**Note:** Thinking blocks are NOT currently indexed for keyword search in retrospecting scripts.

### Tool Use Block

Request to execute a tool.

```json
{
  "type": "tool_use",
  "id": "toolu_abc123",
  "name": "Read",
  "input": {
    "file_path": "/path/to/file.py"
  }
}
```

**Common tool names:**
- `Read` - Read file
- `Write` - Write file
- `Edit` - Edit file with old_string/new_string
- `Bash` - Execute bash command
- `Glob` - Find files by pattern
- `Grep` - Search file contents
- `Task` - Launch specialized agent
- `AskUserQuestion` - Ask clarifying questions
- `TodoWrite` - Update todo list

### Tool Result Block

Output from tool execution.

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_abc123",
  "content": "File contents here...",
  "is_error": false
}
```

## File Path Extraction Patterns

### Read Tool

```json
{
  "type": "tool_use",
  "name": "Read",
  "input": {
    "file_path": "/Users/user/project/file.py"
  }
}
```

**Extract:** `input.file_path`

### Edit Tool

```json
{
  "type": "tool_use",
  "name": "Edit",
  "input": {
    "file_path": "/Users/user/project/file.py",
    "old_string": "...",
    "new_string": "..."
  }
}
```

**Extract:** `input.file_path`

### Write Tool

```json
{
  "type": "tool_use",
  "name": "Write",
  "input": {
    "file_path": "/Users/user/project/new_file.py",
    "content": "..."
  }
}
```

**Extract:** `input.file_path`

### NotebookEdit Tool

```json
{
  "type": "tool_use",
  "name": "NotebookEdit",
  "input": {
    "notebook_path": "/Users/user/notebook.ipynb",
    "cell_id": "...",
    "new_source": "..."
  }
}
```

**Extract:** `input.notebook_path`

### Glob Tool

```json
{
  "type": "tool_use",
  "name": "Glob",
  "input": {
    "pattern": "**/*.py",
    "path": "/Users/user/project"
  }
}
```

**Extract:** `input.path` (if provided, otherwise null)

### Bash Tool (Not Extracted)

Bash commands are not parsed for file references because:
- File paths may be variables (`$OUTPUT_DIR/file.txt`)
- Commands may use pipes/redirects
- Paths may not exist yet (creating new files)
- Complex to parse accurately

**Future enhancement:** Could extract file args from common commands (cat, grep, etc.)

## Content Structure Variations

### Simple String Content

```json
{"content": "Just a simple message"}
```

**Extraction:** Use as-is

### Array Content

```json
{
  "content": [
    {"type": "text", "text": "Message part 1"},
    {"type": "text", "text": "Message part 2"}
  ]
}
```

**Extraction:** Concatenate all text blocks with spaces

### Mixed Content

```json
{
  "content": [
    {"type": "text", "text": "Let me think..."},
    {"type": "thinking", "thinking": "Planning the approach..."},
    {"type": "tool_use", "name": "Read", "input": {...}},
    {"type": "text", "text": "Here's what I found:"}
  ]
}
```

**Extraction:**
- Concatenate text blocks for message preview
- Extract thinking separately
- Extract tool_use blocks separately

## Message Ordering

Messages are ordered chronologically by timestamp. Typical flow:

1. **User message** - User request
2. **Assistant message** - Response with text + thinking + tool uses
3. **Tool result message** - One per tool use
4. **Assistant message** - Continues response with results
5. **Repeat** as conversation continues

## Special Cases

### Interrupted Conversations

```json
{"type": "user", "message": {"content": "[Request interrupted by user for tool use]"}}
```

User interrupted tool execution. Next message may be different request.

### System Reminders

```json
{"type": "user", "message": {"content": "<system-reminder>...</system-reminder>"}}
```

Automatically injected system messages (not actual user input).

### Local Commands

```json
{"type": "user", "message": {"content": "<local-command-stdout>...</local-command-stdout>"}}
```

Output from user's local shell (not requests to Claude).

## Parsing Best Practices

1. **Use try/except for JSON parsing** - Lines may be malformed
2. **Handle both string and array content** - Check type before processing
3. **Don't assume all fields exist** - Use `.get()` with defaults
4. **Skip system messages** - Check for `<system-reminder>` markers
5. **Extract thinking separately** - Different use case than text
6. **Track tool_use_id** - Links tool use to tool result

## Example Parsing Code

```python
import json

def extract_text_content(content):
    """Extract text from various content structures."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'text':
                texts.append(item.get('text', ''))
        return ' '.join(texts)
    return ''

with open('conversation.jsonl', 'r') as f:
    for line_num, line in enumerate(f, 1):
        try:
            data = json.loads(line)
            msg_type = data.get('type')
            message = data.get('message', {})
            content = message.get('content', '')

            if msg_type == 'user':
                text = extract_text_content(content)
                print(f"User: {text}")

            elif msg_type == 'assistant':
                text = extract_text_content(content)
                print(f"Assistant: {text}")

        except json.JSONDecodeError as e:
            print(f"Line {line_num}: Malformed JSON - {e}")
            continue
```
