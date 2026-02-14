# Consultant Reference

## Contents
- [CLI Tools](#cli-tools)
- [Model Selection](#model-selection)
- [Multiple Consultants](#multiple-consultants)

## CLI Tools

### cursor-agent (default)
Widest model selection. Run `cursor-agent models` for current list.

```bash
cursor-agent --model {model} --print --output-format text "{query}"
```

### codex
OpenAI's code-focused CLI.

```bash
codex exec -m {model} "{query}"
```

### claude
Anthropic's official CLI.

```bash
claude -m {model} -p "{query}"
```

### opencode
Run `opencode models` for current list.

```bash
opencode run -m {model} "{query}"
```

## Model Selection

### Via cursor-agent
| Model | Use Case |
|-------|----------|
| auto | Let Cursor choose |
| opus-4.6-thinking | Claude deep reasoning (default) |
| opus-4.6 | Claude 4.6 without thinking |
| opus-4.5-thinking | Claude 4.5 deep reasoning |
| sonnet-4.5-thinking | Claude balanced with thinking |
| sonnet-4.5 | Fast balanced Claude |
| gpt-5.3-codex | Latest OpenAI code-focused |
| gpt-5.2 | OpenAI general reasoning |
| gpt-5.2-high | Higher capability GPT |
| gemini-3-pro | Google's latest, good for large context |
| gemini-3-flash | Fast Google queries |
| composer-1.5 | Cursor's latest native model |

### Via codex
| Model | Use Case |
|-------|----------|
| gpt-5.1-codex-max | Deep reasoning flagship |
| gpt-5.1-codex | Default. Code-focused |
| gpt-5.1-codex-mini | Cheaper/faster |
| gpt-5.1 | General reasoning |

### Via claude
| Model | Use Case |
|-------|----------|
| sonnet | Default. Balanced |
| opus | Maximum capability |

### Via opencode
Run `opencode models` for current list.

## Multiple Consultants

When user asks for multiple perspectives:
1. Launch parallel Task calls
2. Each task consults one model
3. Synthesize findings in response

Example: "Consult gemini and codex on this design"
→ Two parallel tasks, then summarize both perspectives
