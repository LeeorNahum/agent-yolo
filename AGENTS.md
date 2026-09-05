# agent-yolo

Tiny personal launcher scripts for running Codex/Claude Code with approval prompts skipped. See README.md for what each command does and how to use it.

`claudex` lives in its own separate repo, [github.com/LeeorNahum/claudex](https://github.com/LeeorNahum/claudex), not here. `claudexyolo` in this repo is a thin wrapper that assumes `claudex` is already installed and on PATH; it never vendors or duplicates any of claudex's own logic.

## Windows build and installation

- `wrappers.csv` owns the supported names, underlying commands, and permission flags. `build.ps1` compiles `launcher.cs` once per row, generating ignored artifacts in `dist/` and stamping `VERSION` into each executable.
- Keep the native Windows entry points. Forward the raw argument tail and the inherited directory directly to the native CLI, without `cmd /c`, argument reconstruction, or model/prompt defaults. Batch-only dependencies must produce an explicit error.
- Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\build.ps1`, then `python tests/windows.py`. Tests need Python 3 on Windows. Use `--unc \\server\share\directory` when a reachable UNC directory is available. No separate lint, typecheck, or package manager is configured. Compilation treats warnings as errors.
- `install.ps1` builds and copies into the established `.local\bin` and `.local\share\agent-yolo` layout, updates old batch shims, and registers user App Paths. Run `python tests/windows.py --installed` afterward to verify installed binaries and registered names with probe CLIs.
- For releases, update `VERSION`, run checks, commit, tag `v<VERSION>`, push, and create the GitHub release. Attach the three freshly built executables. Source archives contain the build/install workflow. Do not commit `dist/`.

## Standing rules

- Never use em dashes in new text (see `no-em-dashes` skill).
- Keep this repo small. A new launcher earns its own subfolder with matching `.cmd` (Windows) and `.sh` (macOS/Linux) variants; do not add a framework, installer wizard, or dependency beyond what a launcher genuinely needs.
- Run `skill-sync` before every commit (see that skill).
- Use `release-versioning` when bumping `VERSION` or tagging a release (see that skill).
