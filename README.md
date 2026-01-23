# claude-code-config

**Personal Claude Code configuration: agents, skills, hooks, and settings.**

## Quick start

1. **Install / link configs**
   - This repo is designed to be symlinked into `{$HOME}/.claude/` (dotfiles style).
   - Use the `scripts/install.sh` script to create the symlinks.


## Repository layout

```
.
├── claude/
│   ├── agents/        # agent definitions (markdown)
│   ├── hooks/         # Claude Code hooks
│   ├── skills/        # reusable skills
│   ├── CLAUDE.md      # project instructions
│   └── settings.json  # global settings
├── scripts/           # install/uninstall helpers
└── README.md
```

## License

MIT (unless stated otherwise in subfolders).
