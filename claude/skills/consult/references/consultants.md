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
| gemini-3-pro | Google's latest, good for large context |
| gemini-3-flash | Fast Google queries |
| gpt-5.2 | OpenAI general reasoning |
| gpt-5.2-high | Higher capability GPT |
| opus-4.5-thinking | Claude deep reasoning |
| opus-4.5 | Claude without extended thinking |
| sonnet-4.5 | Balanced Claude |
| composer-1 | Cursor's native model |

### Via codex
| Model | Use Case |
|-------|----------|
| gpt-5.2-codex | Default. Code-focused |
| gpt-5.2 | General reasoning |
| gpt-5.1-codex-max | Maximum capability |

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
