---
name: remember
description: Use when asked to persist a project rule or a personal preference shared across coding harnesses.
---

Choose the narrowest scope:

- Project-specific rules: the repository's `AGENTS.md`.
- Personal facts, preferences, and reusable engineering rules:
  `~/.agents/AGENTS.md` (single hand-maintained file linked into each harness).

Read the destination first. Update related rules rather than adding duplicates;
keep wording short, actionable, and consistent with the file.

For global memory, edit `AGENTS.md` in the `~/agent-config` checkout (or the
checkout resolved from the deployed symlink). Installed harness paths point at
this file, so Markdown edits need no `make` or copying. A running harness may
need a new session to reload global instructions.

Report which file changed.
