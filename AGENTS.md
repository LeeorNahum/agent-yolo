# agent-yolo

Tiny personal launcher scripts for running Codex/Claude Code with approval prompts skipped. See README.md for what each command does and how to use it.

`claudex` lives in its own separate repo, [github.com/LeeorNahum/claudex](https://github.com/LeeorNahum/claudex), not here. `claudexyolo` in this repo is a thin wrapper that assumes `claudex` is already installed and on PATH; it never vendors or duplicates any of claudex's own logic.

## Standing rules

- Never use em dashes in new text (see `no-em-dashes` skill).
- Keep this repo small. A new launcher earns its own subfolder with matching `.cmd` (Windows) and `.sh` (macOS/Linux) variants; do not add a framework, installer wizard, or dependency beyond what a launcher genuinely needs.
- Run `skill-sync` before every commit (see that skill).
