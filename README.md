# agent-yolo

Tiny launchers for running Codex and Claude Code with their most permissive modes. Windows uses the `.cmd` files, macOS/Linux use the `.sh` files.

These commands are unsafe. They disable approval prompts and sandbox or permission checks. Use them only on machines and directories you trust.

## Commands

- `codexyolo/codexyolo.cmd` (or `.sh`) runs `codex --dangerously-bypass-approvals-and-sandbox`
- `claudeyolo/claudeyolo.cmd` (or `.sh`) runs `claude --dangerously-skip-permissions`
- `claudexyolo/claudexyolo.cmd` (or `.sh`) runs `claudex --dangerously-skip-permissions`, requires [claudex](https://github.com/LeeorNahum/claudex) to already be set up and on your PATH

## Use

Pick the launcher(s) you want, put the file somewhere on your PATH (or put it in a folder and add that folder to PATH). Requires Codex CLI and Claude Code to already be installed. `claudexyolo` additionally requires [claudex](https://github.com/LeeorNahum/claudex) set up separately first.

## Set up with an AI coding agent

Paste this into Claude Code, Codex, or any coding agent:

> Clone https://github.com/LeeorNahum/agent-yolo, read its README.md, then set up whichever launcher(s) I ask for (all of them if I don't say). Use the `.cmd` files on Windows, the `.sh` files on macOS/Linux. Put the launcher(s) on my PATH. Verify each one actually works, then summarize what you did.
