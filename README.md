# claude-code-agents

**Agent definitions, skills, and conventions for my Claude Code workflow.**

## Quick start

1. **Install / link configs**
   - This repo is designed to be symlinked into `{$HOME}/.claude/` (dotfiles style).
   - Use the `scripts/install.sh` script to create the symlinks.


## Repository layout

```
.
├── claude/
│   ├── agents/                    # agent definitions (markdown)
│   │   └── README.md              # capabilities matrix
│   ├── skills/                    # reusable skills with resources
│   │   ├── mermaid-diagrams/      # diagram creation skill
│   │   ├── graphviz-diagrams/     # architecture diagram skill
│   │   ├── obsidian-vault/        # knowledge management skill
│   │   └── ...
│   ├── hooks/                     # Claude Code hooks
│   └── settings.json              # Claude global settings
└── docs/                          # additional documentation
```

## License

MIT (unless stated otherwise in subfolders).
