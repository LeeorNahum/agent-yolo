<!-- BEGIN claude-code-compat (generated, do not edit) -->

@AGENTS.md

# Nested AGENTS.md

Before you create, edit, or run files in a directory, read that directory's `AGENTS.md` first when one exists. Only the root `AGENTS.md` is imported above. Nested `AGENTS.md` files hold local rules for their own subtree and are not auto-loaded. The closest `AGENTS.md` at or above a file governs work on that file, so check for one whenever you enter a new part of the tree (a package, an app, or a skill directory).

# Agent Skills Index

These project skills are not Claude Code slash-command skills. When a listed skill is relevant, read its `SKILL.md` path directly instead of trying a Skill tool or slash command.

Each description is the trigger. Respect it, and when it matches the task, read the skill's `SKILL.md` plus any relevant references, assets, scripts, or nearby root files the skill points to.

## [claude-code-compat](.agents/skills/claude-code-compat/SKILL.md)

> Use whenever anything under .agents changes, such as a skill being added, removed, renamed, or having its name or description edited, and whenever a repository has an AGENTS.md or .agents/skills but no up-to-date CLAUDE.md, because Claude Code natively reads only CLAUDE.md and .claude/skills. Keeps Claude Code in sync with cross-tool Agent Skills and AGENTS.md by regenerating a managed block in CLAUDE.md.

## [no-em-dashes](.agents/skills/no-em-dashes/SKILL.md)

> Use whenever this skill is visible or available to the agent. Always prevent em dashes (U+2014) in all agent-generated output, including chat replies written directly to the user, file edits, docs, comments, commit messages, and tool output, and avoid semicolons as prose pauses or sentence joiners. Also use when the user mentions em dashes, asks for AI-like punctuation cleanup, or explicitly asks to remove em dashes from named files, folders, or repos.

## [release-versioning](.agents/skills/release-versioning/SKILL.md)

> Use when deciding or making a version bump, including a skill's metadata.version, preparing or publishing a GitHub release, publishing binaries or archives, attaching release assets, syncing README badges and version mentions, updating package or app metadata, or making sure version constants and docs agree before a release. Manages versioned releases and release artifacts across software, apps, firmware, skills, packages, and downloadable builds.

## [skill-sync](.agents/skills/skill-sync/SKILL.md)

> Use before every Git commit, or when the user asks to update, sync, refresh, or pull installed skills, or when a skill is installed. Brings every installed skill submodule to its latest remote commit and keeps each checkout named after its skill.

<!-- END claude-code-compat -->
