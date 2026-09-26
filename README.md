# agent-yolo

[![GitHub Release](https://img.shields.io/github/v/release/LeeorNahum/agent-yolo?sort=semver)](https://github.com/LeeorNahum/agent-yolo/releases/latest)

Tiny launchers for running Codex and Claude Code with their most permissive modes. Windows uses native `.exe` launchers. macOS/Linux use the `.sh` files.

These commands are unsafe. They disable approval prompts and sandbox or permission checks. Use them only on machines and directories you trust.

## Commands

| Wrapper | CLI | Added argument |
| --- | --- | --- |
| `codexyolo` | `codex` | `--dangerously-bypass-approvals-and-sandbox` |
| `claudeyolo` | `claude` | `--dangerously-skip-permissions` |
| `claudexyolo` | `claudex` | `--dangerously-skip-permissions` |

Each launcher adds its permission argument once and forwards all supplied arguments. It adds no model, effort setting, speed option, session name, or prompt. Explicit user arguments, including repeated flags, remain intact. [Claudex](https://github.com/LeeorNahum/claudex) is installed and maintained separately.

## Use

On Windows, run this in your checkout to build and install or update:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

The installer selects available native CLIs and updates previously installed wrappers. To select wrappers explicitly, run `& .\install.ps1 -Names codexyolo,claudeyolo,claudexyolo` in PowerShell. It uses the C# compiler included with Windows .NET Framework, with no SDK or runtime package to install.

Type `codexyolo`, `claudeyolo`, or `claudexyolo` into Explorer's address bar to launch in the displayed filesystem folder. The same names work in cmd and PowerShell. Each child inherits the exact working directory passed to the launcher, including UNC paths. Virtual Explorer locations that have no filesystem directory are outside this contract.

Windows requires `codex.exe`, `claude.exe`, or `claudex.exe` on an absolute PATH entry. The first matching executable is used. Relative PATH entries and batch/PowerShell CLI shims are skipped. For `claudexyolo`, install [claudex v2.2.0 or newer](https://github.com/LeeorNahum/claudex/releases/latest), which supplies the native launcher. Claudex owns the model default and proxy setup. Agent-yolo adds only the permission flag.

The native launchers forward the raw Windows argument tail without a shell or conversion to prompt text. Windows supplies a command-line string, and the target CLI owns its parsing. Normal shell parsing still happens before a launcher runs: quote cmd metacharacters and account for percent/delayed expansion. Windows PowerShell 5.1 has legacy empty-argument and embedded-quote limitations. PowerShell 7's standard native argument mode supports those values. Arguments cannot contain NUL or exceed the Windows process command-line limit, including the launcher-added flag.

Executables are copied to `%USERPROFILE%\.local\bin` and mirrored under `%USERPROFILE%\.local\share\agent-yolo`. The installer adds the bin directory to user PATH and registers each name in the user's App Paths so Explorer resolves it immediately. You can rerun the installer while launcher sessions are open. It renames each running executable aside and deletes that copy on a later install, after its session ends. If another program has an executable open, installation stops with an error naming the file. Existing `.cmd` shims are updated in both locations. Explicit `.cmd` invocation remains available under cmd's more limited argument and directory contract. Source `.cmd` files use the checkout's `dist` executable after a build. If a terminal predates the PATH update, open a new terminal.

On macOS/Linux, put the desired `.sh` file on PATH under its command name and make it executable. The corresponding CLI must already be installed.

## Set up with an AI coding agent

Paste this into Claude Code, Codex, or any coding agent:

> Clone https://github.com/LeeorNahum/agent-yolo and read its README.md. On Windows, run install.ps1 and report any missing native CLI dependency. On macOS/Linux, check which of codex, claude, and claudex are installed, then put only the matching shell launchers on PATH unless I request others. Verify the installed commands and summarize what you did.
