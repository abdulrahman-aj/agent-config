---
name: remember
description: Use when asked to persist a rule in project, shared, or OpenCode-only memory.
---

Choose the narrowest scope:

- Project-specific rules: the repository's `AGENTS.md`.
- Personal facts, preferences, and reusable engineering rules:
  `~/.config/opencode/AGENTS.md` (single hand-maintained file).

Read the destination first. Update related rules rather than adding duplicates;
keep wording short, actionable, and consistent with the file.

For global memory, edit the source in `~/dotfiles`, then run `make stow`
to deploy (or stow just the affected paths).

Report which file changed.
