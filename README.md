# claude-code-agents

**Agent definitions, skills, and conventions for a multi-agent Claude Code workflow.**

This repo contains agent specs (markdown), reusable skills, and operational conventions that extend Claude Code's capabilities. Agents are specialized sub-agents that can be spawned via the Task tool, while skills provide reusable workflows and resources that can be invoked directly.


## Quick start

1. **Install / link configs**
   - This repo is designed to be symlinked into `~/.claude/` (dotfiles style).
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
│   ├── commands/                  # slash commands
│   ├── hooks/                     # Claude Code hooks
│   └── settings.json              # Claude global settings
├── docs/                          # additional documentation
└── CLAUDE.md                      # core principles and usage guide
```

## License

MIT (unless stated otherwise in subfolders).
